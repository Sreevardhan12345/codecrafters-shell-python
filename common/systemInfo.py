""" environment access helpers.

The functions read the environment when called so a test can safely replace
PATH or HOME after this module has been imported.
"""

import os


def path_directories() -> list[str]:
    """Return PATH entries, ignoring empty entries."""
    return [directory for directory in os.environ.get("PATH", "").split(os.pathsep) if directory]


def home_directory() -> str:
    """Return the user's home directory, or an empty string when unavailable."""
    return os.environ.get("HOME", "")


# Compatibility exports for the older modules.
PATH = path_directories()
HOME = home_directory()
