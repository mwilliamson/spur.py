def result(return_code, output, stderr_output, allow_error=False):
    result = ExecutionResult(return_code, output, stderr_output)
    if allow_error or return_code == 0:
        return result
    else:
        raise result.to_error()


class RunProcessError(RuntimeError):
    def __init__(self, return_code, output, stderr_output):
        message = "return code: {0}\noutput: {1}\nstderr output: {2}".format(
            return_code, output, stderr_output)
        super(type(self), self).__init__(message)
        self.return_code = return_code
        self.output = output
        self.stderr_output = stderr_output


class ExecutionResult(object):
    def __init__(self, return_code, output, stderr_output):
        self.return_code = return_code
        self.output = output
        self.stderr_output = stderr_output
        
    def to_error(self):
        return RunProcessError(
            self.return_code,
            self.output, 
            self.stderr_output
        )
