from nose.tools import istest, assert_raises

import spur
import spur.ssh
from .testing import create_ssh_shell


@istest
def attempting_to_connect_to_wrong_port_raises_connection_error():
    def try_connection():
        shell = spur.SshShell(
            username="bob",
            password="password1",
            hostname="localhost",
            port=54321
        )
        shell.run(["echo", "hello"])
        
    assert_raises(spur.ssh.ConnectionError, try_connection)
    

@istest
def trying_to_use_ssh_shell_after_exit_results_in_error():
    with create_ssh_shell() as shell:
        pass
        
    assert_raises(Exception, lambda: shell.run(["true"]))
