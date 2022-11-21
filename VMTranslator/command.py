from enum import Enum

class Command(Enum):
  C_ARITHMETIC = "c_arithmetic"
  C_PUSH = "c_push"
  C_POP = "c_pop"
  C_LABEL = "c_label"
  C_GOTO = "c_goto"
  C_IF = "c_if"
  C_FUNCTION = "c_function"
  C_RETURN = "c_return"
  C_CALL = "c_call"
