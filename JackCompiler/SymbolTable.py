from vmtokens import VariableType

class SymbolTable:
    def __init__(self):
        pass
    
    def reset(self):
        pass
    
    def define(self, name: str, type: str, kind: VariableType):
        pass
    
    def varCount(self, kind: VariableType) -> int:
        pass
    
    def kindOf(self, name: str) -> VariableType:
        pass
    
    def typeOf(self, name: str) -> str:
        pass
    
    def indexOf(self, name: str) -> int:
        pass
