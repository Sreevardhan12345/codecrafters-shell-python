import re, os, subprocess, sys

from commandHandlers.BuiltinHandler import BUILTINS as BUILTIN_COMMANDS


class Result:
    def __init__(self, returncode, output=None, error=None):
        self.returncode = returncode
        self.output = output
        self.error = error


TOKEN_REGEX = re.compile(
    r"""
(?P<SPACE>\s+)

|(?P<APPEND_ERR>2>>)
|(?P<REDIR_ERR>2>)
|(?P<APPEND>>>|1>>)
|(?P<HEREDOC><<)
|(?P<REDIR_OUT>>|1>)
|(?P<REDIR_IN><)

|(?P<PIPE>\|)
|(?P<AND>&&)
|(?P<OR>\|\|)
|(?P<SEMI>;)
|(?P<BACKGROUND>&)

|(?P<DQSTRING>"(?:\\.|[^"\\])*")
|(?P<SQSTRING>'(?:\\.|[^'])*')

|(?P<WORD>[^\s<>&|;]+)
""",
    re.VERBOSE,
)


def tokenize(command):
    pos = 0

    while pos < len(command):
        m = TOKEN_REGEX.match(command, pos)

        if not m:
            raise SyntaxError(command[pos:])

        if m.lastgroup != "SPACE":
            yield m.lastgroup, m.group()

        pos = m.end()


class Parser:
    def __init__(self, command):
        self._command = command
        self._tokens = list(tokenize(command))
        self._pipeline = []
        self._build_pipeline()
        self._exec_pipeline()

    def _build_pipeline(self):
        current_cmd = []
        for token_type, token_value in self._tokens:
            if token_type in ["PIPE", "AND", "OR", "SEMI", "BACKGROUND"]:
                if current_cmd:
                    self._pipeline.append((current_cmd, token_type))
                    current_cmd = []
                else:
                    raise SyntaxError(
                        f"Unexpected {token_value} at position {self._tokens.index((token_type, token_value))}"
                    )
            else:
                current_cmd.append((token_type, token_value))

        if current_cmd:
            self._pipeline.append((current_cmd, None))

    def _exec_pipeline(self):

        def process_double_quoted_string(s):
            # Remove the surrounding double quotes
            s = s[1:-1]
            # Replace escaped characters
            return re.sub(r'\\(.)', r'\1', s)
        def process_single_quoted_string(s):
            # Remove the surrounding single quotes
            s = s[1:-1]
            # Replace escaped characters
            return re.sub(r'\\(.)', r'\1', s)
        for task, operator in self._pipeline:
            _, command = task.pop(0)
            input_args = []
            token_type, token_value = task.pop(0) if task else (None, None)
            while token_type in ["WORD", "DQSTRING", "SQSTRING"]:
                if token_type == "DQSTRING":
                    input_args.append(process_double_quoted_string(token_value))    
                elif token_type == "SQSTRING":
                    input_args.append(process_single_quoted_string(token_value))
                input_args.append(token_value)
                token_type, token_value = task.pop(0) if task else (None, None)

            result = self.process_task(command, input_args)
            outputProcessed = False
            errorProcessed = False
            while token_type in [
                "REDIR_OUT",
                "REDIR_ERR",
                "APPEND",
                "APPEND_ERR",
                "HEREDOC",
            ]:
                redir_type = token_type
                _, redir_target = task.pop(0)
                if redir_type == "REDIR_OUT":
                    outputProcessed = True
                    self.redirect_output(result.output, redir_target)
                elif redir_type == "REDIR_ERR":
                    errorProcessed = True
                    self.redirect_output(result.error, redir_target)
                elif redir_type == "APPEND":
                    outputProcessed = True
                    self.append_output(result.output, redir_target)
                elif redir_type == "APPEND_ERR":
                    errorProcessed = True
                    self.append_output(result.error, redir_target)
                token_type, token_value = task.pop(0) if task else (None, None)

            if not outputProcessed:
                sys.stdout.write(result.output if result.output else "")
            if not errorProcessed:
                sys.stderr.write(result.error if result.error else "")

    def redirect_output(self, output, target):
        with open(target, "w") as f:
            if output:
                f.write(output)

    def append_output(self, output, target):
        with open(target, "a") as f:
            if output:
                f.write(output)

    def process_task(self, command, args):
        if command.upper() in BUILTIN_COMMANDS:
            handler = BUILTIN_COMMANDS.get(command.upper())
            result = handler(args)
            if result is None:
                return Result(0)
            return Result(result.returncode, output=result.stdout, error=result.stderr)
        else:
            for directory in os.environ.get("PATH", "").split(os.pathsep):
                executable_path = os.path.join(directory, command)
                if os.path.isfile(executable_path) and os.access(
                    executable_path, os.X_OK
                ):
                    result = subprocess.run(
                        [command] + args,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    return Result(
                        result.returncode, output=result.stdout, error=result.stderr
                    )
            return Result(1, error=f"{command}: command not found\n")
