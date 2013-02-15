import functools
import StringIO
import time
import uuid
import signal

from nose.tools import istest, assert_equal, assert_not_equal, assert_raises, assert_true

import spur
from .testing import create_ssh_shell
from test_sets import TestSetBuilder


__all__ = ["create"]


test_set_builder = TestSetBuilder()

create = test_set_builder.create

test = test_set_builder.add_test


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
def can_get_result_of_spawned_process(shell):
    process = shell.spawn(["echo", "hello"])
    result = process.wait_for_result()
    assert_equal("hello\n", result.output)
    
@test
def calling_wait_for_result_is_idempotent(shell):
    process = shell.spawn(["echo", "hello"])
    process.wait_for_result()
    result = process.wait_for_result()
    assert_equal("hello\n", result.output)
    
@test
def wait_for_result_raises_error_if_return_code_is_not_zero(shell):
    process = shell.spawn(["false"])
    assert_raises(spur.RunProcessError, process.wait_for_result)

@test
def can_write_to_stdin_of_spawned_processes(shell):
    process = shell.spawn(["sh", "-c", "read value; echo $value"])
    process.stdin_write("hello\n")
    result = process.wait_for_result()
    assert_equal("hello\n", result.output)

@test
def can_tell_if_spawned_process_is_running(shell):
    process = shell.spawn(["sh", "-c", "echo after; read dont_care; echo after"])
    assert_equal(True, process.is_running())
    process.stdin_write("\n")
    _wait_for_assertion(lambda: assert_equal(False, process.is_running()))
    
@test
def can_write_stdout_to_file_object_while_process_is_executing(shell):
    output_file = StringIO.StringIO()
    process = shell.spawn(
        ["sh", "-c", "echo hello; read dont_care;"],
        stdout=output_file
    )
    _wait_for_assertion(lambda: assert_equal("hello\n", output_file.getvalue()))
    assert process.is_running()
    process.stdin_write("\n")
    assert_equal("hello\n", process.wait_for_result().output)
    
@test
def can_write_stderr_to_file_object_while_process_is_executing(shell):
    output_file = StringIO.StringIO()
    process = shell.spawn(
        ["sh", "-c", "echo hello 1>&2; read dont_care;"],
        stderr=output_file
    )
    _wait_for_assertion(lambda: assert_equal("hello\n", output_file.getvalue()))
    assert process.is_running()
    process.stdin_write("\n")
    assert_equal("hello\n", process.wait_for_result().stderr_output)
        
@test
def can_get_process_id_of_process_if_store_pid_is_true(shell):
    process = shell.spawn(["sh", "-c", "echo $$"], store_pid=True)
    result = process.wait_for_result()
    assert_equal(int(result.output.strip()), process.pid)
    
@test
def process_id_is_not_available_if_store_pid_is_not_set(shell):
    process = shell.spawn(["sh", "-c", "echo $$"])
    assert not hasattr(process, "pid")
        
@test
def can_send_signal_to_process_if_store_pid_is_set(shell):
    process = shell.spawn(["cat"], store_pid=True)
    assert process.is_running()
    process.send_signal(signal.SIGTERM)
    _wait_for_assertion(lambda: assert_equal(False, process.is_running()))
    
    
@test
def spawning_non_existent_command_raises_specific_no_such_command_exception(shell):
    try:
        shell.spawn(["bin/i-am-not-a-command"])
        # Expected exception
        assert False
    except spur.NoSuchCommandError as error:
        assert_equal("No such command: bin/i-am-not-a-command", error.message)
        assert_equal("bin/i-am-not-a-command", error.command)


@test
def spawning_command_that_uses_path_env_variable_asks_if_command_is_installed(shell):
    try:
        shell.spawn(["i-am-not-a-command"])
        # Expected exception
        assert False
    except spur.NoSuchCommandError as error:
        expected_message = (
            "Command not found: i-am-not-a-command." +
            " Check that i-am-not-a-command is installed and on $PATH"
        )
        assert_equal(expected_message, error.message)
        assert_equal("i-am-not-a-command", error.command)


@test
def commands_are_run_without_pseudo_terminal_by_default(shell):
    result = shell.run(["bash", "-c", "[ -t 0 ]"], allow_error=True)
    assert_not_equal(0, result.return_code)
    

@test
def command_can_be_explicitly_run_with_pseudo_terminal(shell):
    result = shell.run(["bash", "-c", "[ -t 0 ]"], allow_error=True, use_pty=True)
    assert_equal(0, result.return_code)
    

@test
def output_is_captured_when_using_pty(shell):
    result = shell.run(["echo", "-n", "hello"], use_pty=True)
    assert_equal("hello", result.output)
    

@test
def stderr_is_redirected_stdout_when_using_pty(shell):
    result = shell.run(["sh", "-c", "echo -n hello 1>&2"], use_pty=True)
    assert_equal("hello", result.output)
    assert_equal("", result.stderr_output)
    

@test
def can_write_to_stdin_of_spawned_process_when_using_pty(shell):
    process = shell.spawn(["sh", "-c", "read value; echo $value"], use_pty=True)
    process.stdin_write("hello\n")
    result = process.wait_for_result()
    # Get the output twice since the pty echoes input
    assert_equal("hello\r\nhello\r\n", result.output)

    
@test
def can_write_to_files_opened_by_open(shell):
    path = "/tmp/{0}".format(uuid.uuid4())
    f = shell.open(path, "w")
    try:
        f.write("hello")
        f.flush()
        assert_equal("hello", shell.run(["cat", path]).output)
    finally:
        f.close()
        shell.run(["rm", path])
        
@test
def can_read_files_opened_by_open(shell):
    path = "/tmp/{0}".format(uuid.uuid4())
    shell.run(["sh", "-c", "echo hello > '{0}'".format(path)])
    f = shell.open(path)
    try:
        assert_equal("hello\n", f.read())
    finally:
        f.close()
        shell.run(["rm", path])
        
@test
def open_can_be_used_as_context_manager(shell):
    path = "/tmp/{0}".format(uuid.uuid4())
    shell.run(["sh", "-c", "echo hello > '{0}'".format(path)])
    with shell.open(path) as f:
        assert_equal("hello\n", f.read())
        

# TODO: timeouts in wait_for_result

def _wait_for_assertion(assertion):
    timeout = 1
    period = 0.01
    start = time.time()
    while True:
        try:
            assertion()
            return
        except AssertionError:
            if time.time() - start > timeout:
                raise
            time.sleep(period)
