from __future__ import unicode_literals

import io
import socket

from nose.tools import istest, assert_raises, assert_equal
from paramiko.util import retry_on_signal

import spur
import spur.ssh
from .testing import create_ssh_shell, HOSTNAME, PORT, PASSWORD, USERNAME
from .process_test_set import ProcessTestSet
from .open_test_set import OpenTestSet


class SshTestMixin(object):
    def create_shell(self):
        return create_ssh_shell()
    

@istest
class SshOpenTests(OpenTestSet, SshTestMixin):
    pass


@istest
class SshProcessTests(ProcessTestSet, SshTestMixin):
    pass


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


@istest
def an_open_socket_can_be_used_for_ssh_connection_with_sock_argument():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    retry_on_signal(lambda: sock.connect((HOSTNAME, PORT)))

    with _create_shell_with_wrong_port(sock=sock) as shell:
        result = shell.run(["echo", "hello"])
        assert_equal(b"hello\n", result.output)


def _create_shell_with_wrong_port(**kwargs):
    return spur.SshShell(
        username=USERNAME,
        password=PASSWORD,
        hostname=HOSTNAME,
        port=54321,
        missing_host_key=spur.ssh.MissingHostKey.accept,
        **kwargs
    )


class MinimalSshTestMixin(object):
    def create_shell(self):
        return create_ssh_shell(shell_type=spur.ssh.ShellTypes.minimal)
    

@istest
class MinimalSshOpenTests(OpenTestSet, MinimalSshTestMixin):
    pass


@istest
class MinimalSshProcessTests(ProcessTestSet, MinimalSshTestMixin):
    spawning_command_that_uses_path_env_variable_asks_if_command_is_installed = None
    spawning_non_existent_command_raises_specific_no_such_command_exception = None
    
    can_get_process_id_of_process_if_store_pid_is_true = None
    can_send_signal_to_process_if_store_pid_is_set = None

    # cwd is not supported when using a minimal shell
    using_non_existent_cwd_raises_could_not_change_directory_error = None
    attempting_to_change_directory_without_permissions_raises_cannot_change_directory_error = None
    using_non_existent_cwd_and_command_raises_could_not_change_directory_error = None
    using_non_existent_command_and_correct_cwd_raises_no_such_command_exception = None
    can_find_command_in_cwd = None
    
    @istest
    def cannot_store_pid(self):
        self._assert_unsupported_feature(store_pid=True)
    
    cwd_of_run_can_be_set = None
    
    @istest
    def cannot_set_cwd(self):
        self._assert_unsupported_feature(cwd="/")
    
    environment_variables_can_be_added_for_run = None
    
    @istest
    def update_env_can_be_empty(self):
        self._assert_supported_feature(update_env={})
        
    @istest
    def cannot_update_env(self):
        self._assert_unsupported_feature(update_env={"x": "one"})
        
    @istest
    def cannot_set_new_process_group(self):
        self._assert_unsupported_feature(new_process_group=True)
    
    
    def _assert_supported_feature(self, **kwargs):
        with self.create_shell() as shell:
            result = shell.run(["echo", "hello"], **kwargs)
        
        assert_equal(b"hello\n", result.output)
    
    
    def _assert_unsupported_feature(self, **kwargs):
        name, = kwargs.keys()
        
        try:
            with self.create_shell() as shell:
                shell.run(["echo", "hello"], **kwargs)
            assert False, "Expected error"
        except spur.ssh.UnsupportedArgumentError as error:
            assert_equal("'{0}' is not supported when using a minimal shell".format(name), str(error))



@istest
class ReadInitializationLineTests(object):
    @istest
    def reading_initialization_line_returns_int_from_line_of_file(self):
        assert_equal(42, spur.ssh._read_int_initialization_line(io.StringIO("42\n")))
        
    @istest
    def blank_lines_are_skipped(self):
        assert_equal(42, spur.ssh._read_int_initialization_line(io.StringIO("\n \n\t\t\n42\n")))
        
    @istest
    def error_if_non_blank_line_is_not_integer(self):
        try:
            spur.ssh._read_int_initialization_line(io.StringIO("x\n"))
            assert False, "Expected error"
        except spur.CommandInitializationError as error:
            assert "Failed to parse line 'x' as integer" in str(error)
