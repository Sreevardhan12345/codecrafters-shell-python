"""Interactive entry point for the shell."""

import sys
from pathlib import Path

# Support direct execution as well as module execution.
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from commandHandlers.BuiltinHandler import BUILTINS
from common.re_parser import Parser


PROMPT = "$ "


def _complete_builtin(text: str, state: int) -> str | None:
    """Return a unique builtin completion for the word at the cursor.

    Readline calls the function repeatedly with increasing state values. A
    trailing space is intentional: after a unique command match, the next Tab
    should complete an argument rather than keep extending the command name.
    """
    matches = [name.lower() for name in BUILTINS if name.lower().startswith(text.lower())]
    if len(matches) != 1 or state != 0:
        return None
    return matches[0] + " "


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
