__author__ = 'nmckinney'

_COMMAND_SUCCESSFUL = 0


class EnvironmentalVariables:
    def __init__(self, shell):
        self._shell = shell
        self._env = {}

    def _getEnvVariables(self):
        result = self._shell.run(['env'], allow_error=True)
        if result.return_code != _COMMAND_SUCCESSFUL:
            raise Exception('Unable to build environmental variable list.')
        for val in result.output.split('\n'):
            if val is not '':
                self._env[val.split('=')[0]] = val.split('=')[1]

    @property
    def env(self):
        if len(self._env) == 0:
            self._getEnvVariables()
            return self._env

    def setenv(self, name, value):
        result = self._shell.run(['export', str(name), '=', str(value)], allow_error=True)
        if result.return_code != _COMMAND_SUCCESSFUL:
            raise Exception('Unable to set environmental variable.')
