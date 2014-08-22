import os

import spur
import spur.ssh


def create_ssh_shell(missing_host_key=None, shell_type=None):
    port_var = os.environ.get("TEST_SSH_PORT")
    port = int(port_var) if port_var is not None else None
    return spur.SshShell(
        hostname=os.environ.get("TEST_SSH_HOSTNAME", "127.0.0.1"),
        username=os.environ["TEST_SSH_USERNAME"],
        password=os.environ["TEST_SSH_PASSWORD"],
        port=port,
        missing_host_key=(missing_host_key or spur.ssh.MissingHostKey.accept),
        shell_type=shell_type,
    )
