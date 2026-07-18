import subprocess
import sys, os

BUILTINS = ["echo", "type", "exit", "pwd", "cd"]
PATH = os.environ.get("PATH", "").split(os.pathsep)
HOME = os.environ.get("HOME", "")

def exit_shell():
    sys.exit(0)

def echo_shell(args):
    sys.stdout.write(" ".join(args) + "\n")

def pwd_shell():
    sys.stdout.write(os.getcwd() + "\n")

def find_executable(command):
    for directory in PATH:
        executable_path = os.path.join(directory, command)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path
    return None

def cd_shell(args):
    if len(args) > 0:
        if args[0] == "~":
            home_directory = os.path.expanduser("~")
            os.chdir(home_directory)
        try:
            os.chdir(args[0])
        except FileNotFoundError:
            sys.stdout.write(f"cd: {args[0]}: No such file or directory\n")
    else:
        sys.stdout.write("cd: missing operand\n")
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

def commandProcessor(command):
    cmdLets =command.split()
    if len(cmdLets) == 0:
        return
    elif cmdLets[0] == "exit":
        exit_shell()
    elif cmdLets[0] == "echo":
        echo_shell(cmdLets[1:])
    elif cmdLets[0] == "type":
        type_shell(cmdLets[1:])
    elif cmdLets[0] == "pwd":
        pwd_shell()
    elif cmdLets[0] == "cd":
        cd_shell(cmdLets[1:])
    else:
        executable = find_executable(cmdLets[0])
        if executable:
            subprocess.run(cmdLets)
        else:
            not_found_handler(cmdLets[0])

def main():
    while( True):
        command = input("$ ")
        commandProcessor(command)


if __name__ == "__main__":
    main()
