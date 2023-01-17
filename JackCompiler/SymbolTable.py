from vmtokens import VariableType

class SymbolTable:
    def __init__(self):
        self.var_count = {
			"static": 0,
			"field": 0,
			"local": 0,
			"argument": 0
		}
        self.class_level = {}
        self.subroutine_level = {}
    
    def reset(self):
        self.var_count["local"] = 0
        self.var_count["argument"] = 0
        self.subroutine_level = {}
    
    def define(self, name: str, type: str, kind: VariableType):
        if kind == VariableType.STATIC.value or kind == VariableType.FIELD.value:
            self.class_level[name] = { "type": type, "kind": kind, "index": self.var_count[kind] }
        else:
            self.subroutine_level[name] = { "type": type, "kind": kind, "index": self.var_count[kind] }
        self.var_count[kind] += 1
    
    def varCount(self, kind: VariableType) -> int:
        return self.var_count[kind.value]
    
    def __get_property(self, name, prop):
        if name in self.subroutine_level:
            return self.subroutine_level[name][prop]
        elif name in self.class_level:
            return self.class_level[name][prop]
        return VariableType.NONE.value
    
    def kindOf(self, name: str) -> VariableType:
        kind = self.__get_property(name, "kind")
        if kind == "field":
            return "this"
        return kind
    
    def typeOf(self, name: str) -> str:
        return self.__get_property(name, "type")
    
    def indexOf(self, name: str) -> int:
        return self.__get_property(name, "index")
