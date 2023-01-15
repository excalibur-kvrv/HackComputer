from typing import Union
from JackTokenizer import JackTokenizer
from tokens import LexicalElement, SymbolType, KeywordType
from constants import *


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer = None, output_file: str = None):
        self.tokenizer = tokenizer
        self.output_file = open(output_file, "w")
        self.indents = [0]

    def __close_file(self):
        self.output_file.close()

    def __check_token(
        self,
        actual_token: str,
        expected_token: Union[LexicalElement, SymbolType, KeywordType],
    ):
        assert actual_token == expected_token.value

    def __write_token(self, token: str, end=False, auto=False):
        token_to_write = token

        if end:
            token_to_write = f"</{token_to_write}>\n"
            if auto:
                token_to_write = f"{' ' * self.indents[-1]}{token_to_write}"
            self.output_file.write(f"{token_to_write}")
        else:
            self.output_file.write(f"{' ' * self.indents[-1]}<{token_to_write}>")

    def __handle_or_rule(self, current_token: str, choices: list):
        return any(choice == current_token for choice in choices) == True
    
    def __handle_type_rule(self):
        token_type = self.tokenizer.tokenType()
        if token_type == LexicalElement.KEYWORD:
            self.__handle_token_output(
                self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
            )
        else:
            self.__handle_token_output(
                self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
            )

    def __handle_token_output(self, token: str, token_type: str):
        self.indents.append(self.indents[-1] + 1)
        self.__write_token(token_type)
        self.output_file.write(f" {token} ")
        self.__write_token(token_type, True)
        self.indents.pop()
        self.tokenizer.advance()

    def compileClass(self):
        # rule -> 'class' className '{' classVarDec* subroutineDec* '}'
        self.__check_token(self.tokenizer.keyWord(), KeywordType.CLASS)
        self.__write_token(KeywordType.CLASS.value)
        self.indents.append(self.indents[-1] + 1)
        self.output_file.write("\n")
        self.__handle_token_output(self.tokenizer.keyWord(), LexicalElement.KEYWORD.value)

        self.__handle_token_output(
            self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
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
        self.__write_token("classVarDec")
        self.output_file.write("\n")
        
        current_token = self.tokenizer.keyWord()
        self.__handle_token_output(
            KeywordType(current_token).value, LexicalElement.KEYWORD.value
        )

        token_type = self.tokenizer.tokenType()
        if token_type == LexicalElement.KEYWORD:
            self.__handle_token_output(
                self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
            )
        else:
            self.__handle_token_output(
                self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
            )

        self.__handle_token_output(
            self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
        )

        while (
            self.tokenizer.tokenType() == LexicalElement.SYMBOL
            and self.tokenizer.symbol() == SymbolType.COMMA.value
        ):
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )
            self.__handle_token_output(
                self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
            )

        self.__check_token(self.tokenizer.symbol(), SymbolType.SEMI_COLON)
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__write_token("classVarDec", True, True)
        self.indents.pop()

    def compileSubroutine(self):
        # rule -> ('constructor' | 'function' | 'method') ('void' | type) subroutineName
        #         '(' parameterList ')' subroutineBody
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("subroutineDec")
        self.output_file.write("\n")
        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_type_rule()
        self.__handle_token_output(
            self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
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
        self.__write_token("parameterList")
        self.output_file.write("\n")

        if self.tokenizer.tokenType() != LexicalElement.SYMBOL:
            self.__handle_type_rule()
            self.__handle_token_output(
                self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
            )

            while (
                self.tokenizer.tokenType() == LexicalElement.SYMBOL
                and self.tokenizer.symbol() == SymbolType.COMMA.value
            ):
                self.__handle_token_output(
                    self.tokenizer.symbol(), LexicalElement.SYMBOL.value
                )
                self.__handle_type_rule()
                self.__handle_token_output(
                    self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
                )

        self.__write_token("parameterList", True, True)
        self.indents.pop()

    def compileSubroutineBody(self):
        # rule -> '{' varDec* statements '}'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("subroutineBody")
        self.output_file.write("\n")

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
        self.__write_token("varDec")
        self.output_file.write("\n")

        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_type_rule()
        self.__handle_token_output(
            self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
        )

        while (
            self.tokenizer.tokenType() == LexicalElement.SYMBOL
            and self.tokenizer.symbol() == SymbolType.COMMA.value
        ):
            self.__handle_token_output(
                self.tokenizer.symbol(), LexicalElement.SYMBOL.value
            )
            self.__handle_token_output(
                self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
            )

        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__write_token("varDec", True, True)
        self.indents.pop()

    def compileStatements(self):
        # rule -> statement*
        # statement -> letStatement | ifStatement | whileStatement | doStatement | returnStatement
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("statements")
        self.output_file.write("\n")
        
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
        self.__write_token("letStatement")
        self.output_file.write("\n")
        
        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_token_output(
            self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
        )

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
        self.__write_token("ifStatement")
        self.output_file.write("\n")

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
        self.__write_token("whileStatement")
        self.output_file.write("\n")

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
            self.__handle_token_output(
                self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
            )

        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileExpressionList()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)

    def compileDo(self):
        # rule -> 'do' subroutineCall ';'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("doStatement")
        self.output_file.write("\n")

        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_token_output(
            self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
        )
        self.__handle_subroutine_call()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__write_token("doStatement", True, True)
        self.indents.pop()

    def compileReturn(self):
        # rule -> 'return' expression? ';'
        self.indents.append(self.indents[-1] + 1)
        self.__write_token("returnStatement")
        self.output_file.write("\n")

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
        self.__write_token("expression")
        self.output_file.write("\n")
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
        self.__write_token("term")
        self.output_file.write("\n")

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
            self.__handle_token_output(
                self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
            )
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
        self.__write_token("expressionList")
        self.output_file.write("\n")
        
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
