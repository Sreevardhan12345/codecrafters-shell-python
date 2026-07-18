import os
import subprocess
import sys

BUILTINS = {"echo", "type", "exit", "pwd", "cd"}
PATH = os.environ.get("PATH", "").split(os.pathsep)
HOME = os.environ.get("HOME", "")


def exit_shell():
    sys.exit(0)


def parse_args(command):
    args = []
    current = []
    quote_char = None
    escaped = False

    for char in command:
        if escaped:
            current.append(char)
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if quote_char:
            if char == quote_char:
                quote_char = None
            else:
                current.append(char)
            continue

        if char in ("'", '"'):
            quote_char = char
        elif char.isspace():
            if current:
                args.append("".join(current))
                current = []
        else:
            current.append(char)

    if escaped:
        current.append("\\")

    if current:
        args.append("".join(current))

    return args


def echo_shell(command):
    args = parse_args(command)
    for arg in args:
        sys.stdout.write(arg + " ")
    sys.stdout.write("\n")


def pwd_shell():
    sys.stdout.write(os.getcwd() + "\n")


def find_executable(command):
    for directory in PATH:
        executable_path = os.path.join(directory, command)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path
    return None


def cd_shell(args):
    if not args:
        sys.stdout.write("cd: missing operand\n")
        return

    target = HOME if args[0] == "~" else args[0]
    try:
        os.chdir(target)
    except FileNotFoundError:
        sys.stdout.write(f"cd: {args[0]}: No such file or directory\n")


def type_shell(args):
    if not args:
        sys.stdout.write("type: missing operand\n")
        return

    target = args[0]
    if target in BUILTINS:
        sys.stdout.write(f"{target} is a shell builtin\n")
        return

    executable = find_executable(target)
    if executable:
        sys.stdout.write(f"{target} is {executable}\n")
    else:
        sys.stdout.write(f"{target}: not found\n")


def not_found_handler(command):
    sys.stdout.write(f"{command}: command not found\n")


def run_external_command(args):
    subprocess.run(args)


def process_command(command):
    args = parse_args(command)
    if not args:
        return

    cmd = args[0]
    rest = args[1:]

    if cmd == "exit":
        exit_shell()
    elif cmd == "echo":
        echo_shell(rest)
    elif cmd == "type":
        type_shell(rest)
    elif cmd == "pwd":
        pwd_shell()
    elif cmd == "cd":
        cd_shell(rest)
    else:
        if find_executable(cmd):
            run_external_command(args)
        else:
            not_found_handler(cmd)


def main():
    try:
        while True:
            command = input("$ ")
            process_command(command)
    except KeyboardInterrupt:
        sys.stdout.write("\n")
    except EOFError:
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
