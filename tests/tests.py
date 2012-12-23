import functools
import os

from nose.tools import istest, assert_equal, assert_raises, assert_true

import spur

def test(func):
    @functools.wraps(func)
    def run_test():
        for shell in _create_shells():
            yield func, shell
            
    def _create_shells():
        return [
            spur.LocalShell(),
            _create_ssh_shell()
        ]
        
    def _create_ssh_shell():
        port_var = os.environ.get("TEST_SSH_PORT")
        port = int(port_var) if port_var is not None else None
        return spur.SshShell(
            hostname=os.environ.get("TEST_SSH_HOSTNAME", "127.0.0.1"),
            username=os.environ["TEST_SSH_USERNAME"],
            password=os.environ["TEST_SSH_PASSWORD"],
            port=port
        )
        
    return istest(run_test)

@test
def output_of_run_is_stored(shell):
    result = shell.run(["echo", "hello"])
    assert_equal("hello\n", result.output)
    
@test
def output_is_not_truncated_when_not_ending_in_a_newline(shell):
    result = shell.run(["echo", "-n", "hello"])
    assert_equal("hello", result.output)
    
@test
def trailing_newlines_are_not_stripped_from_run_output(shell):
    result = shell.run(["echo", "\n\n"])
    assert_equal("\n\n\n", result.output)

@test
def stderr_output_of_run_is_stored(shell):
    result = shell.run(["sh", "-c", "echo hello 1>&2"])
    assert_equal("hello\n", result.stderr_output)
    
@test
def cwd_of_run_can_be_set(shell):
    result = shell.run(["pwd"], cwd="/")
    assert_equal("/\n", result.output)

@test
def environment_variables_can_be_added_for_run(shell):
    result = shell.run(["sh", "-c", "echo $NAME"], update_env={"NAME": "Bob"})
    assert_equal("Bob\n", result.output)

@test
def environment_variables_can_be_added_for_run(shell):
    result = shell.run(["sh", "-c", "echo $NAME"], update_env={"NAME": "Bob"})
    assert_equal("Bob\n", result.output)

@test
def exception_is_raised_if_return_code_is_not_zero(shell):
    assert_raises(spur.RunProcessError, lambda: shell.run(["false"]))

@test
def exception_has_output_from_command(shell):
    try:
        shell.run(["sh", "-c", "echo Hello world!; false"])
        assert_true(False)
    except spur.RunProcessError as error:
        assert_equal("Hello world!\n", error.output)

@test
def exception_has_stderr_output_from_command(shell):
    try:
        shell.run(["sh", "-c", "echo Hello world! 1>&2; false"])
        assert_true(False)
    except spur.RunProcessError as error:
        assert_equal("Hello world!\n", error.stderr_output)

@test
def exception_message_contains_return_code_and_all_output(shell):
    try:
        shell.run(["sh", "-c", "echo starting; echo failed! 1>&2; exit 1"])
        assert_true(False)
    except spur.RunProcessError as error:
        assert_equal(
            "return code: 1\noutput: starting\n\nstderr output: failed!\n",
            error.message
        )

@test
def return_code_stored_if_errors_allowed(shell):
    result = shell.run(["sh", "-c", "exit 14"], allow_error=True)
    assert_equal(14, result.return_code)

@test
def can_tell_if_spawned_process_is_running(shell):
    process = shell.spawn(["sh", "-c", "echo after; read dont_care; echo after"])
    assert_equal(True, process.is_running())
    process.stdin_write("\n")
    # TODO: Remove sleep
    import time
    time.sleep(1)
    assert_equal(False, process.is_running())
