"""Value object returned by every command handler."""

from dataclasses import dataclass


@dataclass(slots=True)
class Result:
    """The observable outcome of a shell command."""

    returncode: int
    stdout: str = ""
    stderr: str = ""
