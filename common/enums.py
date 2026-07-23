from enum import Enum

class COMMAND_TYPE(Enum):
    INVALID = 0
    BUILTIN = 1
    OTHER = 2
    
class STD_TYPE(Enum):
    STDIN = 0
    STDOUT = 1
    STDERR = 2