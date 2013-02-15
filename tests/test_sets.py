import functools
import contextlib

from nose.tools import istest, nottest


class TestSetBuilder(object):
    def __init__(self):
        self._test_funcs = []
    
    @nottest
    def add_test(self, func):
        self._test_funcs.append(func)
        
    def create(self, name, run_test):
        @istest
        class Tests(object):
            pass
            
        for test_func in self._test_funcs:
            self._add_test_func(Tests, test_func, run_test)
        
        Tests.__name__ = name
        return Tests
        
    def _add_test_func(self, cls, test_func, run_test):
        @functools.wraps(test_func)
        @istest
        def test_method(self):
            return run_test(test_func)
        
        setattr(cls, test_func.__name__, test_method)
