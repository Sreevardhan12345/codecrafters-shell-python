"""module for readline completion of commands and filenames."""
import os
import subprocess

from common.systemInfo import path_directories
from commandHandlers.BuiltinHandler import BUILTINS, COMPLETERS


PROMPT = "$ "
_completion_matches: list[str] = []


def _complete_builtin(text: str, state: int) -> str | None:
    """Return command or filename candidates for readline.

    Readline calls the function repeatedly with increasing state values. A
    A candidate carries a trailing space so the next Tab completes an argument.
    At the command position, candidates come from builtins and PATH. For a
    command with a registered completer, its script supplies argument
    candidates; otherwise regular files are used.
    """
    import readline

    global _completion_matches

    if state == 0:
        buffer = readline.get_line_buffer()
        os.environ["COMP_LINE"] = buffer
        os.environ["COMP_POINT"] = str(readline.get_endidx())
        preceding_text = buffer[: readline.get_begidx()]
        command_words = preceding_text.split()
        command = command_words[0] if command_words else None
        if command in COMPLETERS:
            previous_word = command_words[-1] if len(command_words) > 1 else ""
            _completion_matches = _completer_completions(
                COMPLETERS[command], command, text, previous_word
            )
            # A broken completer should not disable the shell's normal Tab
            # behavior for that command.
            if not _completion_matches:
                _completion_matches = _filename_completions(text)
        elif preceding_text.strip():
            _completion_matches = _filename_completions(text)
        else:
            _completion_matches = _command_completions(text)

    if state >= len(_completion_matches):
        return None
    return _completion_matches[state]


def _completer_completions(
    script: str, command: str, current_word: str, previous_word: str
) -> list[str]:
    """Run a completer with the command, current word, and previous word."""
    try:
        completed = subprocess.run(
            [script, command, current_word, previous_word],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []

    return [f"{line} " for line in completed.stdout.splitlines() if line]


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


def _filename_completions(prefix: str) -> list[str]:
    """Return matching files for a current-directory or path-qualified prefix.

    The readline configuration treats whitespace as the only word separator,
    so a filename containing punctuation such as a hyphen remains one
    completion target. When a slash is present, the final slash separates the
    directory to scan from the filename prefix to match. Filesystem errors are
    ignored so an absent or unreadable directory does not break the shell.
    """
    directory_prefix, separator, filename_prefix = prefix.rpartition("/")
    directory = directory_prefix or ("/" if separator else ".")
    path_prefix = f"{directory_prefix}/" if separator else ""

    try:
        matches = [
            path_prefix + entry.name + ("/" if entry.is_dir() else " ")
            for entry in os.scandir(directory)
            if entry.name.startswith(filename_prefix)
            and (entry.is_file() or entry.is_dir())
        ]
    except OSError:
        return []
    return sorted(matches)


def _configure_completion() -> None:
    """Enable Tab completion"""
    try:
        import readline
    except ImportError:
        # The non-interactive fallback still works on platforms without readline.
        return

    readline.set_completer(_complete_builtin)
    # Filename prefixes can contain punctuation; whitespace is the only
    # separator for this shell's simple argument completion.
    readline.set_completer_delims(" \t\n")
    readline.parse_and_bind("tab: complete")