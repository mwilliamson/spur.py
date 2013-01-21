import subprocess
import os
import os.path
import shutil
import contextlib
import uuid
import time
import re
import socket

import paramiko

from spur.tempdir import create_temporary_dir
from spur.files import FileOperations
import spur.results
from .io import IoHandler


_ONE_MINUTE = 60


class ConnectionError(Exception):
    pass


class SshShell(object):
    def __init__(self, hostname, username, password=None, port=22, private_key_file=None, connect_timeout=None):
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._private_key_file = private_key_file
        self._client = None
        self._connect_timeout = connect_timeout if not None else _ONE_MINUTE
        self._closed = False

    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        self._closed = True
        if self._client is not None:
            self._client.close()

    def run(self, *args, **kwargs):
        return self.spawn(*args, **kwargs).wait_for_result()
    
    def spawn(self, *args, **kwargs):
        stdout = kwargs.pop("stdout", None)
        stderr = kwargs.pop("stderr", None)
        allow_error = kwargs.pop("allow_error", False)
        store_pid = kwargs.pop("store_pid", False)
        command_in_cwd = self._generate_run_command(*args, store_pid=store_pid, **kwargs)
        channel = self._get_ssh_transport().open_session()
        channel.exec_command(command_in_cwd)
        
        process_stdout = channel.makefile('rb')
        if store_pid:
            pid = int(process_stdout.readline().strip())
            
        process = SshProcess(
            channel,
            allow_error=allow_error,
            process_stdout=process_stdout,
            stdout=stdout,
            stderr=stderr,
            shell=self,
        )
        if store_pid:
            process.pid = pid
        
        return process
    
    @contextlib.contextmanager
    def temporary_dir(self):
        result = self.run(["mktemp", "--directory"])
        temp_dir = result.output.strip()
        try:
            yield temp_dir
        finally:
            self.run(["rm", "-rf", temp_dir])
    
    def _generate_run_command(self, command_args, store_pid,
            cwd=None, update_env={}, new_process_group=False):
        commands = []

        if store_pid:
            commands.append("echo $$")

        if cwd is not None:
            commands.append("cd {0}".format(escape_sh(cwd)))
        
        update_env_commands = [
            "export {0}={1}".format(key, escape_sh(value))
            for key, value in update_env.iteritems()
        ]
        commands += update_env_commands
        
        command = " ".join(map(escape_sh, command_args))
        command = "exec {0}".format(command)
        if new_process_group:
            command = "setsid {0}".format(command)
            
        commands.append(command)
        
        return "; ".join(commands)
        
    
    def upload_dir(self, local_dir, remote_dir, ignore):
        with create_temporary_dir() as temp_dir:
            content_tarball_path = os.path.join(temp_dir, "content.tar.gz")
            content_path = os.path.join(temp_dir, "content")
            shutil.copytree(local_dir, content_path, ignore=shutil.ignore_patterns(*ignore))
            subprocess.check_call(
                ["tar", "czf", content_tarball_path, "content"],
                cwd=temp_dir
            )
            with self._connect_sftp() as sftp:
                remote_tarball_path = "/tmp/{0}.tar.gz".format(uuid.uuid4())
                sftp.put(content_tarball_path, remote_tarball_path)
                self.run(["mkdir", "-p", remote_dir])
                self.run([
                    "tar", "xzf", remote_tarball_path,
                    "--strip-components", "1", "--directory", remote_dir
                ])
                    
                sftp.remove(remote_tarball_path)
                
    def open(self, name, mode="r"):
        sftp = self._open_sftp_client()
        return SftpFile(sftp, sftp.open(name, mode))
                
    @property
    def files(self):
        return FileOperations(self)
    
    def _get_ssh_transport(self):
        try:
            return self._connect_ssh().get_transport()
        except (socket.error, paramiko.SSHException, EOFError) as error:
            raise ConnectionError(
                "Error creating SSH connection\n" +
                "Original error: {0}".format(error)
            )
    
    def _connect_ssh(self):
        if self._client is None:
            if self._closed:
                raise RuntimeError("Shell is closed")
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            client.connect(
                hostname=self._hostname,
                port=self._port,
                username=self._username,
                password=self._password,
                key_filename=self._private_key_file,
                timeout=self._connect_timeout
            )
            self._client = client
        return self._client
    
    @contextlib.contextmanager
    def _connect_sftp(self):
        sftp = self._open_sftp_client()
        try:
            yield sftp
        finally:
            sftp.close()
            
    def _open_sftp_client(self):
        return self._get_ssh_transport().open_sftp_client()


class SftpFile(object):
    def __init__(self, sftp, file):
        self._sftp = sftp
        self._file = file
    
    def __getattr__(self, key):
        if hasattr(self._file, key):
            return getattr(self._file, key)
        raise AttributeError
        
    def close(self):
        try:
            self._file.close()
        finally:
            self._sftp.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
        

def escape_sh(value):
    return "'" + value.replace("'", "'\\''") + "'"


class SshProcess(object):
    def __init__(self, channel, allow_error, process_stdout, stdout, stderr, shell):
        self._channel = channel
        self._allow_error = allow_error
        self._stdin = channel.makefile('wb')
        self._stdout = process_stdout
        self._stderr = channel.makefile_stderr('rb')
        self._shell = shell
        self._result = None
        
        self._io = IoHandler([
            (self._stdout, stdout),
            (self._stderr, stderr),
        ], lambda: (self._stdout.read(), self._stderr.read()))
        
    def is_running(self):
        return not self._channel.exit_status_ready()
        
    def stdin_write(self, value):
        self._channel.sendall(value)
        
    def send_signal(self, signal):
        self._shell.run(["kill", "-{0}".format(signal), str(self.pid)])
        
    def wait_for_result(self):
        if self._result is None:
            self._result = self._generate_result()
            
        return self._result
        
    def _generate_result(self):
        output, stderr_output = self._io.wait()
        return_code = self._channel.recv_exit_status()
        
        return spur.results.result(
            return_code,
            self._allow_error,
            output,
            stderr_output
        )
