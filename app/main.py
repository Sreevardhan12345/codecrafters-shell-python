"""Interactive entry point for the shell."""


import sys
from pathlib import Path

# Support direct execution as well as module execution.
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.re_parser import Parser
from common.completions import _configure_completion, PROMPT


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
