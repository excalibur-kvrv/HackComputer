from constants import InstructionType
from SymbolTable import SymbolTable
import os
import re


C_INS_PATTERN = "(?:([ADM]{0,3})=)?([01ADM\-+!&|]{1,3})(?:;(JGT|JEQ|JGE|JLT|JNE|JLE|JMP))?"


class Parser:
    def __init__(self, input_file: str):
        self.__file_contents = []
        self.current_line_no = 0
        self.parsed_line = ""
        self.completed = False
        self.symbol_table = SymbolTable()
        self.available_ram = 16
        
        if not os.path.isfile(input_file):
            raise ValueError(f"Supplied path: {input_file}, is not a file")
        
        with open(input_file) as file:
            self.__file_contents = file.readlines()
        
        self.__first_pass()
    
    def __first_pass(self):
        instruction_count = 0
        labels_found = 0
        
        for line in self.__file_contents:
            current_line = self.__strip_comments(line).strip()
            
            if current_line:
                self.parsed_line = current_line
                instruction_count += 1
                
                if self.instructionType() == InstructionType.L_INSTRUCTION:
                    self.symbol_table.addEntry(self.symbol(), instruction_count - 1 - labels_found)
                    labels_found += 1

    
    def hasMoreLines(self) -> bool:
        return not self.completed 
    
    def __strip_comments(self, string) -> str:
        if len(string) >= 1:
            chars = []
            
            if string[0] != "/":
                chars.append(string[0])
                
            for i in range(1, len(string)):
                if not (string[i] == "/" and string[i - 1] == "/"):
                    if string[i] != " ":
                        chars.append(string[i])
                else:
                    break
            
            string = "".join(chars)

        return string
    
    def advance(self):
        while self.hasMoreLines():
            try:
                current_line = self.__strip_comments(self.__file_contents[self.current_line_no]).strip()
                self.current_line_no += 1
                
                if self.current_line_no == len(self.__file_contents):
                    self.completed = True
                            
                if current_line:
                    self.parsed_line = current_line
                    break
            except:
                return
            
            
    
    def instructionType(self) -> InstructionType:
        current_line = self.parsed_line
        
        if current_line.startswith("("):
            return InstructionType.L_INSTRUCTION
        elif current_line.startswith("@"):
            return InstructionType.A_INSTRUCTION
        
        return InstructionType.C_INSTRUCTION
    
    def symbol(self) -> str:
        if self.instructionType() == InstructionType.L_INSTRUCTION:
            return self.parsed_line[1:-1]
        elif self.instructionType() == InstructionType.A_INSTRUCTION:
            return self.parsed_line[1:]
        
        return None
    
    def __c_matches(self, index) -> str:
        matches = re.search(C_INS_PATTERN, self.parsed_line)
        
        if matches.groups()[index]:
            return matches.groups()[index]
        
        return ""
    
    def dest(self) -> str:
        return self.__c_matches(0)
    
    def comp(self) -> str:
        return self.__c_matches(1)
    
    def jump(self) -> str:
        return self.__c_matches(2)