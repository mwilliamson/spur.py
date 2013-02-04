class NoSuchCommandError(OSError):
    def __init__(self, command):
        if "/" in command:
            message = "No such command: {0}".format(command)
        else:
            message = "Command not found: {0}. Check that {0} is installed and on $PATH".format(command)
        super(type(self), self).__init__(message)
        self.command = command
