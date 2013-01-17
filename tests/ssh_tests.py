from nose.tools import istest, assert_equal, assert_raises, assert_true

import spur
import spur.ssh


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
    
