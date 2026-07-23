import os
import subprocess
import sys, io
from pathlib import Path

# When running `python app/main.py` directly, make sure project root
# is on sys.path so top-level imports like `common` resolve.
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.systemInfo import PATH
from common.parser import Parser


def find_executable(command):
    for directory in PATH:
        executable_path = os.path.join(directory, command)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path
    return None


def not_found_handler(command):
    sys.stdout.write(f"{command}: command not found\n")


def run_external_command(args):
    subprocess.run(args)


def process_command(command):
    command = Parser(command)
    if command._cmdLet == "EXIT":
        sys.exit(0)

    if command:
        if command.isBuiltIn():
            handler = command.getBuiltInHandler()
            if handler:
                output = handler()
                if command.isOutputRedirected():
                    open(command.outArgs[0], "w").write(output)
                    return None
                return output
            # command.write_output(output)
                
        elif command.isExternal():
            handler = command.getExternalHandler()
            if handler:
                output = handler()
                if output.returncode != 0:
                    sys.stdout.write(output.stderr.decode())
                if command.isOutputRedirected():
                    open(command.outArgs[0], "w").write(output.stdout.decode())
                    return None
                else:
                    return output.stdout.decode()
        else:
            not_found_handler(command._cmdLet)
    else:
        not_found_handler(command._cmdLet)
        
    


def main():
    try:
        while True:
            command = input("$ ")
            commandOutput = process_command(command)
            if commandOutput:
                sys.stdout.write(commandOutput)
    except KeyboardInterrupt:
        sys.stdout.write("\n")
    except EOFError:
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()