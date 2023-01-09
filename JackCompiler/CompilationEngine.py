from typing import Union
from JackTokenizer import JackTokenizer
from tokens import LexicalElement, SymbolType, KeywordType


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer = None, output_file: str = None):
        self.tokenizer = tokenizer
        self.output_file = open(output_file, "w")

    def __close_file(self):
        self.output_file.close()

    def __check_token(
        self,
        actual_token: str,
        expected_token: Union[LexicalElement, SymbolType, KeywordType],
    ):
        assert actual_token == expected_token.value

    def __write_token(self, token: str, end=False):
        token_to_write = token
        if end:
            token_to_write = f"/{token_to_write}"
        self.output_file.write(f"<{token_to_write}>")

    def __handle_or_rule(self, current_token: str, choices: list):
        assert any(choice == current_token for choice in choices) == True
        return True

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
        self.__write_token(token_type)
        self.output_file.write(f" {token} ")
        self.__write_token(token_type, True)
        self.tokenizer.advance()

    def compileClass(self):
        # rule -> 'class' className '{' classVarDec* subroutineDec* '}'
        self.__check_token(self.tokenizer.keyWord(), KeywordType.CLASS)
        self.__write_token(KeywordType.CLASS.value)
        self.tokenizer.advance()

        self.__handle_token_output(
            self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value
        )

        self.__check_token(self.tokenizer.symbol(), SymbolType.LEFT_BRACE)
        self.__write_token(SymbolType.LEFT_BRACE.value)
        self.tokenizer.advance()

        token_count = self.tokenizer.token_count

        while (
            self.tokenizer.tokenType() == LexicalElement.KEYWORD
            and self.__handle_or_rule(
                self.tokenizer.keyWord(),
                [KeywordType.FIELD.value, KeywordType.STATIC.value],
            )
        ):
            self.compileClassVarDec()

        if self.tokenizer.token_count == token_count:
            self.tokenizer.advance()

        token_count = self.tokenizer.token_count

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

        if self.tokenizer.token_count == token_count:
            self.tokenizer.advance()

        self.__check_token(self.tokenizer.symbol(), SymbolType.RIGHT_BRACE)
        self.__write_token(SymbolType.RIGHT_BRACE.value)
        self.__write_token(KeywordType.CLASS.value, True)
        self.__close_file()

    def compileClassVarDec(self):
        # rule -> ('static'|'field') type varName (',' varName)* ';'
        self.__write_token("classVarDec")

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
        self.__write_token("classVarDec", True)

    def compileSubroutine(self):
        # rule -> ('constructor' | 'function' | 'method') ('void' | type) subroutineName
        #         '(' parameterList ')' subroutineBody
        self.__write_token("subroutineDec")
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
        self.__write_token("subroutineDec", True)

    def compileParameterList(self):
        # rule -> ((type varName) (',' type varName)*)?
        self.__write_token("parameterList")

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

        self.__write_token("parameterList", True)

    def compileSubroutineBody(self):
        # rule -> '{' varDec* statements '}'
        self.__write_token("subroutineBody")

        while (
            self.tokenizer.tokenType() == LexicalElement.KEYWORD
            and self.tokenizer.keyWord() == KeywordType.VAR.value
        ):
            self.compileVarDec()

        self.compileStatements()
        self.__write_token("subroutineBody", True)

    def compileVarDec(self):
        # varDec -> 'var' type varName (',' varName)* ';'
        self.__write_token("varDec")
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
        self.__write_token("varDec", True)

    def compileStatements(self):
        # rule -> statement*
        # statement -> letStatement | ifStatement | whileStatement | doStatement | returnStatement
        self.__write_token("statements")

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

        self.__write_token("statements", True)

    def compileLet(self):
        # rule -> 'let' varName ('[' expression, ']')? = expression ';'
        self.__write_token("letStatement")
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
        self.__write_token("letStatement", True)

    def compileIf(self):
        # rule -> 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self.__write_token("ifStatement")
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
            self.__handle_token_output(self.tokenizer.keyWord(), LexicalElement.KEYWORD.value)
            self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
            self.compileStatements()
            self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)

        self.__write_token("ifStatement", True)

    def compileWhile(self):
        # rule -> 'while' '(' expression ')' '{' statements '}'
        self.__write_token("whileStatement")
        
        self.__handle_token_output(
            self.tokenizer.keyWord(), LexicalElement.KEYWORD.value
        )
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileExpression()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileStatements()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        
        self.__write_token("whileStatement", True)

    def compileDo(self):
        # rule -> 'do' subroutineCall ';'
        pass

    def compileReturn(self):
        pass

    def compileExpression(self):
        pass

    def compileTerm(self):
        pass

    def compileExpressionList(self) -> int:
        pass
