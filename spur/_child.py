from __future__ import absolute_import
from __future__ import print_function

import atexit
from .errors import NoSuchCommandError
import os
from .results import RunProcessError
import signal
import sys
import threading
import traceback


_CHILDREN = []


def register(shell, process, cleanup):
    _CHILDREN.append((shell, process, cleanup))


def unregister(process_arg):
    for idx, (_, process, _) in enumerate(_CHILDREN):
        if process_arg is process:
            del _CHILDREN[idx]


def cleanup_children():
    _CLEANUP_LOCK.acquire()
    while len(_CHILDREN) > 0:
        shell, process, cleanup = _CHILDREN.pop()
        if process.is_running():
            if cleanup:
                try:
                    shell.run(cleanup)
                except (NoSuchCommandError, RunProcessError) as e:
                    # send SIGKILL in the hopes that will be enough
                    process.send_signal(signal.SIGKILL)
                    # restart to ensure no child is left behind
                    cleanup_children()

                    # NOTE: cannot reraise because exit code is zero and
                    #       traceback is printed twice
                    stack_info = traceback.extract_stack()
                    print("While executing cleanup command %s" % cleanup,
                          file=sys.stderr)
                    print("Traceback (most recent call last):", file=sys.stderr)
                    msg = traceback.format_list(stack_info[:-1])
                    print("".join(msg), end="", file=sys.stderr)
                    exc_type, exc_value, tb = sys.exc_info()
                    info = traceback.extract_tb(tb)
                    msg = traceback.format_list(info)
                    print("".join(msg), end="", file=sys.stderr)
                    print("%s.%s: %s" % (
                        exc_type.__module__, exc_type.__name__, exc_value),
                          file=sys.stderr)
                    os._exit(1)
            else:
                try:
                    process.send_signal(signal.SIGKILL)
                except RunProcessError:
                    pass
    _CLEANUP_LOCK.release()

_CLEANUP_LOCK = threading.RLock()
atexit.register(cleanup_children)
