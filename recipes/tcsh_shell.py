class TcshShellType(object):
    """A shell type for tcsh
    
    Note that this is untested code.
    
    Contributed by @MHC03."""
    supports_which = True
    
    def generate_run_command(
        self,
        command_args,
        store_pid,
        cwd=None,
        update_env={},
        new_process_group=False,
    ):
        commands = []

        if store_pid:
            commands.append("echo $$")

        if cwd is not None:
            commands.append("cd {0} |& cat || (( echo '\n'spur-cd: $?; exit 1; ))".format(escape_sh(cwd)))
            commands.append("echo '\n'spur-cd: 0")

        update_env_commands = [
            "set {0}={1}".format(key, escape_sh(value))
            for key, value in update_env.items()
        ]
        commands += update_env_commands
        which_commands = " || ".join(self._generate_which_commands(command_args[0]))
        which_commands = "( ( " + which_commands + "; ) && echo 0; ) || ( echo $?; exit 1; )"
        commands.append(which_commands)
        
        command = " ".join(map(escape_sh, command_args))
        command = "exec {0}".format(command)
        if new_process_group:
            command = "setsid {0}".format(command)
        commands.append(command)
        return "; ".join(commands)
    
    def _generate_which_commands(self, command):
        which_commands = ["command -v {0}", "which {0}"]
        return (
            self._generate_which_command(which, command)
            for which in which_commands
        )
    
    def _generate_which_command(self, which, command):
        return which.format(escape_sh(command)) + " >& /dev/null"


def escape_sh(value):
    return "'" + value.replace("'", "'\\''") + "'"
