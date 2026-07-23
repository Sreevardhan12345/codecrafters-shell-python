from functools import partial
import os
import subprocess
import sys
from pathlib import Path

# When running `python app/main.py` directly, make sure project root
# is on sys.path so top-level imports like `common` resolve.
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.systemInfo import PATH
from common.parser import Parser
from common.result import Result


def find_executable(command):
    for directory in PATH:
        executable_path = os.path.join(directory, command)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path
    return None


def not_found_handler(command):
    return Result(1, stderr=f"{command}: command not found\n")  


def run_external_command(args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
    result = Result(result.returncode, stdout=result.stdout, stderr=result.stderr)
    return result


def process_command(command):
    command = Parser(command)
    if command._cmdLet == "EXIT":
        sys.exit(0)

    if command:
        handler = None
        
        if command.isOutputRedirected():
            open(command.outArgs[0], "w").close()
        if command.isErrorRedirected():
            open(command.errArgs[0], "w").close()
            
        if command.isBuiltIn():
            handler = command.getBuiltInHandler()
        elif command.isExternal():
            handler = command.getExternalHandler()
        else:
            handler = partial(not_found_handler, command._cmdLet)

        if handler:
            output = handler()
            if output:
                if output.stdout:
                    output_message = output.stdout if isinstance(output.stdout, str) else output.stdout.decode()
                    if output_message:
                        if command.isOutputRedirected():
                            open(command.outArgs[0], "w").write(output_message)
                        else:
                            sys.stdout.write(output_message)
                if output.stderr:
                    error_message = output.stderr if isinstance(output.stderr, str) else output.stderr.decode()
                    if error_message :
                        if command.isErrorRedirected():
                            open(command.errArgs[0], "w").write(error_message)
                        else:
                            sys.stderr.write(error_message)
    else:
        sys.stderr.write(f"{command._cmdLet}: command not found\n")


def main():
    try:
        while True:
            command = input("$ ")
            if command.strip() == "":
                continue
            process_command(command)
    except KeyboardInterrupt:
        sys.stdout.write("\n")
    except EOFError:
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
