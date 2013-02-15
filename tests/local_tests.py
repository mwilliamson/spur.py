import spur

from . import tests


def _run_local_test(test_func):
    with spur.LocalShell() as shell:
        test_func(shell)

LocalTests = tests.create("LocalTests", _run_local_test)
