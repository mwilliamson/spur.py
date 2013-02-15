import spur

from . import open_test_set, process_test_set


def _run_local_test(test_func):
    with spur.LocalShell() as shell:
        test_func(shell)


LocalOpenTests = open_test_set.create("LocalOpenTests", _run_local_test)
LocalProcessTests = process_test_set.create("LocalProcessTests", _run_local_test)
