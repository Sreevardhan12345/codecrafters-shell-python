"""Builtin commands and their registration."""

import os
from collections.abc import Callable

from commandHandlers.ExternalHandler import find_executable
from common.registry import Registry
from common.result import Result
from common.systemInfo import home_directory


Builtin = Callable[[list[str]], Result]
BUILTINS: Registry[Builtin] = Registry("built-ins")
# Completion specifications are shell state, rather than builtins themselves.
# Keep the script exactly as parsed and render it only when queried so that
# `complete -p` has one canonical representation.
COMPLETERS: dict[str, str] = {}


@BUILTINS.register("EXIT")
def exit_shell(_: list[str]) -> Result:
    """Exit the interactive shell."""
    raise SystemExit(0)


@BUILTINS.register("ECHO")
def echo_shell(args: list[str]) -> Result:
    """Print arguments separated by one space."""
    return Result(0, stdout=" ".join(args) + "\n")


@BUILTINS.register("PWD")
def pwd_shell(_: list[str]) -> Result:
    """Print the current working directory."""
    return Result(0, stdout=os.getcwd() + "\n")


@BUILTINS.register("CD")
def cd_shell(args: list[str]) -> Result:
    """Change directory; a standalone tilde means HOME."""
    if not args:
        return Result(1, stderr="cd: missing operand\n")

    target = home_directory() if args[0] == "~" else args[0]
    try:
        os.chdir(target)
    except FileNotFoundError:
        return Result(1, stderr=f"cd: {args[0]}: No such file or directory\n")
    except NotADirectoryError:
        return Result(1, stderr=f"cd: {args[0]}: Not a directory\n")
    except PermissionError:
        return Result(1, stderr=f"cd: {args[0]}: Permission denied\n")
    return Result(0)


@BUILTINS.register("TYPE")
def type_shell(args: list[str]) -> Result:
    """Describe whether a name resolves to a builtin or PATH executable."""
    if not args:
        return Result(1, stderr="type: missing operand\n")

    target = args[0]
    if target in BUILTINS:
        return Result(0, stdout=f"{target} is a shell builtin\n")

    executable = find_executable(target)
    if executable:
        return Result(0, stdout=f"{target} is {executable}\n")
    return Result(1, stderr=f"{target}: not found\n")


@BUILTINS.register("COMPLETE")
def complete_shell(args: list[str]) -> Result:
    """Register completer scripts and print their normalized specifications."""

    if len(args) >= 3 and args[0] == "-C":
        script, command = args[1], args[2]
        COMPLETERS[command] = script
        return Result(0)

    if len(args) >= 2 and args[0] == "-p":
        command = args[1]
        script = COMPLETERS.get(command)
        if script is not None:
            return Result(0, stdout=f"complete -C '{script}' {command}\n")
        return Result(0, stderr=f"complete: {command}: no completion specification\n")
    return Result(0)
