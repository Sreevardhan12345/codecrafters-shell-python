import os
import sys

from .ExternalHandler import EXTERNAL
from common.registry import Registry
from common.systemInfo import HOME
from common.result import Result

BUILTINS = Registry("built-ins")


@BUILTINS.register("EXIT")
def exit_shell(args):
    sys.exit(0)


@BUILTINS.register("ECHO")
def echo_shell(args):
    return Result(0, stdout=" ".join(args)+"\n")


@BUILTINS.register("PWD")
def pwd_shell(args):
    return Result(0, stdout=os.getcwd()+"\n")



@BUILTINS.register("CD")
def cd_shell(args):
    if not args:
        return Result(1, stderr="cd: missing operand\n")

    target = HOME if args[0] == "~" else args[0]
    try:
        os.chdir(target)
    except FileNotFoundError:
        return Result(1, stderr=f"cd: {args[0]}: No such file or directory\n")


@BUILTINS.register("TYPE")
def type_shell(args):
    if not args:
        return Result(1, stderr="type: missing operand\n")

    target = args[0]
    if target.upper() in BUILTINS:
        return Result(0, stdout=f"{target} is a shell builtin\n")

    executable = EXTERNAL.get("FIND")(target)
    if executable:
        return Result(0, stdout=f"{target} is {executable}\n")
    else:
        return Result(1, stderr=f"{target}: not found\n")
