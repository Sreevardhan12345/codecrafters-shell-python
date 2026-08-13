"""External command discovery and execution."""

import os
import subprocess

from common.result import Result
from common.systemInfo import path_directories


def find_executable(command: str) -> str | None:
    """Find an executable in PATH without invoking a shell.

    Joining paths directly is important: commands containing spaces must remain
    one executable name rather than being split by a shell.
    """
    for directory in path_directories():
        candidate = os.path.join(directory, command)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def run_external_command(command: str, args: list[str]) -> Result:
    """Run one already-tokenized executable and capture its output."""
    executable = find_executable(command)
    if executable is None:
        return Result(1, stderr=f"{command}: command not found\n")

    completed = subprocess.run(
        [command, *args],
        executable=executable,
        capture_output=True,
        text=True,
        check=False,
    )
    return Result(completed.returncode, completed.stdout, completed.stderr)
