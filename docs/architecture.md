# Architecture

## Execution flow

    app.main (REPL)
            |
            v
    common.re_parser.Parser
      lexer -> splitter -> dispatcher -> output writer
                            |
                            v
                  builtin or external handler

The application entry point owns interactive input and prompt handling only.

The parser owns shell syntax, command boundaries, redirections, dispatch, and
output routing. It never invokes a host shell, so an executable name containing
spaces remains one value.

BuiltinHandler owns builtin behavior. Each handler accepts already-parsed
arguments and returns common.result.Result.

ExternalHandler owns PATH traversal and subprocess execution. This prevents
duplicated executable lookup logic.

## Design principles

- Single responsibility: REPL, lexer/parser, builtins, external lookup, and
  result transport each have one owner.
- DRY: Result, PATH lookup, and stream writing each have one implementation.
- KISS: parsing is a small character scanner, not a host-shell invocation.
- Open for extension: add a builtin by registering one function.

## Compatibility

The legacy common.parser.Parser import remains an alias of the active parser.
