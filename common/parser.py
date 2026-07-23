import os, subprocess
from functools import partial
import sys

from common.enums import COMMAND_TYPE
from commandHandlers.BuiltinHandler import BUILTINS
from commandHandlers.ExternalHandler import PATH


class Parser:
    def __init__(self, command):
        self._command = command
        self._cmdLet = None
        self._cmdType = COMMAND_TYPE.INVALID
        self.inArgs = []
        self.outArgs = []
        self.errArgs = []
        self._setArgs()

    def __str__(self):
        return f"{self._cmdType.name} - {self._cmdLet} - object"

    def __repr__(self):
        return f"{self._cmdType.name} - {self._cmdLet} - object"

    def _find_executable(self,command):
        for directory in PATH:
            executable_path = os.path.join(directory, command)
            if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
                return executable_path
        return None

    def _parseCommandType(self):
        if self._cmdLet.upper() in BUILTINS:
            self._cmdType = COMMAND_TYPE.BUILTIN
        else:
            executable = self._find_executable(self._cmdLet)
            self._cmdType = COMMAND_TYPE.OTHER if executable else COMMAND_TYPE.INVALID

    def _parse(self, command: str) -> list:
        index, length = 0, len(command)
        result = []
        arg = ""

        while index < length:
            if command[index].isalnum() or command[index] in [
                "-",
                "_",
                ".",
                "/",
                "~",
                ">",
            ]:
                arg += command[index]
                index += 1
                continue

            if command[index] == " ":
                if arg:
                    result.append(arg)
                    arg = ""
                index += 1
                continue

            if command[index] == "\\":
                index += 1
                if index < length:
                    arg += command[index]
                    index += 1
                continue

            if command[index] in ['"', "'"]:
                quote_char = command[index]
                index += 1
                if quote_char == "'":
                    while index < length and command[index] != quote_char:
                        arg += command[index]
                        index += 1
                else:
                    while index < length:
                        if command[index] == "\\":
                            arg += command[index + 1]
                            index += 2
                            continue
                        if command[index] != quote_char:
                            arg += command[index]
                            index += 1
                        else:
                            break

            index += 1
        if arg:
            result.append(arg)
        if result:
            return result[0], result[1:]

    def _setArgs(self):
        self._cmdLet, args = self._parse(self._command)
        self._parseCommandType()
        destRef = self.inArgs
        for arg in args:
            if arg in "1>":
                destRef = self.outArgs
                continue
            if arg in "2>":
                destRef = self.errArgs
                continue
            destRef.append(arg)
                
    def isBuiltIn(self):
        return self._cmdType == COMMAND_TYPE.BUILTIN
    
    def isExternal(self):
        return self._cmdType == COMMAND_TYPE.OTHER
    
    def getBuiltInHandler(self):
        if self.isBuiltIn():
            return partial(BUILTINS.get(self._cmdLet.upper()),self.inArgs)
        
    def getExternalHandler(self):
        if self.isExternal():
            executable = self._find_executable(self._cmdLet)
            if executable:
                return partial(subprocess.run, [self._cmdLet] + self.inArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def isOutputRedirected(self):
        return len(self.outArgs) > 0
    
    def isErrorRedirected(self):
        return len(self.errArgs) > 0