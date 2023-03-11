import pytest


def assert_equal(expected, actual):
    assert expected == actual


def assert_not_equal(expected, actual):
    assert expected != actual


def assert_raises(exception_type, func):
    pytest.raises(exception_type, func)
