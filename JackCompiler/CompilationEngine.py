from typing import Union
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from tokens import LexicalElement, SymbolType, KeywordType
from vmtokens import VariableType, VirtualMemorySegmentType
from constants import *


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer = None, output_file: str = None):
        self.tokenizer = tokenizer
        self.output_file = open(output_file, "w")
        self.indents = [0]
        self.symbol_table = SymbolTable()
        self.class_name = None

    def __close_file(self):
        self.output_file.close()

    def __check_token(
        self,
        actual_token: str,
        expected_token: Union[LexicalElement, SymbolType, KeywordType],
    ):
        assert actual_token == expected_token.value

    def __write_token(self, token: str, end=False, auto=False, insert_newline=False):
        token_to_write = token

        if end:
            token_to_write = f"</{token_to_write}>\n"
            if auto:
                token_to_write = f"{' ' * self.indents[-1]}{token_to_write}"
            self.output_file.write(f"{token_to_write}")
        else:
            self.output_file.write(f"{' ' * self.indents[-1]}<{token_to_write}>")
            if insert_newline:
                self.output_file.write("\n")

    def __handle_or_rule(self, current_token: str, choices: list):
        return any(choice == current_token for choice in choices) == True
    
    def __handle_type_rule(self) -> str:
        token_type = None
        
        if self.tokenizer.tokenType() == LexicalElement.KEYWORD:
            token_type = self.tokenizer.keyWord()
            self.__handle_token_output(
                token_type, LexicalElement.KEYWORD.value
            )
        else:
            token_type = self.tokenizer.identifier()
            self.__handle_identifier(token_type, "used")
        
        return token_type
    
    def __handle_identifier(self, name: str, usage: str):
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("identifier", insert_newline=True)
        self.__handle_token_output(name, "name", False)
        category = self.symbol_table.kindOf(name)
        if category == "none":
            if name[0].isupper():
                category = "class"
            else:
                category = "subroutine"
        self.__handle_token_output(category, "category", False)
        self.__handle_token_output(self.symbol_table.indexOf(name), "index", False)
        self.__handle_token_output(usage, "usage", False)
        self.__write_token("identifier", True, True)
        self.indents.pop()
        self.tokenizer.advance()

    def __handle_token_output(self, token: str, token_type: str, advance=True):
        self.indents.append(self.indents[-1] + 1)
        self.__write_token(token_type)
        self.output_file.write(f" {token} ")
        self.__write_token(token_type, True)
        self.indents.pop()
        
        if advance:
            self.tokenizer.advance()

    def compileClass(self):
        # rule -> 'class' className '{' classVarDec* subroutineDec* '}'
        self.__check_token(self.tokenizer.keyWord(), KeywordType.CLASS)
        self.__write_token(KeywordType.CLASS.value, insert_newline=True)
        self.indents.append(self.indents[-1] + 1)
        self.__handle_token_output(self.tokenizer.keyWord(), LexicalElement.KEYWORD.value)
        self.class_name = self.tokenizer.identifier()
        self.__handle_identifier(
            self.tokenizer.identifier(), "declared"
        )

        self.__check_token(self.tokenizer.symbol(), SymbolType.LEFT_BRACE)
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)

        while (
            self.tokenizer.tokenType() == LexicalElement.KEYWORD
            and self.__handle_or_rule(
                self.tokenizer.keyWord(),
                [KeywordType.FIELD.value, KeywordType.STATIC.value],
            )
        ):
            self.compileClassVarDec()

        while (
            self.tokenizer.tokenType() == LexicalElement.KEYWORD
            and self.__handle_or_rule(
                self.tokenizer.keyWord(),
                [
                    KeywordType.CONSTRUCTOR.value,
                    KeywordType.FUNCTION.value,
                    KeywordType.METHOD.value,
                ],
            )
        ):
            self.compileSubroutine()

        self.__check_token(self.tokenizer.symbol(), SymbolType.RIGHT_BRACE)
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.indents.pop()
        self.__write_token(KeywordType.CLASS.value, True, True)
        self.__close_file()

    def compileClassVarDec(self):
        # rule -> ('static'|'field') type varName (',' varName)* ';'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("classVarDec", insert_newline=True)
        
        current_token = self.tokenizer.keyWord()
        token_kind = current_token
        self.__handle_token_output(
            KeywordType(current_token).value, LexicalElement.KEYWORD.value
        )

        token_type = self.__handle_type_rule()

        self.symbol_table.define(self.tokenizer.identifier(), token_type, token_kind)
        self.__handle_identifier(
            self.tokenizer.identifier(), "declared"
        )

        while (
            self.tokenizer.tokenType() == LexicalElement.SYMBOL
            and self.tokenizer.symbol() == SymbolType.COMMA.value
        ):
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )
            self.symbol_table.define(self.tokenizer.identifier(), token_type, token_kind)
            self.__handle_identifier(
                self.tokenizer.identifier(), "declared"
            )

        self.__check_token(self.tokenizer.symbol(), SymbolType.SEMI_COLON)
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__write_token("classVarDec", True, True)
        self.indents.pop()

    def compileSubroutine(self):
        # rule -> ('constructor' | 'function' | 'method') ('void' | type) subroutineName
        #         '(' parameterList ')' subroutineBody
        self.symbol_table.reset()
        self.symbol_table.define("this", self.class_name, VariableType.ARG.value)
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("subroutineDec", insert_newline=True)
        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_type_rule()
        self.__handle_identifier(
            self.tokenizer.identifier(), "declared"
        )
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileParameterList()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileSubroutineBody()
        self.__write_token("subroutineDec", True, True)
        self.indents.pop()

    def compileParameterList(self):
        # rule -> ((type varName) (',' type varName)*)?
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("parameterList", insert_newline=True)

        if self.tokenizer.tokenType() != LexicalElement.SYMBOL:
            token_type = self.__handle_type_rule()
            self.symbol_table.define(self.tokenizer.identifier(), token_type, VariableType.ARG.value)
            self.__handle_identifier(
                self.tokenizer.identifier(), "declared"
            )

            while (
                self.tokenizer.tokenType() == LexicalElement.SYMBOL
                and self.tokenizer.symbol() == SymbolType.COMMA.value
            ):
                self.__handle_token_output(
                    self.tokenizer.symbol(), LexicalElement.SYMBOL.value
                )
                token_type = self.__handle_type_rule()
                self.symbol_table.define(self.tokenizer.identifier(), token_type, VariableType.ARG.value)
                self.__handle_identifier(
                    self.tokenizer.identifier(), "declared"
                )

        self.__write_token("parameterList", True, True)
        self.indents.pop()

    def compileSubroutineBody(self):
        # rule -> '{' varDec* statements '}'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("subroutineBody", insert_newline=True)

        self.__handle_token_output(
            self.tokenizer.symbol(), LexicalElement.SYMBOL.value
        )
        
        while (
            self.tokenizer.tokenType() == LexicalElement.KEYWORD
            and self.tokenizer.keyWord() == KeywordType.VAR.value
        ):
            self.compileVarDec()

        self.compileStatements()
        self.__handle_token_output(
            self.tokenizer.symbol(), LexicalElement.SYMBOL.value
        )
        self.__write_token("subroutineBody", True, True)
        self.indents.pop()

    def compileVarDec(self):
        # varDec -> 'var' type varName (',' varName)* ';'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("varDec", insert_newline=True)

        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        token_type = self.__handle_type_rule()
        self.symbol_table.define(self.tokenizer.identifier(), token_type, VirtualMemorySegmentType.LOCAL.value)
        self.__handle_identifier(self.tokenizer.identifier(), "declared")

        while (
            self.tokenizer.tokenType() == LexicalElement.SYMBOL
            and self.tokenizer.symbol() == SymbolType.COMMA.value
        ):
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )
            self.symbol_table.define(self.tokenizer.identifier(), token_type, VirtualMemorySegmentType.LOCAL.value)
            self.__handle_identifier(self.tokenizer.identifier(), "declared")

        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__write_token("varDec", True, True)
        self.indents.pop()

    def compileStatements(self):
        # rule -> statement*
        # statement -> letStatement | ifStatement | whileStatement | doStatement | returnStatement
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("statements", insert_newline=True)
        
        while (
            self.tokenizer.tokenType() == LexicalElement.KEYWORD
            and self.__handle_or_rule(
                self.tokenizer.keyWord(),
                [
                    KeywordType.LET.value,
                    KeywordType.IF.value,
                    KeywordType.WHILE.value,
                    KeywordType.DO.value,
                    KeywordType.RETURN.value,
                ],
            )
        ):
            current_token = self.tokenizer.keyWord()
            if current_token == KeywordType.LET.value:
                self.compileLet()
            elif current_token == KeywordType.IF.value:
                self.compileIf()
            elif current_token == KeywordType.WHILE.value:
                self.compileWhile()
            elif current_token == KeywordType.DO.value:
                self.compileDo()
            elif current_token == KeywordType.RETURN.value:
                self.compileReturn()

        self.__write_token("statements", True, True)
        self.indents.pop()

    def compileLet(self):
        # rule -> 'let' varName ('[' expression, ']')? = expression ';'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("letStatement", insert_newline=True)
        
        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_identifier(self.tokenizer.identifier(), "used")

        if self.tokenizer.symbol() == SymbolType.LEFT_SQ_BRACE.value:
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )
            self.compileExpression()
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )

        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileExpression()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__write_token("letStatement", True, True)
        self.indents.pop()

    def compileIf(self):
        # rule -> 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("ifStatement", insert_newline=True)

        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileExpression()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileStatements()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)

        if self.tokenizer.keyWord() == KeywordType.ELSE.value:
            self.__handle_token_output(
                self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
            )
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )
            self.compileStatements()
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )

        self.__write_token("ifStatement", True, True)
        self.indents.pop()

    def compileWhile(self):
        # rule -> 'while' '(' expression ')' '{' statements '}'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("whileStatement", insert_newline=True)

        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileExpression()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileStatements()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)

        self.__write_token("whileStatement", True, True)
        self.indents.pop()

    def __handle_subroutine_call(self):
        # rule -> subroutineName '(' expressionList ')' | (className|varName)'.'subroutineName '(' expressionList ')'
        if self.tokenizer.symbol() == SymbolType.DOT.value:
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )
            self.__handle_identifier(self.tokenizer.identifier(), "used")

        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileExpressionList()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)

    def compileDo(self):
        # rule -> 'do' subroutineCall ';'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("doStatement", insert_newline=True)

        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_identifier(self.tokenizer.identifier(), "used")
        self.__handle_subroutine_call()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__write_token("doStatement", True, True)
        self.indents.pop()

    def compileReturn(self):
        # rule -> 'return' expression? ';'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("returnStatement", insert_newline=True)

        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )

        if self.tokenizer.tokenType() != LexicalElement.SYMBOL:
            self.compileExpression()

        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__write_token("returnStatement", True, True)
        self.indents.pop()

    def compileExpression(self):
        # rule -> term (op term)*
        # op -> '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("expression", insert_newline=True)
        self.compileTerm()

        while (
            self.tokenizer.tokenType() == LexicalElement.SYMBOL
            and self.__handle_or_rule(
                self.tokenizer.symbol(),
                [
                    SymbolType.PLUS.value,
                    SymbolType.MINUS.value,
                    SymbolType.SLASH.value,
                    SymbolType.STAR.value,
                    SPECIAL_MAPPINGS[SymbolType.AMPERSAND.value],
                    SymbolType.PIPE.value,
                    SPECIAL_MAPPINGS[SymbolType.LESS_THAN.value],
                    SPECIAL_MAPPINGS[SymbolType.GREATER_THAN.value],
                    SymbolType.EQUAL.value,
                ],
            )
        ):
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )
            self.compileTerm()

        self.__write_token("expression", True, True)
        self.indents.pop()

    def compileTerm(self):
        # rule -> integerConstant | stringConstant | keywordConstant | varName |
        # varName '[' expression ']' | '(' expression ')' | (unaryOp term) | subroutineCall
        # unaryOp -> '-' | '~'
        # keywordConstant -> 'true' | 'false' | 'null' | 'this'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("term", insert_newline=True)

        token_type = self.tokenizer.tokenType()
        if token_type == LexicalElement.INT_CONST:
            self.__handle_token_output(
                self.tokenizer.intVal(), LexicalElement.INT_CONST.value
            )
        elif token_type == LexicalElement.STRING_CONST:
            self.__handle_token_output(
                self.tokenizer.stringVal(), LexicalElement.STRING_CONST.value
            )
        elif token_type == LexicalElement.KEYWORD:
            self.__handle_token_output(self.tokenizer.keyWord(), LexicalElement.KEYWORD.value)
        elif token_type == LexicalElement.SYMBOL:
            current_token = self.tokenizer.symbol()
            if current_token == SymbolType.LEFT_PAREN.value:
                self.__handle_token_output(current_token, LexicalElement.SYMBOL.value)
                self.compileExpression()
                self.__handle_token_output(
                    self.tokenizer.symbol(), LexicalElement.SYMBOL.value
                )
            else:
                self.__handle_token_output(current_token, LexicalElement.SYMBOL.value)
                self.compileTerm()
        elif token_type == LexicalElement.IDENTIFIER:
            self.__handle_identifier(self.tokenizer.identifier(), "used")
            if self.tokenizer.symbol() == SymbolType.LEFT_SQ_BRACE.value:
                self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
                self.compileExpression()
                self.__handle_token_output(
                    self.tokenizer.symbol(), LexicalElement.SYMBOL.value
                )
            elif (
                self.tokenizer.symbol() == SymbolType.DOT.value
                or self.tokenizer.symbol() == SymbolType.LEFT_PAREN.value
            ):
                self.__handle_subroutine_call()

        self.__write_token("term", True, True)
        self.indents.pop()

    def compileExpressionList(self) -> int:
        # rule -> (expression (',' expression)*)?
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("expressionList", insert_newline=True)
        
        if self.tokenizer.symbol() != SymbolType.RIGHT_PAREN.value:
            self.compileExpression()
            while (
                self.tokenizer.tokenType() == LexicalElement.SYMBOL
                and self.tokenizer.symbol() == SymbolType.COMMA.value
            ):
                self.__handle_token_output(
                    self.tokenizer.symbol(), LexicalElement.SYMBOL.value
                )
                self.compileExpression()

        self.__write_token("expressionList", True, True)
        self.indents.pop()
