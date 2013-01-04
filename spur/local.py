import os
import subprocess
import shutil

from spur.tempdir import create_temporary_dir
from spur.files import FileOperations
import spur.results
from .io import IoHandler


class LocalShell(object):
    def upload_dir(self, source, dest, ignore=None):
        shutil.copytree(source, dest, ignore=shutil.ignore_patterns(*ignore))

    def upload_file(self, source, dest):
        shutil.copyfile(source, dest)
    
    def open(self, name, mode="r"):
        return open(name, mode)
    
    def write_file(self, remote_path, contents):
        subprocess.check_call(["mkdir", "-p", os.path.dirname(remote_path)])
        open(remote_path, "w").write(contents)

    def spawn(self, *args, **kwargs):
        stdout = kwargs.pop("stdout", None)
        stderr = kwargs.pop("stderr", None)
        allow_error = kwargs.pop("allow_error", False)
        process = subprocess.Popen(**self._subprocess_args(*args, **kwargs))
        return LocalProcess(
            process,
            allow_error=allow_error,
            stdout=stdout,
            stderr=stderr
        )
        
    def run(self, *args, **kwargs):
        return self.spawn(*args, **kwargs).wait_for_result()
        
    def temporary_dir(self):
        return create_temporary_dir()
    
    @property
    def files(self):
        return FileOperations(self)
    
    def _subprocess_args(self, command, cwd=None, update_env=None, new_process_group=False):
        kwargs = {
            "args": command,
            "cwd": cwd,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "stdin": subprocess.PIPE
        }
        if update_env is not None:
            new_env = os.environ.copy()
            new_env.update(update_env)
            kwargs["env"] = new_env
        if new_process_group:
            kwargs["preexec_fn"] = os.setpgrp
        return kwargs

class LocalProcess(object):
    def __init__(self, subprocess, allow_error, stdout, stderr):
        self._subprocess = subprocess
        self._allow_error = allow_error
        self._result = None
            
        self._io = IoHandler([
            (subprocess.stdout, stdout),
            (subprocess.stderr, stderr),
        ], lambda: self._subprocess.communicate())
        
    def is_running(self):
        return self._subprocess.poll() is None
        
    def stdin_write(self, value):
        self._subprocess.stdin.write(value)
        
    def wait_for_result(self):
        if self._result is None:
            self._result = self._generate_result()
            
        return self._result
    
    def _generate_result(self):
        output, stderr_output = self._io.wait()
        return_code = self._subprocess.poll()
        
        return spur.results.result(
            return_code,
            self._allow_error,
            output,
            stderr_output
        )

