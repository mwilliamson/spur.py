class RunProcessError(RuntimeError):
    def __init__(self, return_code, stdout, stderr):
        super(type(self), self).__init__("")
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
