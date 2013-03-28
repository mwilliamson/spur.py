from nose.tools import istest, assert_raises

import spur
import spur.ssh
from .testing import create_ssh_shell
from . import open_test_set, process_test_set


def _run_ssh_test(test_func):
    with create_ssh_shell() as shell:
        test_func(shell)
        
        
SshOpenTests = open_test_set.create("SshOpenTests", _run_ssh_test)
SshProcessTests = process_test_set.create("SshProcessTests", _run_ssh_test)


@istest
def attempting_to_connect_to_wrong_port_raises_connection_error():
    def try_connection():
        shell = _create_shell_with_wrong_port()
        shell.run(["echo", "hello"])
        
    assert_raises(spur.ssh.ConnectionError, try_connection)


@istest
def connection_error_contains_original_error():
    try:
        shell = _create_shell_with_wrong_port()
        shell.run(["true"])
        # Expected error
        assert False
    except spur.ssh.ConnectionError as error:
        assert isinstance(error.original_error, IOError)


@istest
def connection_error_contains_traceback_for_original_error():
    try:
        shell = _create_shell_with_wrong_port()
        shell.run(["true"])
        # Expected error
        assert False
    except spur.ssh.ConnectionError as error:
        assert "Traceback (most recent call last):" in error.original_traceback


@istest
def missing_host_key_set_to_accept_allows_connection_with_missing_host_key():
    with create_ssh_shell(missing_host_key=spur.ssh.MissingHostKey.accept) as shell:
        shell.run(["true"])


@istest
def missing_host_key_set_to_warn_allows_connection_with_missing_host_key():
    with create_ssh_shell(missing_host_key=spur.ssh.MissingHostKey.warn) as shell:
        shell.run(["true"])


@istest
def missing_host_key_set_to_raise_error_raises_error_when_missing_host_key():
    with create_ssh_shell(missing_host_key=spur.ssh.MissingHostKey.raise_error) as shell:
        assert_raises(spur.ssh.ConnectionError, lambda: shell.run(["true"]))
        

@istest
def trying_to_use_ssh_shell_after_exit_results_in_error():
    with create_ssh_shell() as shell:
        pass
        
    assert_raises(Exception, lambda: shell.run(["true"]))


def _create_shell_with_wrong_port():
    return spur.SshShell(
        username="bob",
        password="password1",
        hostname="localhost",
        port=54321,
        missing_host_key=spur.ssh.MissingHostKey.accept,
    )
