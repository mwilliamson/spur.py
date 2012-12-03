from nose.tools import istest, assert_equal

from spur import LocalShell

shell = LocalShell()

@istest
def output_of_run_is_stored():
    result = shell.run(["echo", "hello"])
    assert_equal("hello\n", result.output)
