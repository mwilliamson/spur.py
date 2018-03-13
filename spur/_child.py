from __future__ import absolute_import
import atexit
from .results import RunProcessError
import signal
import threading


_CHILDREN = []


def register(process):
    _CHILDREN.append(process)


def unregister(process_arg):
    for idx, process in enumerate(_CHILDREN):
        if process_arg is process:
            del _CHILDREN[idx]


def cleanup_children():
    _CLEANUP_LOCK.acquire()
    while len(_CHILDREN) > 0:
        process = _CHILDREN.pop()
        if process.is_running():
            try:
                process.send_signal(signal.SIGKILL)
            except RunProcessError:
                pass
    _CLEANUP_LOCK.release()

_CLEANUP_LOCK = threading.RLock()
atexit.register(cleanup_children)
