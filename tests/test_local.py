import spur

from .test_process_set import ProcessTestSet
from .test_open_set import OpenTestSet


class LocalTestMixin(object):
    def create_shell(self):
        return spur.LocalShell()



class TestLocalOpenTests(OpenTestSet, LocalTestMixin):
    pass



class TestLocalProcessTests(ProcessTestSet, LocalTestMixin):
    # Locally these produce FileNotFound Exceptions
    test_spawning_non_existent_command_raises_specific_no_such_command_exception = None
    test_spawning_command_that_uses_path_env_variable_asks_if_command_is_installed = None
    test_using_non_existent_command_and_correct_cwd_raises_no_such_command_exception = None
