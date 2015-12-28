import threading
import os


class IoHandler(object):
    def __init__(self, channels, encoding):
        self._handlers = [
            _output_handler(channel, encoding)
            for channel in channels
        ]
        
    def wait(self):
        return [handler.wait() for handler in self._handlers]


class Channel(object):
    def __init__(self, file_in, file_out, is_pty=False):
        self.file_in = file_in
        self.file_out = file_out
        self.is_pty = is_pty


def _output_handler(channel, encoding):
    bytes_handler = _bytes_output_handler(channel)
    if encoding is None:
        return bytes_handler
    else:
        return _EncodedOutputHandler(bytes_handler, encoding)


class _EncodedOutputHandler(object):
    def __init__(self, bytes_handler, encoding):
        self._bytes_handler = bytes_handler
        self._encoding = encoding
    
    def wait(self):
        return self._bytes_handler.wait().decode(self._encoding)


def _bytes_output_handler(channel):
    if channel.file_out is None and not channel.is_pty:
        return _ReadOutputAtEnd(channel.file_in)
    else:
        return _ContinuousReader(channel)


class _ReadOutputAtEnd(object):
    def __init__(self, file_in):
        self._file_in = file_in
    
    def wait(self):
        return self._file_in.read()
    

class _ContinuousReader(object):
    def __init__(self, channel):
        self._file_in = channel.file_in
        self._file_out = channel.file_out
        self._is_pty = channel.is_pty
        self._output = b""
        
        self._thread = threading.Thread(target=self._capture_output)
        self._thread.daemon = True
        self._thread.start()

    def wait(self):
        self._thread.join()
        return self._output
    
    def _capture_output(self):
        output_buffer = []
        while True:
            try:
                output = self._file_in.read(1)
            except IOError:
                if self._is_pty:
                    output = b""
                else:
                    raise
            if output:
                if self._file_out is not None:
                    self._file_out.write(output)
                output_buffer.append(output)
            else:
                self._output = b"".join(output_buffer)
                return
