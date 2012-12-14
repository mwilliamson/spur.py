class RunProcessError(RuntimeError):
    def __init__(self, return_code, output, stderr_output):
        message = "return code: {0}\noutput: {1}\nstderr output: {2}".format(
            return_code, output, stderr_output)
        super(type(self), self).__init__(message)
        self.return_code = return_code
        self.output = output
        self.stderr_output = stderr_output
