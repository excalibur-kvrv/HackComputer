from vmparser import Parser
from codewriter import CodeWriter
from command import Command
import argparse
import os


if __name__ == "__main__":
  arg_parse = argparse.ArgumentParser()
  arg_parse.add_argument("vm_file", help="Enter path of vm code file")
  args = arg_parse.parse_args()
  
  vm_file = args.vm_file
  path, file_name = os.path.split(vm_file)
  output_file = os.path.join(path, file_name.replace("vm", "asm"))
  
  if not os.path.exists(vm_file):
    raise ValueError("Enter a valid vm file path")
  
  parser = Parser(input_file=vm_file)
  code_writer = CodeWriter(output_file=output_file)
  
  try:
    while parser.hasMoreCommands():
      parser.advance()
      command_type, arg1, arg2 = parser.commandType(), parser.arg1(), parser.arg2()

      if command_type == Command.C_ARITHMETIC:
        code_writer.writeArithmetic(arg1)
      elif command_type == Command.C_POP or command_type == Command.C_PUSH:
        code_writer.writePushPop(command_type, arg1, arg2)

  finally:
    code_writer.close()