import functools

from nose.tools import istest, assert_equal

from spur import LocalShell

def test(func):
    @functools.wraps(func)
    def run_test():
        for shell in _create_shells():
            yield func, shell
            
    def _create_shells():
        return [
            LocalShell()
        ]
        
    return istest(run_test)

@test
def output_of_run_is_stored(shell):
    result = shell.run(["echo", "hello"])
    assert_equal("hello\n", result.output)

@test
def cwd_of_run_can_be_set(shell):
    result = shell.run(["pwd"], cwd="/")
    assert_equal("/\n", result.output)

@test
def environment_variables_can_be_added_for_run(shell):
    result = shell.run(["sh", "-c", "echo $NAME"], update_env={"NAME": "Bob"})
    assert_equal("Bob\n", result.output)
