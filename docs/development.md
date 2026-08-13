# Development guide

Run the shell locally:

    ./your_program.sh

Useful smoke checks:

    python -m py_compile app/main.py common/*.py commandHandlers/*.py
    python -m app.main

## Adding a builtin

1. Add one function to commandHandlers/BuiltinHandler.py.
2. Register it with BUILTINS.register.
3. Accept a list of strings and return Result.
4. Add quote and error-path coverage.

Do not parse command strings in handlers. They receive final argument values,
which prevents quote handling from being reimplemented inconsistently.
