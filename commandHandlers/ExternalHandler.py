import os, sys, subprocess
from common.registry import Registry
from common.systemInfo import PATH

EXTERNAL = Registry("External Commands")


@EXTERNAL.register("NOT FOUND")
def not_found_handler(command):
    sys.stdout.write(f"{command}: command not found")


@EXTERNAL.register("FIND")
def find_executable(command):
    for directory in PATH:
        executable_path = os.path.join(directory, command)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path
    return None


@EXTERNAL.register("RUN")
def run_external_command(args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
