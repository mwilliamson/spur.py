import threading


class IoHandler(object):
    def __init__(self, in_out_pairs, read_all):
        self._handlers = [
            OutputHandler(file_in, file_out)
            for file_in, file_out
            in in_out_pairs
        ]
        self._read_all = read_all
        
    def wait(self):
        handler_result = [handler.wait() for handler in self._handlers]
        read_all_result = self._read_all()
        return [
            handler_output or read_all_output
            for handler_output, read_all_output
            in zip(handler_result, read_all_result)
        ]
    

class OutputHandler(object):
    def __init__(self, file_in, file_out):
        self._file_in = file_in
        self._file_out = file_out
        self._output = []
        
        if file_out:
            self._thread = threading.Thread(target=self._capture_output)
            self._thread.daemon = True
            self._thread.start()
        else:
            self._thread = None

    def wait(self):
        if self._thread:
            self._thread.join()
        return "".join(self._output)
    
    def _capture_output (self):
        while True:
            output = self._file_in.read(1)
            if output:
                self._file_out.write(output)
                self._output.append(output)
            else:
                return
