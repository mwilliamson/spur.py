import spur

from nose.tools import istest

from .process_test_set import ProcessTestSet
from .open_test_set import OpenTestSet


class LocalTestMixin(object):
    def create_shell(self):
        return spur.LocalShell()
    

@istest
class LocalOpenTests(OpenTestSet, LocalTestMixin):
    pass


@istest
class LocalProcessTests(ProcessTestSet, LocalTestMixin):
    pass
