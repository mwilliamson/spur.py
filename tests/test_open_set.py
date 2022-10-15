from __future__ import unicode_literals

import uuid
import functools

import pytest

__all__ = ["OpenTestSet"]


def wrapper(test_func):
    @functools.wraps(test_func)
    def run_test(self, *args, **kwargs):
        with self.create_shell() as shell:
            test_func(shell)

    return run_test


class OpenTestSet(object):
    @wrapper
    def test_can_write_to_files_opened_by_open(shell):
        path = "/tmp/{0}".format(uuid.uuid4())
        f = shell.open(path, "w")
        try:
            f.write("hello")
            f.flush()
            assert b"hello" == shell.run(["cat", path]).output
        finally:
            f.close()
            shell.run(["rm", path])

    @wrapper
    def test_can_read_files_opened_by_open(shell):
        path = "/tmp/{0}".format(uuid.uuid4())
        shell.run(["sh", "-c", "echo hello > '{0}'".format(path)])
        f = shell.open(path)
        try:
            assert "hello\n" == f.read()
        finally:
            f.close()
            shell.run(["rm", path])

    @wrapper
    def test_open_can_be_used_as_context_manager(shell):
        path = "/tmp/{0}".format(uuid.uuid4())
        shell.run(["sh", "-c", "echo hello > '{0}'".format(path)])
        with shell.open(path) as f:
            assert "hello\n" == f.read()

    @wrapper
    def test_files_can_be_opened_in_binary_mode(shell):
        path = "/tmp/{0}".format(uuid.uuid4())
        shell.run(["sh", "-c", "echo hello > '{0}'".format(path)])
        with shell.open(path, "rb") as f:
            assert b"hello\n" == f.read()
