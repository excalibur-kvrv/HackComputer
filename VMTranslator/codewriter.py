from command import Command

class CodeWriter:
  def __init__(self, output_file=None, stream=None):
    if not (output_file or stream):
      raise ValueError("Output file or a write stream must be provided.")
    
    if output_file:
      self.stream = open(output_file, "w")
    else:
      if stream.mode != "w":
        raise ValueError(f"File opened not opened in 'w' mode instead is open in {stream.mode}")
      
      self.stream = stream
  
    self.arithmetic_fns = {
      "add": self.__write_add,
      "sub": self.__write_sub,
      "neg": self.__write_neg,
      "eq": self.__write_eq,
      "gt": self.__write_gt,
      "lt": self.__write_lt,
      "and": self.__write_and,
      "or": self.__write_or,
      "not": self.__write_not
    }
  
  def __write_instructions(self, instructions):
    for instruction in instructions:
      self.stream.write(f"{instruction}\n")
  
  def __write_and(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "M=D&M"
    ]
    self.__write_instructions(instructions)
  
  def __write_or(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "M=D|M"
    ]
    self.__write_instructions(instructions)
  
  def __write_not(self):
    instructions = [
      "@SP",
      "A=M-1",
      "M=!M"
    ]
    self.__write_instructions(instructions)
  
  def __write_add(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "M=M+D"
    ]
    self.__write_instructions(instructions)
    
  def __write_sub(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M-1",
      "D=M",
      "A=A+1",
      "D=D-M",
      "A=A-1",
      "M=D"
    ]
    self.__write_instructions(instructions)
    
  def __write_neg(self):
    instructions = [
      "@SP",
      "A=M-1",
      "M=-M"
    ]
    self.__write_instructions(instructions)
  
  def __write_eq(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "D=M-D",
      "@EQUAL",
      "D;JEQ",
      "@NOTEQUAL",
      "0;JMP",
      "(EQUAL)",
      " @SP",
      " A=M-1",
      " M=1",
      " @EQUALEND",
      " 0;JMP",
      "(NOTEQUAL)",
      " @SP",
      " A=M-1",
      " M=0",
      " @EQUALEND",
      " 0;JMP",
      "(EQUALEND)"
    ]
    self.__write_instructions(instructions)
  
  def __write_gt(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "D=D-M",
      "@GREATERTHAN",
      "D;JLT",
      "@NOTGREATERTHAN",
      "0;JMP",
      "(GREATERTHAN)",
      " @SP",
      " A=M-1",
      " M=1",
      " @GREATERTHANEND",
      " 0;JMP",
      "(NOTGREATERTHAN)",
      " @SP",
      " A=M-1",
      " M=0",
      " @GREATERTHANEND",
      " 0;JMP",
      "(GREATERTHANEND)"
    ]
    self.__write_instructions(instructions)
  
  def __write_lt(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "D=D-M",
      "@LESSTHAN",
      "D;JGT",
      "@NOTLESSTHAN",
      "0;JMP",
      "(LESSTHAN)",
      " @SP",
      " A=M-1",
      " M=1",
      " @LESSTHANEND",
      " 0;JMP",
      "(NOTLESSTHAN)",
      " @SP",
      " A=M-1",
      " M=0",
      " @LESSTHANEND",
      " 0;JMP",
      "(LESSTHANEND)"
    ]
    self.__write_instructions(instructions)
    
  def writeArithmetic(self, command: str):
    fn = self.arithmetic_fns[command]
    fn()
  
  def writePushPop(self, command: Command, segment: str, index: int):
    pass
  
  def close(self):
    self.stream.close()
