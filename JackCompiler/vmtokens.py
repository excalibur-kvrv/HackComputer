from enum import Enum


class VariableType(Enum):
    STATIC = "static"
    FIELD = "field"
    ARG = "argument"
    VAR = "local"
    NONE = "none"


class VirtualMemorySegmentType(Enum):
    CONSTANT = "constant"
    ARGUMENT = "argument"
    LOCAL = "local"
    STATIC = "static"
    THIS = "this"
    THAT = "that"
    POINTER = "pointer"
    TEMP = "temp"


class CommandType(Enum):
    ADD = "add"
    SUB = "sub"
    NEG = "neg"
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    AND = "and"
    OR = "or"
    NOT = "not"
