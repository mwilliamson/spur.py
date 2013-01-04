import threading


class IoHandler(object):
    def __init__(self, in_out_pairs):
        self._handlers = [
            OutputHandler(file_in, file_out)
            for file_in, file_out
            in in_out_pairs
        ]
        
    def wait(self):
        return [handler.wait() for handler in self._handlers]
    

class OutputHandler(object):
    def __init__(self, stdout_in, stdout_out):
        self._stdout_in = stdout_in
        self._stdout_out = stdout_out
        self._output = []
        
        if stdout_out:
            self._stdout_thread = threading.Thread(target=self._capture_stdout)
            self._stdout_thread.daemon = True
            self._stdout_thread.start()
        else:
            self._stdout_thread = None

    def wait(self):
        if self._stdout_thread:
            self._stdout_thread.join()
        return "".join(self._output)
    
    def _capture_stdout(self):
        while True:
            output = self._stdout_in.read(1)
            if output:
                self._stdout_out.write(output)
                self._output.append(output)
            else:
                return
