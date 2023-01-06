from enum import Enum


class LexicalElement(Enum):
    KEYWORD = "keyword"
    IDENTIFIER = "identifier"
    SYMBOL = "symbol"
    INT_CONST = "integerConstant"
    STRING_CONST = "stringConstant"


class KeywordType(Enum):
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    INT = "int"
    BOOLEAN = "boolean"
    CHAR = "char"
    VOID = "void"
    VAR = "var"
    STATIC = "static"
    FIELD = "field"
    LET = "let"
    DO = "do"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    THIS = "this"


class SymbolType(Enum):
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_SQ_BRACE = "["
    RIGHT_SQ_BRACE = "]"
    DOT = "."
    COMMA = ","
    SEMI_COLON = ";"
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    AMPERSAND = "&"
    PIPE = "|"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    EQUAL = "="
    TILDE = "~"

