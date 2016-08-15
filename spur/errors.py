class NoSuchCommandError(OSError):
    def __init__(self, command):
        if "/" in command:
            message = "No such command: {0}".format(command)
        else:
            message = "Command not found: {0}. Check that {0} is installed and on $PATH".format(command)
        super(type(self), self).__init__(message)
        self.command = command


class CommandInitializationError(Exception):
    def __init__(self, line):
        super(type(self), self).__init__(
"""Error while initializing command. The most likely cause is an unsupported shell. Try using a minimal shell type when calling 'spawn' or 'run'.
(Failed to parse line '{0}' as integer)""".format(line)
        )


class NoSuchDirectoryError(OSError):

    def __init__(self, directory):
        message = "No such directory: {0}".format(directory)
        super(type(self), self).__init__(message)
        self.directory = directory
