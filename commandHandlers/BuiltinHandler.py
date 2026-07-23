import os
import sys

from .ExternalHandler import EXTERNAL
from common.registry import Registry
from common.systemInfo import HOME

BUILTINS = Registry("built-ins")


@BUILTINS.register("EXIT")
def exit_shell(args):
    sys.exit(0)


@BUILTINS.register("ECHO")
def echo_shell(args):
    return(" ".join(args)+"\n")


@BUILTINS.register("PWD")
def pwd_shell(args):
    return(os.getcwd()+"\n")



@BUILTINS.register("CD")
def cd_shell(args):
    if not args:
        return("cd: missing operand")

    target = HOME if args[0] == "~" else args[0]
    try:
        os.chdir(target)
    except FileNotFoundError:
        return(f"cd: {args[0]}: No such file or directory\n")


@BUILTINS.register("TYPE")
def type_shell(args):
    if not args:
        return("type: missing operand")

    target = args[0]
    if target.upper() in BUILTINS:
        return(f"{target} is a shell builtin\n")

    executable = EXTERNAL.get("FIND")(target)
    if executable:
        return(f"{target} is {executable}\n")
    else:
        return(f"{target}: not found\n")
    
# @BUILTINS.register("CAT")
# def cat_shell(args):
#     if not args:
#         return("cat: missing operand")

#     output = ""
#     for filename in args:
#         try:
#             with open(filename, "r") as f:
#                 output += f.read()
#         except FileNotFoundError:
#             output += f"cat: {filename}: No such file or directory"
#     return output
