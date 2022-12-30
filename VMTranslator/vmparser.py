from command import Command
from constants import ARITHMETIC_LOGICAL_COMMANDS

class Parser:
  def __init__(self, input_file: str = None, stream=None):
    if not (input_file or stream):
      raise ValueError("Either input file or a read stream must be provided.")
    
    if input_file:
      file_content = open(input_file)
    else:
      file_content = stream
    
    if file_content.mode != "r":
      raise ValueError(f"Input file stream expected to be in 'r' mode but was in {stream.mode}")

    self.lines = file_content.readlines()
    self.line_count = len(self.lines)
    self.current_line = 0
     
    file_content.close()
    
  def hasMoreCommands(self) -> bool:
    return self.current_line != self.line_count
  
  def advance(self):
    if not self.hasMoreCommands():
      return
    
    self.command = None
    self.argument_1 = None
    self.argument_2 = None

    line = self.lines[self.current_line].strip()
    tokens = line.split(" ")
    
    if len(tokens) > 0:
      command = tokens[0]
      if command == "push":
        self.__create_command(Command.C_PUSH, tokens)
      elif command == "pop":
        self.__create_command(Command.C_POP, tokens)
      elif command in ARITHMETIC_LOGICAL_COMMANDS:
        self.command = Command.C_ARITHMETIC
        self.argument_1 = command
      elif command == "label":
        self.command = Command.C_LABEL
        self.__create_command(Command.C_LABEL, tokens)
      elif command == "goto":
        self.command = Command.C_GOTO
        self.__create_command(Command.C_GOTO, tokens)
      elif command == "if-goto":
        self.command = Command.C_IF
        self.__create_command(Command.C_IF, tokens)
      elif command == "call":
        self.command = Command.C_CALL
        self.__create_command(Command.C_CALL, tokens)
      elif command == "function":
        self.command = Command.C_FUNCTION
        self.__create_command(Command.C_FUNCTION, tokens)
      elif command == "return":
        self.command = Command.C_RETURN
      else:
        self.current_line += 1
        return self.advance()
  
    self.current_line += 1
  
  def __create_command(self, command: Command, tokens: list):
    self.command = command
    self.argument_1 = tokens[1]
    
    if len(tokens) >= 3:
      self.argument_2 = tokens[2]
  
  def commandType(self) -> Command:
    return self.command
  
  def arg1(self) -> str:
    return self.argument_1
  
  def arg2(self) -> int:
    return self.argument_2