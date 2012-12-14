class RunProcessError(RuntimeError):
    def __init__(self, return_code, output, stderr_output):
        super(type(self), self).__init__("")
        self.return_code = return_code
        self.output = output
        self.stderr_output = stderr_output
