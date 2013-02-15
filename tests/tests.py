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
