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
    def __init__(self, file_in, file_out):
        self._file_in = file_in
        self._file_out = file_out
        self._output = ""
        
        self._thread = threading.Thread(target=self._capture_output)
        self._thread.daemon = True
        self._thread.start()

    def wait(self):
        self._thread.join()
        return self._output
    
    def _capture_output(self):
        if self._file_out is None:
            try:
                self._output = self._file_in.read()
            except IOError:
                # TODO: is there a more elegant fix?
                # Attempting to read from a pty master that has received nothing
                # seems to raise an IOError when reading
                # See: http://bugs.python.org/issue5380
                self._output = b""
        else:
            output_buffer = []
            while True:
                output = self._file_in.read(1)
                if output:
                    self._file_out.write(output)
                    output_buffer.append(output)
                else:
                    self._output = b"".join(output_buffer)
                    return
