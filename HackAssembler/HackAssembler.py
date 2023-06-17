from asmparser import Parser
from Code import Code
from constants import InstructionType
import argparse
import os


if __name__ == "__main__":
    """usage:- python3 HackAssembler.py <path-to-asm file>

    Generates .hack file with same file name in the location of the .asm file.
    """
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("asm_file", help="Enter path of asm code file", default="")
    args = arg_parse.parse_args()
    asm_file = args.asm_file
    
    
    if not os.path.exists(asm_file) or not asm_file.endswith(".asm"):
        raise ValueError(f"Enter a valid asm file path, supplied path: {asm_file} does not exist")
    
    output_path, file_name = os.path.split(asm_file)
    parser = Parser(asm_file)
    opcode_gen = Code()
    
    with open(os.path.join(output_path, file_name.replace(".asm", ".hack")), "w") as file:
        while parser.hasMoreLines():
            parser.advance()
            instruction_type = parser.instructionType()
            
            if instruction_type == InstructionType.A_INSTRUCTION:
                symbol = parser.symbol()
        
                if not symbol.isdigit():
                    if parser.symbol_table.contains(symbol):
                        symbol = parser.symbol_table.getAddress(symbol)
                    else:
                        address = parser.available_ram
                        parser.available_ram = parser.available_ram + 1
                        parser.symbol_table.addEntry(symbol, address)
                        symbol = address
            
                bin_val = bin(int(symbol)).replace("0b", "")
                bin_val = f"{(16 - len(bin_val)) * '0'}{bin_val}\n" 
                file.write(bin_val)
                        
            elif instruction_type == InstructionType.C_INSTRUCTION:
                dest = opcode_gen.dest(parser.dest())
                comp = opcode_gen.comp(parser.comp())
                jump = opcode_gen.jump(parser.jump())
                file.write(f"111{comp}{dest}{jump}\n")
        
            
    