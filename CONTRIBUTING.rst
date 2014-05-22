Contributing
============

Tests
-----

You can run the tests using tox.
The SSH tests require a running SSH server.
The following environment variables are used in the SSH tests:

* ``TEST_SSH_HOSTNAME``
* ``TEST_SSH_PORT`` (optional)
* ``TEST_SSH_USERNAME``
* ``TEST_SSH_PASSWORD``

Tests should pass on CPython 2.6/3.2 and later.
There's currently no support for PyPy since paramiko doesn't appear to install on PyPy
(in turn, because of PyCrypto).
