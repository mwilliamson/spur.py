import subprocess
import os
import os.path
import shutil
import contextlib
import uuid
import time

import paramiko

from spur.tempdir import create_temporary_dir
from spur.files import FileOperations
import spur.results

class SshShell(object):
    def __init__(self, hostname, username, password=None, port=22, private_key_file=None):
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._private_key_file = private_key_file
        self._client = None

    def run(self, *args, **kwargs):
        allow_error = kwargs.pop("allow_error", False)
        command_in_cwd = self._generate_run_command(*args, **kwargs)
        
        with self._connect_ssh() as client:
            stdin, stdout, stderr = client.exec_command(command_in_cwd)
            output = []
            for line in stdout:
                output.append(line)
            
            stderr_output = []
            for line in stderr:
                stderr_output.append(line)
                
            return_code = int(output[-1])
            # Strip the extra newline and line containing the return code
            output_as_str = "".join(output[:-1])[:-1]
            stderr_output_as_str = "".join(stderr_output)
            return spur.results.result(
                return_code,
                output_as_str,
                stderr_output_as_str,
                allow_error=allow_error
            )
    
    def spawn(self, *args, **kwargs):
        command_in_cwd = self._generate_run_command(*args, **kwargs)
        print "RUN: ", command_in_cwd
        with self._connect_ssh() as client:
            client.exec_command(command_in_cwd)
    
    @contextlib.contextmanager
    def temporary_dir(self):
        result = self.run(["mktemp", "--directory"])
        temp_dir = result.output.strip()
        try:
            yield temp_dir
        finally:
            self.run(["rm", "-rf", temp_dir])
    
    def _generate_run_command(self, command_args, cwd="/", update_env={}, new_process_group=False):
        command = " ".join(map(escape_sh, command_args))
        
        update_env_commands = " ".join([
            "export {0}={1};".format(key, escape_sh(value))
            for key, value in update_env.iteritems()
        ])
        
        if new_process_group:
            command = "setsid {0}".format(command)
        
        return "cd {0}; {1} {2}; echo '\n'$?".format(cwd, update_env_commands, command)
        
    
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
                
    def open(self, name, mode):
        with self._connect_ssh() as client:
            sftp = client.open_sftp()
            return SftpFile(sftp, sftp.open(name, mode))
                
    @property
    def files(self):
        return FileOperations(self)
    
    @contextlib.contextmanager
    def _connect_ssh(self):
        if self._client is None:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            client.connect(
                hostname=self._hostname,
                port=self._port,
                username=self._username,
                password=self._password,
                key_filename=self._private_key_file
            )
            self._client = client
        yield self._client
    
    @contextlib.contextmanager
    def _connect_sftp(self):
        with self._connect_ssh() as client:
            sftp = client.open_sftp()
            try:
                yield sftp
            finally:
                sftp.close()


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
            
    def __exit__(self, *args):
        self.close()
        

def escape_sh(value):
    return "'" + value.replace("'", "'\\''") + "'"
