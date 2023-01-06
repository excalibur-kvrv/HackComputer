from tokens import LexicalElement
from constants import *


class JackTokenizer:
    def __init__(self, input_file=None):
        if not input_file:
            raise ValueError("Input file must be provided.")

        with open(input_file) as file:
            file_content = file.read()

        self.characters_read = 0
        self.current_token = None
        self.current_token_type = None
        self.file_content = file_content
        self.token_count = 0
    
    def hasMoreTokens(self) -> bool:
        return self.characters_read < len(self.file_content) - 1
    
    def advance(self):
        self.current_token = None
        self.current_token_type = None
        
        if self.hasMoreTokens():
            current_index = self.characters_read
            current_character = self.file_content[current_index]
            
            if current_character == "\n":
                current_index = self.__handle_single_comment(current_index)
            elif current_character == " ":
                current_index = self.__handle_whitespace(current_index + 1)
            elif current_character == "/" and self.__get_file_character(current_index + 1) == "/":
                current_index = self.__handle_single_comment(current_index + 2)
            elif current_character == "/" and self.__get_file_character(current_index + 1) == "*":
                current_index = self.__handle_multiline_comment(current_index + 2)
            elif current_character == '"':
                current_index = self.__handle_string_token(current_index + 1)
            elif current_character.isdigit():
                current_index = self.__handle_int_token(current_index)
            elif current_character in SYMBOLS:
                current_index = self.__handle_symbol_token(current_index)
            else:
                current_index = self.__handle_identifier_keyword_token(current_index)
            
            self.characters_read = current_index
    
    def __get_file_character(self, index: int) -> str:
        if self.hasMoreTokens():
            return self.file_content[index]
        return ""

    def __handle_whitespace(self, index: int) -> int:
        current_index = index
        current_char = self.__get_file_character(current_index)
        
        while current_char == " ":
            current_index += 1
            current_char = self.__get_file_character(current_index)
        
        return current_index
    
    def __handle_single_comment(self, index: int) -> int:
        current_index = index
        current_char = self.__get_file_character(current_index)
        
        while current_char != "\n":
            current_index += 1
            current_char = self.__get_file_character(current_index)
        
        return current_index + 1
            
    def __handle_multiline_comment(self, index: int) -> int:
        current_index = index
        current_char = self.__get_file_character(current_index)
        
        while not (current_char == "*" and self.__get_file_character(current_index + 1) == "/"):
            current_index += 1
            current_char = self.__get_file_character(current_index)
        
        return current_index + 2
    
    def __handle_string_token(self, index: int) -> int:
        self.current_token_type = LexicalElement.STRING_CONST
        
        current_index = index
        string_characters = []
        
        while not self.current_token:
            current_char = self.__get_file_character(current_index)
            if  current_char != '"':
                string_characters.append(current_char)
                current_index += 1
            else:
                current_index += 1
                self.current_token = "".join(string_characters)
                self.token_count += 1
        
        return current_index
            
    
    def __handle_int_token(self, index: int) -> int:
        self.current_token_type = LexicalElement.INT_CONST
        
        current_index = index
        digit_characters = []

        while not self.current_token:
            current_char = self.__get_file_character(current_index)
            if current_char.isdigit():
                digit_characters.append(current_char)
                current_index += 1
            else:
                self.current_token = "".join(digit_characters)
                self.token_count += 1
        
        return current_index
    
    def __handle_symbol_token(self, index: int) -> int:
        self.current_token_type = LexicalElement.SYMBOL
        self.current_token = self.__get_file_character(index)
        self.token_count += 1
        return index + 1
    
    def __handle_identifier_keyword_token(self, index: int) -> int:
        characters = []
        current_index = index
        
        while self.current_token is None:
            current_char = self.__get_file_character(current_index)
            if current_char not in [" ", "\n", "\""] and current_char not in SYMBOLS:
                characters.append(current_char)
                current_index += 1
            else:
                self.current_token = "".join(characters)
                if self.current_token in KEYWORDS:
                    self.current_token_type = LexicalElement.KEYWORD
                else:
                    self.current_token_type = LexicalElement.IDENTIFIER
                self.token_count += 1
        
        return current_index
    
    def tokenType(self) -> LexicalElement:
        return self.current_token_type
    
    def keyWord(self) -> str:
        return self.current_token
    
    def symbol(self) -> str:
        return "".join(SPECIAL_MAPPINGS[c] if c in SPECIAL_MAPPINGS else c for c in self.current_token)
    
    def identifier(self) -> str:
        return self.current_token
    
    def intVal(self) -> int:
        return int(self.current_token)
    
    def stringVal(self) -> str:
        return "".join(SPECIAL_MAPPINGS[c] if c in SPECIAL_MAPPINGS else c for c in self.current_token)

