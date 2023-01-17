from typing import Union
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from tokens import LexicalElement, SymbolType, KeywordType
from vmtokens import VariableType, VirtualMemorySegmentType, CommandType
from constants import *


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer = None, vm_writer: VMWriter = None):
        self.tokenizer = tokenizer
        self.vm_writer = vm_writer
        self.symbol_table = SymbolTable()
        self.class_name = None
        self.subroutine_name = None
        self.subroutine_type = None
        self.running_index = 0

    def __check_token(
        self,
        actual_token: str,
        expected_token: Union[LexicalElement, SymbolType, KeywordType],
    ):
        assert (
            actual_token == expected_token.value
        ), f"Expected {expected_token.value} but found {actual_token} in {self.class_name}"
        self.tokenizer.advance()

    def __handle_or_rule(self, current_token: str, choices: list):
        return any(choice == current_token for choice in choices) == True

    def __handle_type_rule(self) -> str:
        # Consume 'type' token
        token_type = None

        if self.tokenizer.tokenType() == LexicalElement.KEYWORD:
            token_type = self.tokenizer.keyWord()
        else:
            token_type = self.tokenizer.identifier()

        self.tokenizer.advance()
        return token_type

    def compileClass(self):
        # rule -> 'class' className '{' classVarDec* subroutineDec* '}'
        self.__check_token(
            self.tokenizer.keyWord(), KeywordType.CLASS
        )  # Consume 'class' token

        self.class_name = self.tokenizer.identifier()  # Consume className identifier
        self.tokenizer.advance()

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.LEFT_BRACE
        )  # Consume '{' token

        # Consume classVarDec* rule
        while (
            self.tokenizer.tokenType() == LexicalElement.KEYWORD
            and self.__handle_or_rule(
                self.tokenizer.keyWord(),
                [KeywordType.FIELD.value, KeywordType.STATIC.value],
            )
        ):
            self.compileClassVarDec()

        # Consume subroutineDec* rule
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

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.RIGHT_BRACE
        )  # Consume '}' token
        self.vm_writer.close()

    def compileClassVarDec(self):
        # rule -> ('static'|'field') type varName (',' varName)* ';'
        current_token = self.tokenizer.keyWord()  # Consume ('static' | 'field') token
        token_kind = current_token
        self.tokenizer.advance()

        token_type = self.__handle_type_rule()  # Consume type token

        self.symbol_table.define(
            self.tokenizer.identifier(), token_type, token_kind
        )  # Consume varName token
        self.tokenizer.advance()

        # Consume (',' varName)*
        while (
            self.tokenizer.tokenType() == LexicalElement.SYMBOL
            and self.tokenizer.symbol() == SymbolType.COMMA.value
        ):
            self.tokenizer.advance()  # Consume ',' token
            self.symbol_table.define(
                self.tokenizer.identifier(), token_type, token_kind
            )
            self.tokenizer.advance()  # Consume varName token

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.SEMI_COLON
        )  # Consume ';' token

    def compileSubroutine(self):
        # rule -> ('constructor' | 'function' | 'method') ('void' | type) subroutineName
        #         '(' parameterList ')' subroutineBody
        self.symbol_table.reset()

        self.subroutine_type = (
            self.tokenizer.keyWord()
        )  # Consume ('constructor' | 'function' | 'method') token
        if self.subroutine_type == "method":
            self.symbol_table.define("this", self.class_name, VariableType.ARG.value)

        self.tokenizer.advance()

        self.subroutine_return = self.__handle_type_rule()  # Consume type
        self.subroutine_name = self.tokenizer.identifier()  # Consume subroutineName
        self.tokenizer.advance()

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.LEFT_PAREN
        )  # Consume '(' token

        # Consume parameterList rule
        self.compileParameterList()

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.RIGHT_PAREN
        )  # Consume ')' token

        # Consume subroutineBody rule
        self.compileSubroutineBody()

    def compileParameterList(self):
        # rule -> ((type varName) (',' type varName)*)?
        if self.tokenizer.tokenType() != LexicalElement.SYMBOL:
            token_type = self.__handle_type_rule()  # Consume type token
            self.symbol_table.define(  # Consume varName token
                self.tokenizer.identifier(), token_type, VariableType.ARG.value
            )
            self.tokenizer.advance()

            # Consume (',' type varName)*
            while (
                self.tokenizer.tokenType() == LexicalElement.SYMBOL
                and self.tokenizer.symbol() == SymbolType.COMMA.value
            ):
                self.tokenizer.advance()  # Consume ',' token
                token_type = self.__handle_type_rule()  # Consume type token
                self.symbol_table.define(  # Consume varName token
                    self.tokenizer.identifier(), token_type, VariableType.ARG.value
                )
                self.tokenizer.advance()

    def compileSubroutineBody(self):
        # rule -> '{' varDec* statements '}'
        self.__check_token(
            self.tokenizer.symbol(), SymbolType.LEFT_BRACE
        )  # Consume '{' token

        # Consume varDec*
        while (
            self.tokenizer.tokenType() == LexicalElement.KEYWORD
            and self.tokenizer.keyWord() == KeywordType.VAR.value
        ):
            self.compileVarDec()

        self.vm_writer.writeFunction(
            f"{self.class_name}.{self.subroutine_name}",
            self.symbol_table.varCount(VariableType.VAR),
        )

        if self.subroutine_type == "method":
            self.vm_writer.writePush(VirtualMemorySegmentType.ARGUMENT, 0)
            self.vm_writer.writePop(VirtualMemorySegmentType.POINTER, 0)
        elif self.subroutine_type == "constructor":
            self.vm_writer.writePush(
                VirtualMemorySegmentType.CONSTANT,
                self.symbol_table.varCount(VariableType.FIELD),
            )
            self.vm_writer.writeCall("Memory.alloc", 1)
            self.vm_writer.writePop(VirtualMemorySegmentType.POINTER, 0)

        self.compileStatements()  # Consume statements
        self.__check_token(
            self.tokenizer.symbol(), SymbolType.RIGHT_BRACE
        )  # Consume '}' token

    def compileVarDec(self):
        # varDec -> 'var' type varName (',' varName)* ';'
        self.__check_token(
            self.tokenizer.keyWord(), KeywordType.VAR
        )  # Consume 'var' token
        token_type = self.__handle_type_rule()  # Consume 'type' token
        self.symbol_table.define(  # Consume varName
            self.tokenizer.identifier(),
            token_type,
            VariableType.VAR.value,
        )
        self.tokenizer.advance()

        # Consume (',' varName)*
        while (
            self.tokenizer.tokenType() == LexicalElement.SYMBOL
            and self.tokenizer.symbol() == SymbolType.COMMA.value
        ):
            self.tokenizer.advance()  # Consume ',' token
            self.symbol_table.define(  # Consume varName token
                self.tokenizer.identifier(),
                token_type,
                VariableType.VAR.value,
            )
            self.tokenizer.advance()

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.SEMI_COLON
        )  # Consume ';' token

    def compileStatements(self):
        # rule -> statement*
        # statement -> letStatement | ifStatement | whileStatement | doStatement | returnStatement
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

    def compileLet(self):
        # rule -> 'let' varName ('[' expression, ']')? = expression ';'
        self.__check_token(
            self.tokenizer.keyWord(), KeywordType.LET
        )  # Consume 'let' token
        var_name = self.tokenizer.identifier()  # Consume varName token
        self.tokenizer.advance()

        is_array = False

        if self.tokenizer.symbol() == SymbolType.LEFT_SQ_BRACE.value:
            is_array = True
            self.vm_writer.writePush(
                self.symbol_table.kindOf(var_name), self.symbol_table.indexOf(var_name)
            )
            self.__check_token(
                self.tokenizer.symbol(), SymbolType.LEFT_SQ_BRACE
            )  # Consume '[' token
            self.compileExpression()  # Consume expression
            self.__check_token(
                self.tokenizer.symbol(), SymbolType.RIGHT_SQ_BRACE
            )  # Consume ']' token
            self.vm_writer.writeArithmetic(CommandType.ADD)

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.EQUAL
        )  # Consume '=' token
        self.compileExpression()  # Consume expression
        self.__check_token(
            self.tokenizer.symbol(), SymbolType.SEMI_COLON
        )  # Consume ';' token

        if is_array:
            self.vm_writer.writePop(VirtualMemorySegmentType.TEMP, 0)
            self.vm_writer.writePop(VirtualMemorySegmentType.POINTER, 1)
            self.vm_writer.writePush(VirtualMemorySegmentType.TEMP, 0)
            self.vm_writer.writePop(VirtualMemorySegmentType.THAT, 0)
        else:
            self.vm_writer.writePop(
                self.symbol_table.kindOf(var_name), self.symbol_table.indexOf(var_name)
            )

    def __get_label(self):
        label = f"{self.class_name}.{self.subroutine_name}.{self.running_index}"
        self.running_index += 1
        return label

    def compileIf(self):
        # rule -> 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self.__check_token(
            self.tokenizer.keyWord(), KeywordType.IF
        )  # Consume 'if' token

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.LEFT_PAREN
        )  # Consume '(' token
        self.compileExpression()  # Consume expression
        self.__check_token(
            self.tokenizer.symbol(), SymbolType.RIGHT_PAREN
        )  # Consume ')' token

        if_label_end = self.__get_label()
        else_label = self.__get_label()
        self.vm_writer.writeArithmetic(CommandType.NOT)
        self.vm_writer.writeIf(else_label)

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.LEFT_BRACE
        )  # Consume '{'
        self.compileStatements()  # Consume statements
        self.__check_token(
            self.tokenizer.symbol(), SymbolType.RIGHT_BRACE
        )  # Consume '}'

        self.vm_writer.writeGoto(if_label_end)
        self.vm_writer.writeLabel(else_label)

        # Consume ('else' '{' statements '}')?
        if self.tokenizer.keyWord() == KeywordType.ELSE.value:
            self.__check_token(
                self.tokenizer.keyWord(), KeywordType.ELSE
            )  # Consume 'else' token

            self.__check_token(
                self.tokenizer.symbol(), SymbolType.LEFT_BRACE
            )  # Consume '{' token
            self.compileStatements()  # Consume statements
            self.__check_token(
                self.tokenizer.symbol(), SymbolType.RIGHT_BRACE
            )  # Consume '}' token

        self.vm_writer.writeLabel(if_label_end)

    def compileWhile(self):
        # rule -> 'while' '(' expression ')' '{' statements '}'
        self.__check_token(
            self.tokenizer.keyWord(), KeywordType.WHILE
        )  # Consume 'while' token

        loop_label = self.__get_label()
        loop_label_end = self.__get_label()
        self.vm_writer.writeLabel(loop_label)

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.LEFT_PAREN
        )  # Consume '(' token
        self.compileExpression()  # Consume expression
        self.__check_token(
            self.tokenizer.symbol(), SymbolType.RIGHT_PAREN
        )  # Consume ')' token

        self.vm_writer.writeArithmetic(CommandType.NOT)
        self.vm_writer.writeIf(loop_label_end)

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.LEFT_BRACE
        )  # Consume '{' token
        self.compileStatements()  # Consume statements
        self.__check_token(
            self.tokenizer.symbol(), SymbolType.RIGHT_BRACE
        )  # Consume '}' token

        self.vm_writer.writeGoto(loop_label)
        self.vm_writer.writeLabel(loop_label_end)

    def __handle_subroutine_call(self, identifier: str):
        # rule -> subroutineName '(' expressionList ')' | (className|varName)'.'subroutineName '(' expressionList ')'
        subroutine_name = f"{self.class_name}.{identifier}"
        is_direct = True
        expression_count = 0
        if self.tokenizer.symbol() == SymbolType.DOT.value:
            is_direct = False
            self.__check_token(
                self.tokenizer.symbol(), SymbolType.DOT
            )  # Consume '.' token
            current_token = self.tokenizer.identifier()

            if current_token[0].islower() and identifier[0].islower():
                self.vm_writer.writePush(
                    self.symbol_table.kindOf(identifier),
                    self.symbol_table.indexOf(identifier),
                )
                expression_count = 1

            cls_name = identifier
            if not cls_name[0].isupper():
                cls_name = self.symbol_table.typeOf(identifier)

            subroutine_name = f"{cls_name}.{current_token}"  # Consume subroutine token
            self.tokenizer.advance()

        if is_direct:
            self.vm_writer.writePush(VirtualMemorySegmentType.POINTER, 0)
            expression_count += 1

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.LEFT_PAREN
        )  # Consume '(' token
        expression_count += self.compileExpressionList()  # Consume expressionList
        self.__check_token(
            self.tokenizer.symbol(), SymbolType.RIGHT_PAREN
        )  # Consume ')' token

        self.vm_writer.writeCall(subroutine_name, expression_count)

    def compileDo(self):
        # rule -> 'do' subroutineCall ';'
        self.__check_token(
            self.tokenizer.keyWord(), KeywordType.DO
        )  # Consume 'do' token

        subroutine_name = self.tokenizer.identifier()  # Consume subroutine name
        self.tokenizer.advance()

        self.__handle_subroutine_call(subroutine_name)
        self.__check_token(
            self.tokenizer.symbol(), SymbolType.SEMI_COLON
        )  # Consume ';' token
        self.vm_writer.writePop(VirtualMemorySegmentType.TEMP, 0)

    def compileReturn(self):
        # rule -> 'return' expression? ';'
        self.__check_token(
            self.tokenizer.keyWord(), KeywordType.RETURN
        )  # Consume 'return' token

        if self.tokenizer.tokenType() != LexicalElement.SYMBOL:
            self.compileExpression()  # Consume expression

        self.__check_token(
            self.tokenizer.symbol(), SymbolType.SEMI_COLON
        )  # Consume ';' token
        if self.subroutine_return == "void":
            self.vm_writer.writePush(VirtualMemorySegmentType.CONSTANT, 0)
        self.vm_writer.writeReturn()

    def __get_cmd(self, op: str):
        cmd = None

        if op == "+":
            cmd = CommandType.ADD
        elif op == "-":
            cmd = CommandType.SUB
        elif op == "/":
            self.vm_writer.writeCall("Math.divide", 2)
        elif op == "*":
            self.vm_writer.writeCall("Math.multiply", 2)
        elif op == "&amp;":
            cmd = CommandType.AND
        elif op == "|":
            cmd = CommandType.OR
        elif op == "&lt;":
            cmd = CommandType.LT
        elif op == "&gt;":
            cmd = CommandType.GT
        elif op == "=":
            cmd = CommandType.EQ

        return cmd

    def compileExpression(self):
        # rule -> term (op term)*
        # op -> '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
        self.compileTerm()  # Consume term

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
            op = self.tokenizer.symbol()  # Consume op
            self.tokenizer.advance()

            self.compileTerm()  # Consume term

            cmd = self.__get_cmd(op)
            if cmd:
                self.vm_writer.writeArithmetic(cmd)

    def compileTerm(self):
        # rule -> integerConstant | stringConstant | keywordConstant | varName |
        # varName '[' expression ']' | '(' expression ')' | (unaryOp term) | subroutineCall
        # unaryOp -> '-' | '~'
        # keywordConstant -> 'true' | 'false' | 'null' | 'this'

        token_type = self.tokenizer.tokenType()
        if token_type == LexicalElement.INT_CONST:
            int_const = self.tokenizer.intVal()  # Consume intConstant
            self.vm_writer.writePush(VirtualMemorySegmentType.CONSTANT, int_const)
            self.tokenizer.advance()
        elif token_type == LexicalElement.STRING_CONST:
            str_val = self.tokenizer.stringVal()  # Consume strConstant
            self.vm_writer.writePush(VirtualMemorySegmentType.CONSTANT, len(str_val))
            self.vm_writer.writeCall("String.new", 1)
            for char in str_val:
                self.vm_writer.writePush(VirtualMemorySegmentType.CONSTANT, ord(char))
                self.vm_writer.writeCall("String.appendChar", 2)
            self.tokenizer.advance()
        elif token_type == LexicalElement.KEYWORD:
            keyword = self.tokenizer.keyWord()  # Consume keyword
            if keyword == "null" or keyword == "false":
                self.vm_writer.writePush(VirtualMemorySegmentType.CONSTANT, 0)
            elif keyword == "true":
                self.vm_writer.writePush(VirtualMemorySegmentType.CONSTANT, 1)
                self.vm_writer.writeArithmetic(CommandType.NEG)
            elif keyword == "this":
                self.vm_writer.writePush(VirtualMemorySegmentType.POINTER, 0)
            self.tokenizer.advance()
        elif token_type == LexicalElement.SYMBOL:
            # Handle '(' expression ')' | unaryop term
            current_token = self.tokenizer.symbol()
            self.tokenizer.advance()
            if current_token == SymbolType.LEFT_PAREN.value:
                self.compileExpression()
                self.__check_token(self.tokenizer.symbol(), SymbolType.RIGHT_PAREN)
            else:
                self.compileTerm()
                cmd = CommandType.NOT
                if current_token == "-":
                    cmd = CommandType.NEG
                self.vm_writer.writeArithmetic(cmd)
        elif token_type == LexicalElement.IDENTIFIER:
            var_name = self.tokenizer.identifier()  # Consume varName
            self.tokenizer.advance()

            if self.tokenizer.symbol() == SymbolType.LEFT_SQ_BRACE.value:
                self.vm_writer.writePush(
                    self.symbol_table.kindOf(var_name),
                    self.symbol_table.indexOf(var_name),
                )
                self.__check_token(self.tokenizer.symbol(), SymbolType.LEFT_SQ_BRACE)
                self.compileExpression()
                self.__check_token(self.tokenizer.symbol(), SymbolType.RIGHT_SQ_BRACE)
                self.vm_writer.writeArithmetic(CommandType.ADD)
                self.vm_writer.writePop(VirtualMemorySegmentType.POINTER, 1)
                self.vm_writer.writePush(VirtualMemorySegmentType.THAT, 0)
            elif (
                self.tokenizer.symbol() == SymbolType.DOT.value
                or self.tokenizer.symbol() == SymbolType.LEFT_PAREN.value
            ):
                self.__handle_subroutine_call(var_name)
            else:
                self.vm_writer.writePush(
                    self.symbol_table.kindOf(var_name),
                    self.symbol_table.indexOf(var_name),
                )

    def compileExpressionList(self) -> int:
        # rule -> (expression (',' expression)*)?
        expression_count = 0

        if self.tokenizer.symbol() != SymbolType.RIGHT_PAREN.value:
            self.compileExpression()
            expression_count += 1

            while (
                self.tokenizer.tokenType() == LexicalElement.SYMBOL
                and self.tokenizer.symbol() == SymbolType.COMMA.value
            ):
                self.__check_token(self.tokenizer.symbol(), SymbolType.COMMA)
                self.compileExpression()
                expression_count += 1

        return expression_count
