"""Lexer, parser, and command dispatcher for the small shell.

This module intentionally does not use a host shell.  It converts the command
line into arguments itself, which keeps quoted executable names and literal
backslashes portable and prevents shell-injection side effects.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator

from commandHandlers.BuiltinHandler import BUILTINS
from commandHandlers.ExternalHandler import run_external_command
from common.result import Result


WORD = "WORD"
COMMAND_SEPARATORS = {"|", "&&", "||", ";", "&"}
REDIRECTIONS = {"1>", ">", "1>>", ">>", "2>", "2>>"}


@dataclass(frozen=True, slots=True)
class Token:
    """A lexical token with its shell-normalized value."""

    kind: str
    value: str


def tokenize(command: str) -> Iterator[tuple[str, str]]:
    """Yield tokens while applying shell quote and escape rules.

    Single quotes preserve every character literally. Double quotes and
    unquoted words consume a backslash plus its following character as one
    literal character. A trailing backslash remains literal rather than being
    silently dropped.
    """
    position = 0
    word: list[str] = []

    def flush_word() -> Token | None:
        if not word:
            return None
        token = Token(WORD, "".join(word))
        word.clear()
        return token

    while position < len(command):
        char = command[position]

        if char.isspace():
            token = flush_word()
            if token:
                yield token.kind, token.value
            position += 1
            continue

        redirection = next(
            (operator for operator in ("2>>", "1>>", "2>", "1>", ">>", ">")
             if command.startswith(operator, position)),
            None,
        )
        if redirection:
            token = flush_word()
            if token:
                yield token.kind, token.value
            yield redirection, redirection
            position += len(redirection)
            continue

        separator = next(
            (operator for operator in ("&&", "||", "|", ";", "&")
             if command.startswith(operator, position)),
            None,
        )
        if separator:
            token = flush_word()
            if token:
                yield token.kind, token.value
            yield separator, separator
            position += len(separator)
            continue

        if char == "'":
            # A backslash cannot escape a quote inside single quotes.
            closing_quote = command.find("'", position + 1)
            if closing_quote == -1:
                raise SyntaxError("unterminated single quote")
            word.append(command[position + 1:closing_quote])
            position = closing_quote + 1
            continue

        if char == '"':
            position += 1
            while position < len(command) and command[position] != '"':
                if command[position] == "\\" and position + 1 < len(command):
                    word.append(command[position + 1])
                    position += 2
                else:
                    word.append(command[position])
                    position += 1
            if position == len(command):
                raise SyntaxError("unterminated double quote")
            position += 1
            continue

        if char == "\\" and position + 1 < len(command):
            word.append(command[position + 1])
            position += 2
            continue

        word.append(char)
        position += 1

    token = flush_word()
    if token:
        yield token.kind, token.value


class Parser:
    """Parse and immediately execute a command line."""

    def __init__(self, command: str) -> None:
        self._command = command
        self._tokens = [Token(kind, value) for kind, value in tokenize(command)]
        self._commands = self._split_commands()
        self._execute_commands()

    def _split_commands(self) -> list[list[Token]]:
        """Split a token stream at command separators.

        Operators are retained only as boundaries for now; the shell's current
        stage runs each resulting command in order.
        """
        commands: list[list[Token]] = []
        current: list[Token] = []
        for token in self._tokens:
            if token.kind in COMMAND_SEPARATORS:
                if not current:
                    raise SyntaxError(f"unexpected operator: {token.value}")
                commands.append(current)
                current = []
            else:
                current.append(token)
        if current:
            commands.append(current)
        return commands

    def _execute_commands(self) -> None:
        """Run parsed commands and route their captured streams."""
        for tokens in self._commands:
            self._execute_one(tokens)

    def _execute_one(self, tokens: list[Token]) -> None:
        """Dispatch one command, separating arguments from redirection targets."""
        words: list[str] = []
        stdout_target: Token | None = None
        stderr_target: Token | None = None
        append_stdout = False
        append_stderr = False
        position = 0

        while position < len(tokens):
            token = tokens[position]
            if token.kind in REDIRECTIONS:
                if position + 1 == len(tokens) or tokens[position + 1].kind != WORD:
                    raise SyntaxError(f"redirection {token.value} requires a target")
                target = tokens[position + 1]
                if token.kind.startswith("2"):
                    stderr_target, append_stderr = target, token.kind == "2>>"
                else:
                    stdout_target, append_stdout = target, token.kind in {"1>>", ">>"}
                position += 2
            else:
                words.append(token.value)
                position += 1

        if not words:
            raise SyntaxError("missing command")

        result = self._dispatch(words[0], words[1:])
        self._write_stream(result.stdout, stdout_target, append_stdout, sys.stdout)
        self._write_stream(result.stderr, stderr_target, append_stderr, sys.stderr)

    @staticmethod
    def _dispatch(command: str, args: list[str]) -> Result:
        """Run a builtin when registered, otherwise resolve an external command."""
        if command in BUILTINS:
            return BUILTINS.get(command)(args)
        return run_external_command(command, args)

    @staticmethod
    def _write_stream(
        content: str,
        target: Token | None,
        append: bool,
        stream: object,
    ) -> None:
        """Write output to a redirection target or to the supplied text stream."""
        if target is None:
            if content:
                stream.write(content)  # type: ignore[attr-defined]
            return

        # Redirection creates or truncates its target even when the associated
        # command writes no bytes, such as echo text with stderr redirected.
        mode = "a" if append else "w"
        with open(target.value, mode, encoding="utf-8") as destination:
            destination.write(content)
