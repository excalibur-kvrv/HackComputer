from vmparser import Parser
from codewriter import CodeWriter
from command import Command
import argparse
import os


if __name__ == "__main__":
  """usage:- python3 VMTranslator.py <path-to-vm file>

  Generates a .asm file with same file name in location of .vm file
  """
  arg_parse = argparse.ArgumentParser()
  arg_parse.add_argument("vm_file", help="Enter path of vm code file", default="")
  args = arg_parse.parse_args()
  
  vm_file = args.vm_file
  files_to_translate = []
  
  if os.path.isdir(vm_file):
    if vm_file.endswith(os.path.sep):
      vm_file = vm_file[:-1]
    files_to_translate = [ os.path.join(vm_file, file) for file in os.listdir(vm_file) if file.endswith("vm") ]
  else:
    files_to_translate.append(vm_file)

  path, file_name = os.path.split(vm_file)
  output_file = os.path.join(path, file_name.replace("vm", "asm") if file_name.endswith("vm") else os.path.join(file_name, f"{file_name}.asm"))
  
  if not os.path.exists(vm_file):
    raise ValueError("Enter a valid vm file path")
  
  code_writer = CodeWriter(output_file=output_file)
  
  for file in files_to_translate:
    parser = Parser(input_file=file)
    path, file_name = os.path.split(file)
    try:
      code_writer.setFileName(file_name)
      while parser.hasMoreCommands():
        parser.advance()
        command_type, arg1, arg2 = parser.commandType(), parser.arg1(), parser.arg2()

        if command_type == Command.C_ARITHMETIC:
          code_writer.writeArithmetic(arg1)
        elif command_type == Command.C_POP or command_type == Command.C_PUSH:
          code_writer.writePushPop(command_type, arg1, arg2)
        elif command_type == Command.C_LABEL:
          code_writer.writeLabel(arg1)
        elif command_type == Command.C_GOTO:
          code_writer.writeGoto(arg1)
        elif command_type == Command.C_IF:
          code_writer.writeIf(arg1)
        elif command_type == Command.C_CALL:
          code_writer.writeCall(arg1, int(arg2))
        elif command_type == Command.C_FUNCTION:
          code_writer.writeFunction(arg1, int(arg2))
        elif command_type == Command.C_RETURN:
          code_writer.writeReturn()
    except Exception as e:
      print(e)
  code_writer.close()
