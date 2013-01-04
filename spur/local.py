import os
import subprocess
import shutil
import threading

from spur.tempdir import create_temporary_dir
from spur.files import FileOperations
import spur.results
    
class LocalShell(object):
    def upload_dir(self, source, dest, ignore=None):
        shutil.copytree(source, dest, ignore=shutil.ignore_patterns(*ignore))

    def upload_file(self, source, dest):
        shutil.copyfile(source, dest)
    
    def open(self, name, mode):
        return open(name, mode)
    
    def write_file(self, remote_path, contents):
        subprocess.check_call(["mkdir", "-p", os.path.dirname(remote_path)])
        open(remote_path, "w").write(contents)

    def spawn(self, *args, **kwargs):
        stdout = kwargs.pop("stdout", None)
        process = subprocess.Popen(**self._subprocess_args(*args, **kwargs))
        return LocalProcess(process, stdout=stdout)
        
    def run(self, *args, **kwargs):
        allow_error = kwargs.pop("allow_error", False)
        process = self.spawn(*args, **kwargs)
        return spur.results.result(
            process,
            allow_error=allow_error
        )
        
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
    def __init__(self, subprocess, stdout):
        self._subprocess = subprocess
        self._stdout = stdout
        self._result = None
        self._output = []
        
        if stdout:
            self._stdout_thread = threading.Thread(target=self._capture_stdout)
            self._stdout_thread.daemon = True
            self._stdout_thread.start()
        else:
            self._stdout_thread = None
        
    def is_running(self):
        return self._subprocess.poll() is None
        
    def stdin_write(self, value):
        self._subprocess.stdin.write(value)
        
    def wait_for_result(self):
        if self._result is None:
            self._result = self._generate_result()
            
        return self._result
    
    def _capture_stdout(self):
        while True:
            output = self._subprocess.stdout.read(1)
            if output:
                self._stdout.write(output)
                self._output.append(output)
            else:
                return
    
    def _generate_result(self):
        if self._stdout_thread:
            self._stdout_thread.join()
        
        communicate_output, stderr = self._subprocess.communicate()
        if self._output:
            output = "".join(self._output)
        else:
            output = communicate_output
        
        return_code = self._subprocess.poll()
        return spur.results.ExecutionResult(
            return_code,
            output,
            stderr
        )
