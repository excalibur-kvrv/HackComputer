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
        self.__handle_token_output(self.tokenizer.keyWord(), LexicalElement.KEYWORD.value)
        token_type = self.tokenizer.tokenType()
        if token_type == LexicalElement.KEYWORD:
            self.__handle_token_output(self.tokenizer.keyWord(), LexicalElement.KEYWORD.value)
        else:
            self.__handle_token_output(self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value)
        
        self.__handle_token_output(self.tokenizer.identifier(), LexicalElement.IDENTIFIER.value)
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileParameterList()
        self.__handle_token_output(self.tokenizer.symbol(), LexicalElement.SYMBOL.value)
        self.compileSubroutineBody()

    def compileParameterList(self):
        # rule -> ((type varName) (',' type varName)*)?
        pass

    def compileSubroutineBody(self):
        pass

    def compileVarDec(self):
        pass

    def compileStatements(self):
        pass

    def compileLet(self):
        pass

    def compileIf(self):
        pass

    def compileWhile(self):
        pass

    def compileDo(self):
        pass

    def compileReturn(self):
        pass

    def compileExpression(self):
        pass

    def compileTerm(self):
        pass

    def compileExpressionList(self) -> int:
        pass
