spur.py: Run commands and manipulate files locally or over SSH using the same interface
=======================================================================================

To run echo locally:

.. code-block:: python

    import spur

    shell = spur.LocalShell()
    result = shell.run(["echo", "-n", "hello"])
    print result.output # prints hello

Executing the same command over SSH uses the same interface -- the only
difference is how the shell is created:

.. code-block:: python

    import spur

    shell = spur.SshShell(hostname="localhost", username="bob", password="password1")
    with shell:
        result = shell.run(["echo", "-n", "hello"])
    print result.output # prints hello

Installation
------------

``$ pip install spur``

Shell constructors
------------------

LocalShell
~~~~~~~~~~

Takes no arguments:

.. code-block:: sh

    spur.LocalShell()

SshShell
~~~~~~~~

Requires a hostname. Also requires some combination of a username,
password and private key, as necessary to authenticate:

.. code-block:: python

    # Use a password
    spur.SshShell(
        hostname="localhost",
        username="bob",
        password="password1"
    )
    # Use a private key
    spur.SshShell(
        hostname="localhost",
        username="bob",
        private_key_file="path/to/private.key"
    )
    # Use a port other than 22
    spur.SshShell(
        hostname="localhost",
        port=50022,
        username="bob",
        password="password1"
    )

Optional arguments:

* ``connect_timeout`` -- a timeout in seconds for establishing an SSH
  connection. Defaults to 60 (one minute).

* ``missing_host_key`` -- by default, an error is raised when a host
  key is missing. One of the following values can be used to change the
  behaviour when a host key is missing:
   
  - ``spur.ssh.MissingHostKey.raise_error`` -- raise an error
  - ``spur.ssh.MissingHostKey.warn`` -- accept the host key and log a
    warning
  - ``spur.ssh.MissingHostKey.accept`` -- accept the host key

Shell interface
---------------

run(command, cwd, update\_env, store\_pid, allow\_error, stdout, stderr)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run a command and wait for it to complete. The command is expected to be
a list of strings. Returns an instance of ``ExecutionResult``.

.. code-block:: python

    result = shell.run(["echo", "-n", "hello"])
    print result.output # prints hello

Note that arguments are passed without any shell expansion. For
instance, ``shell.run(["echo", "$PATH"])`` will print the literal string
``$PATH`` rather than the value of the environment variable ``$PATH``.

Raises ``spur.NoSuchCommandError`` if trying to execute a non-existent
command.

Optional arguments:

* ``cwd`` -- change the current directory to this value before
  executing the command.
* ``update_env`` -- a ``dict`` containing environment variables to be
  set before running the command. If there's an existing environment
  variable with the same name, it will be overwritten. Otherwise, it is
  unchanged.
* ``store_pid`` -- if set to ``True`` when calling ``spawn``, store the
  process id of the spawned process as the attribute ``pid`` on the
  returned process object. Has no effect when calling ``run``.
* ``allow_error`` -- ``False`` by default. If ``False``, an exception
  is raised if the return code of the command is anything but 0. If
  ``True``, a result is returned irrespective of return code.
* ``stdout`` -- if not ``None``, anything the command prints to
  standard output during its execution will also be written to
  ``stdout`` using ``stdout.write``.
* ``stderr`` -- if not ``None``, anything the command prints to
  standard error during its execution will also be written to
  ``stderr`` using ``stderr.write``.

``shell.run(*args, **kwargs)`` should behave similarly to
``shell.spawn(*args, **kwargs).wait_for_result()``

spawn(command, cwd, update\_env, store\_pid, allow\_error, stdout, stderr)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Behaves the same as ``run`` except that ``spawn`` immediately returns an
object representing the running process.

Raises ``spur.NoSuchCommandError`` if trying to execute a non-existent
command.

open(path, mode="r")
~~~~~~~~~~~~~~~~~~~~

Open the file at ``path``. Returns a file-like object.

Process interface
-----------------

Returned by calls to ``shell.spawn``. Has the following attributes:

* ``pid`` -- the process ID of the process. Only available if
  ``store_pid`` was set to ``True`` when calling ``spawn``.

Has the following methods:

* ``is_running()`` -- return ``True`` if the process is still running,
  ``False`` otherwise.
* ``stdin_write(value)`` -- write ``value`` to the standard input of
  the process.
* ``wait_for_result()`` -- wait for the process to exit, and then
  return an instance of ``ExecutionResult``. Will raise
  ``RunProcessError`` if the return code is not zero and
  ``shell.spawn`` was not called with ``allow_error=True``.
* ``send_signal(signal)`` -- sends the process the signal ``signal``.
  Only available if ``store_pid`` was set to ``True`` when calling
  ``spawn``.

Classes
-------

ExecutionResult
~~~~~~~~~~~~~~~

``ExecutionResult`` has the following properties:

* ``return_code`` -- the return code of the command
* ``output`` -- a string containing the result of capturing stdout
* ``stderr_output`` -- a string containing the result of capturing
  stdout

It also has the following methods:

* ``to_error()`` -- return the corresponding RunProcessError. This is
  useful if you want to conditionally raise RunProcessError, for
  instance:

.. code-block:: python

    result = shell.run(["some-command"], allow_error=True)
    if result.return_code > 4:
        raise result.to_error()

RunProcessError
~~~~~~~~~~~~~~~

A subclass of ``RuntimeError`` with the same properties as
``ExecutionResult``:

* ``return_code`` -- the return code of the command
* ``output`` -- a string containing the result of capturing stdout
* ``stderr_output`` -- a string containing the result of capturing
  stdout

NoSuchCommandError
~~~~~~~~~~~~~~~~~~

``NoSuchCommandError`` has the following properties:

* ``command`` -- the command that could not be found

API stability
-------------

Using the the terminology from `Semantic
Versioning <http://semver.org/spec/v1.0.0.html>`_, if the version of
spur is X.Y.Z, then X is the major version, Y is the minor version, and
Z is the patch version.

While the major version is 0, incrementing the patch version indicates a
backwards compatible change. For instance, if you're using 0.3.1, then
it should be safe to upgrade to 0.3.2.

Incrementing the minor version indicates a change in the API. This means
that any code using previous minor versions of spur may need updating
before it can use the current minor version.

Undocumented features
~~~~~~~~~~~~~~~~~~~~~

Some features are undocumented, and should be considered experimental.
Use them at your own risk. They may not behave correctly, and their
behaviour and interface may change at any time.

Troubleshooting
---------------

I get the error "Connection refused" when trying to connect to a virtual machine using a forwarded port on ``localhost``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try using ``"127.0.0.1"`` instead of ``"localhost"`` as the hostname.

I get the error "Connection refused" when trying to execute commands over SSH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try connecting to the machine using SSH on the command line with the
same settings. For instance, if you're using the code:

.. code-block:: python

    shell = spur.SshShell(
            hostname="remote",
            port=2222,
            username="bob",
            private_key_file="/home/bob/.ssh/id_rsa"
        )
    with shell:
        result = shell.run(["echo", "hello"])

Try running:

.. code-block:: sh

    ssh bob@remote -p 2222 -i /home/bob/.ssh/id_rsa

If the ``ssh`` command succeeds, make sure that the arguments to
``ssh.SshShell`` and the ``ssh`` command are the same. If any of the
arguments to ``ssh.SshShell`` are dynamically generated, try hard-coding
them to make sure they're set to the values you expect.
