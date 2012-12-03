# spur.py: Run commands and manipulate files locally or over SSH using the same interface

To run echo locally:

```python
import spur

shell = spur.LocalShell()
result = shell.run(["echo", "-n", "hello"])
print result.output # prints hello
```

Executing the same command over SSH uses the same interface -- the only difference
is how the shell is created:

```python
import spur

shell = spur.SshShell(hostname="localhost", username="bob", password="password1")
result = shell.run(["echo", "-n", "hello"])
print result.output # prints hello
```

## Shell constructors

### LocalShell

Takes no arguments:

```python
spur.LocalShell()
```

### SshShell

Requires a hostname and a username. Also requires some combination of a password
and private key, as necessary to authenticate:

```python
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
```

## Operations

### run(command, cwd, update_env)

Run a command and wait for it to complete. The command is expected to be a list
of strings.

```python
result = shell.run(["echo", "-n", "hello"])
print result.output # prints hello
```

Note that arguments are passed without any shell expansion. For instance,
`shell.run(["echo", "$PATH"])` will print the literal string `$PATH` rather
than the value of the environment variable `$PATH`.

Optional arguments:

* `cwd` -- change the current directory to this value before executing the
  command
* `update_env` -- a `dict` containing environment variables to be set before
  running the command. If there's an existing environment variable with the same
  name, it will be overwritten. Otherwise, it is unchanged.
