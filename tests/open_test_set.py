from __future__ import unicode_literals

import uuid
import functools

from .assertions import assert_equal


__all__ = ["OpenTestSet"]


def with_shell(test_func):
    @functools.wraps(test_func)
    def run_test(self, *args, **kwargs):
        with self.create_shell() as shell:
            test_func(shell)

    return run_test


class OpenTestSet(object):
    @with_shell
    def test_can_write_to_files_opened_by_open(shell):
        path = "/tmp/{0}".format(uuid.uuid4())
        f = shell.open(path, "w")
        try:
            f.write("hello")
            f.flush()
            assert_equal(b"hello", shell.run(["cat", path]).output)
        finally:
            f.close()
            shell.run(["rm", path])

    @with_shell
    def test_can_read_files_opened_by_open(shell):
        path = "/tmp/{0}".format(uuid.uuid4())
        shell.run(["sh", "-c", "echo hello > '{0}'".format(path)])
        f = shell.open(path)
        try:
            assert_equal("hello\n", f.read())
        finally:
            f.close()
            shell.run(["rm", path])

    @with_shell
    def test_open_can_be_used_as_context_manager(shell):
        path = "/tmp/{0}".format(uuid.uuid4())
        shell.run(["sh", "-c", "echo hello > '{0}'".format(path)])
        with shell.open(path) as f:
            assert_equal("hello\n", f.read())

    @with_shell
    def test_files_can_be_opened_in_binary_mode(shell):
        path = "/tmp/{0}".format(uuid.uuid4())
        shell.run(["sh", "-c", "echo hello > '{0}'".format(path)])
        with shell.open(path, "rb") as f:
            assert_equal(b"hello\n", f.read())
