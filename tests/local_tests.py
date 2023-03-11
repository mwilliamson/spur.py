import spur

from .process_test_set import ProcessTestSet
from .open_test_set import OpenTestSet


class LocalTestMixin(object):
    def create_shell(self):
        return spur.LocalShell()


class LocalOpenTests(OpenTestSet, LocalTestMixin):
    pass


class LocalProcessTests(ProcessTestSet, LocalTestMixin):
    pass
