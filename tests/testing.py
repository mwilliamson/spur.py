import os

import spur


def create_ssh_shell():
    port_var = os.environ.get("TEST_SSH_PORT")
    port = int(port_var) if port_var is not None else None
    return spur.SshShell(
        hostname=os.environ.get("TEST_SSH_HOSTNAME", "127.0.0.1"),
        username=os.environ["TEST_SSH_USERNAME"],
        password=os.environ["TEST_SSH_PASSWORD"],
        port=port
    )
