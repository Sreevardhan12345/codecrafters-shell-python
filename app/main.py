"""Interactive entry point for the shell."""

import os
import sys
from pathlib import Path

# Support direct execution as well as module execution.
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from commandHandlers.BuiltinHandler import BUILTINS
from common.re_parser import Parser
from common.systemInfo import path_directories


PROMPT = "$ "


def _complete_builtin(text: str, state: int) -> str | None:
    """Return a unique builtin or PATH executable completion.

    Readline calls the function repeatedly with increasing state values. A
    A trailing space is intentional after any unique command match: the next
    Tab should complete an argument rather than extend the command name.
    """
    matches = _command_completions(text)
    if len(matches) != 1 or state != 0:
        return None
    return matches[0]


def _command_completions(prefix: str) -> list[str]:
    """Find unique builtin and executable names beginning with prefix.

    PATH may contain missing, inaccessible, or non-directory entries. Each
    entry is isolated so a filesystem error never breaks interactive input.
    """
    normalized_prefix = prefix.lower()
    matches = {
        name.lower() + " "
        for name in BUILTINS
        if name.lower().startswith(normalized_prefix)
    }

    for directory in path_directories():
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if (
                        entry.name.lower().startswith(normalized_prefix)
                        and entry.is_file()
                        and os.access(entry.path, os.X_OK)
                    ):
                        matches.add(entry.name + " ")
        except OSError:
            # A PATH entry can disappear or be unreadable after process start.
            continue

    return sorted(matches)


def _configure_completion() -> None:
    """Enable Tab completion"""
    try:
        import readline
    except ImportError:
        # The non-interactive fallback still works on platforms without readline.
        return

    readline.set_completer(_complete_builtin)
    readline.parse_and_bind("tab: complete")


def main() -> None:
    """Run the REPL until EOF, Ctrl-C, or the exit builtin."""
    _configure_completion()
    while True:
        try:
            command = input(PROMPT)
        except EOFError:
            sys.stdout.write("\n")
            return
        except KeyboardInterrupt:
            sys.stdout.write("\n")
            continue

        # Whitespace-only input has no command and should not invoke parsing.
        if command.strip():
            Parser(command)


if __name__ == "__main__":
    main()
