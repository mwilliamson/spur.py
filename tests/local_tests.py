import spur

from . import tests, process_tests


def _run_local_test(test_func):
    with spur.LocalShell() as shell:
        test_func(shell)


LocalTests = tests.create("LocalTests", _run_local_test)
LocalProcessTests = process_tests.create("LocalProcessTests", _run_local_test)
