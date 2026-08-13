"""Legacy command classifications kept for import compatibility."""

from enum import Enum


class CommandType(Enum):
    """Classify a command after lookup."""

    INVALID = 0
    BUILTIN = 1
    EXTERNAL = 2


COMMAND_TYPE = CommandType
