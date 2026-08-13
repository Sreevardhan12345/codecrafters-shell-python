# Parsing and quoting rules

The lexer produces final argument values. The executor never splits values
again, which is essential for executable names and paths containing spaces.

| Input form | Result |
| --- | --- |
| plain words | two arguments |
| single-quoted text | one literal argument |
| double-quoted text | one argument; escaped characters are literal |
| adjacent quoted and plain text | one concatenated argument |
| backslash followed by a space | literal space in an unquoted word |
| two backslashes | one literal backslash |
| single-quoted backslash-77 | literal backslash-77 |

An unmatched single or double quote raises SyntaxError. A trailing unquoted
backslash remains literal; it is never discarded.

## Redirection

The parser recognises >, >>, 1>, 1>>, 2>, and 2>>. The next token must be a parsed word, so quoted file names are supported. Redirected output uses UTF-8.
