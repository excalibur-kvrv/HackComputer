from tokens import KeywordType, LexicalElement

class JackTokenizer:
    def __init__(self, input_file=None):
        pass
    
    def hasMoreTokens(self) -> bool:
        pass
    
    def advance(self):
        pass
    
    def tokenType(self) -> LexicalElement:
        pass
    
    def keyWord(self) -> KeywordType:
        pass
    
    def symbol(self) -> str:
        pass
    
    def identifier(self) -> str:
        pass
    
    def intVal(self) -> int:
        pass
    
    def stringVal(self) -> str:
        pass