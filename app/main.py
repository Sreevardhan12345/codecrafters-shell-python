from asyncio import subprocess
import sys, os

BUILTINS = ["echo", "type", "exit"]
PATH = os.environ.get("PATH", "").split(os.pathsep)

def exit_shell():
    sys.exit(0)

def echo_shell(args):
    sys.stdout.write(" ".join(args) + "\n")

def find_executable(command):
    for directory in PATH:
        executable_path = os.path.join(directory, command)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path
    return None

def type_shell(args):
    if len(args) > 0:
        if args[0] in BUILTINS:
            sys.stdout.write(f"{args[0]} is a shell builtin\n")
        else:
            executable = find_executable(args[0])
            if executable:
                sys.stdout.write(f"{args[0]} is {executable}\n")
            else:
                sys.stdout.write(f"{args[0]}: not found\n")
    else:
        sys.stdout.write("type: missing operand\n")

def not_found_handler(command):
    sys.stdout.write(f"{command}: command not found\n")

def main():
    while( True):
        command = input("$ ")
        if command == "exit":
            exit_shell()
        elif command.startswith("echo "):
            echo_shell(command[5:].split())
        elif command.startswith("type "):
            type_shell(command[5:].split())
        else:
            executable = find_executable(command)
            if executable:
                subprocess.run([executable] + command.split()[1:])
            else:
                not_found_handler(command)


if __name__ == "__main__":
    main()
