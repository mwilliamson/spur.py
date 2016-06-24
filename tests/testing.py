import os

import spur
import spur.ssh


def _int_or_none(val):
    return int(val) if val is not None else None


HOSTNAME = os.environ.get("TEST_SSH_HOSTNAME", "127.0.0.1")
USERNAME = os.environ["TEST_SSH_USERNAME"]
PASSWORD = os.environ["TEST_SSH_PASSWORD"]
PORT = _int_or_none(os.environ.get("TEST_SSH_PORT", 22))


def create_ssh_shell(missing_host_key=None, shell_type=None):
    return spur.SshShell(
        hostname=HOSTNAME,
        username=USERNAME,
        password=PASSWORD,
        port=PORT,
        missing_host_key=(missing_host_key or spur.ssh.MissingHostKey.accept),
        shell_type=shell_type,
    )
