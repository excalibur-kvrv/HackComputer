from command import Command
import os


class CodeWriter:
    def __init__(self, output_file=None, stream=None):
        if not (output_file or stream):
            raise ValueError("Output file or a write stream must be provided.")

        _, file_name = os.path.split(output_file)
        self.file_name = file_name

        if output_file:
            self.stream = open(output_file, "w")
        else:
            if stream.mode != "w":
                raise ValueError(
                    f"File opened not opened in 'w' mode instead is open in {stream.mode}"
                )

            self.stream = stream

        self.arithmetic_fns = {
            "add": self.__write_add,
            "sub": self.__write_sub,
            "neg": self.__write_neg,
            "eq": self.__write_eq,
            "gt": self.__write_gt,
            "lt": self.__write_lt,
            "and": self.__write_and,
            "or": self.__write_or,
            "not": self.__write_not,
        }

        self.instruction_written_count = 0

        self.segment_addresses = {
            "temp": "5",
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT",
        }

    def writeBootstrapCode(self):
        instructions = ["@256", "D=A", "@SP", "M=D"]
        self.__write_instructions(instructions)
        self.writeCall("Sys.init", 0)

    def writeArithmetic(self, command: str):
        self.arithmetic_fns[command]()

    def writePushPop(self, command: Command, segment: str, index: int):
        if command == Command.C_PUSH:
            self.__push_cmd(segment, index)
        elif command == Command.C_POP:
            self.__pop_cmd(segment, index)

    def writeLabel(self, label: str):
        instructions = [f"({label})"]
        self.__write_instructions(instructions)

    def writeGoto(self, label: str):
        instructions = [f"@{label}", "0;JMP"]
        self.__write_instructions(instructions)

    def writeIf(self, label: str):
        instructions = ["@SP", "M=M-1", "A=M", "D=M", f"@{label}", "D;JNE"]
        self.__write_instructions(instructions)

    def setFileName(self, fileName: str):
        self.file_name = fileName

    def writeFunction(self, functionName: str, nVars: int):
        instructions = [f"({functionName})"]

        for _ in range(nVars):
            instructions.extend(
                [
                    "@SP",
                    "D=A",
                    "A=M",
                    "M=D",
                    "@SP",
                    "M=M+1",
                ]
            )
        self.__write_instructions(instructions)

    def writeCall(self, functionName: str, nArgs: int):
        push_instructions = self.__get_push_instructions()

        common_instructions = []
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            common_instructions.extend([f"@{segment}", "D=M", *push_instructions])

        return_label = f"{functionName}$ret.{self.instruction_written_count+1}"
        instructions = [
            f"@{return_label}",
            "D=A",
            *push_instructions,
            *common_instructions,
            "@SP",
            "D=M",
            "@ARG",
            "M=D",
            "@5",
            "D=A",
            "@ARG",
            "M=M-D",
            f"@{nArgs}",
            "D=A",
            "@ARG",
            "M=M-D",
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
        ]

        self.__write_instructions(instructions)
        self.writeGoto(functionName)
        self.__write_instructions([f"({return_label})"])

    def writeReturn(self):
        instructions = [
            "@LCL",
            "D=M",
            "@frame",
            "M=D",
            "@5",
            "A=D-A",
            "D=M",
            "@returnAddr",
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@ARG",
            "A=M",
            "M=D",
            "@ARG",
            "D=M",
            "@SP",
            "M=D",
            "M=M+1",
        ]

        memory_segments = ["THAT", "THIS", "ARG", "LCL"]
        for index, segment in enumerate(memory_segments, start=1):
            instructions.extend(
                [
                    "@frame",
                    "D=M",
                    f"@{segment}",
                    "M=D",
                    f"@{index}",
                    "D=A",
                    f"@{segment}",
                    "M=M-D",
                    "A=M",
                    "D=M",
                    f"@{segment}",
                    "M=D",
                ]
            )
        instructions.extend(["@returnAddr", "A=M", "0;JMP"])
        self.__write_instructions(instructions)

    def __push_cmd(self, segment: str, index: int):
        if segment in self.segment_addresses:
            addr = self.segment_addresses[segment]

            if segment == "temp":
                index = int(addr) + int(index)

            instructions = [
                f"@{index}",
                "D=A",
                f"@{addr}",
                "A=D+M",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
            ]
        elif segment == "static":
            instructions = [
                f"@{self.file_name.replace('.asm', '')}.{index}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
            ]
        elif segment == "pointer":
            if index == 0:
                addr = "THIS"
            elif index == 1:
                addr = "THAT"

            instructions = [f"@{addr}", "D=M", f"@SP", "A=M", "M=D", "@SP", "M=M+1"]
        elif segment == "constant":
            instructions = [f"@{index}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"]
        self.__write_instructions(instructions)

    def __pop_cmd(self, segment: str, index: int):
        if segment in self.segment_addresses:
            addr = self.segment_addresses[segment]

            if segment == "temp":
                instructions = [
                    "@5",
                    "D=A",
                    "@addr",
                    "M=D",
                    f"@{index}",
                    "D=A",
                    "@addr",
                    "M=D+M",
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@addr",
                    "A=M",
                    "M=D",
                    "@addr",
                    "M=0",
                ]
            else:
                instructions = [
                    f"@{index}",
                    "D=A",
                    f"@{addr}",
                    "A=D+M",
                    "D=A",
                    "@addr",
                    "M=D",
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@addr",
                    "A=M",
                    "M=D",
                    "@addr",
                    "M=0",
                ]
        elif segment == "static":
            instructions = [
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{self.file_name.replace('.asm', '')}.{index}",
                "M=D",
            ]
        elif segment == "pointer":
            if index == 0:
                addr = "THIS"
            elif index == 1:
                addr = "THAT"

            instructions = [
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{addr}",
                "M=D",
            ]
        self.__write_instructions(instructions)

    def __get_push_instructions(self):
        return ["@SP", "A=M", "M=D", "@SP", "M=M+1"]
    
    def __write_instructions(self, instructions):
        for instruction in instructions:
            self.stream.write(f"{instruction}\n")
        self.instruction_written_count += len(instructions)

    def __write_and(self):
        instructions = ["@SP", "M=M-1", "A=M", "D=M", "A=A-1", "M=D&M"]
        self.__write_instructions(instructions)

    def __write_or(self):
        instructions = ["@SP", "M=M-1", "A=M", "D=M", "A=A-1", "M=D|M"]
        self.__write_instructions(instructions)

    def __write_not(self):
        instructions = ["@SP", "A=M-1", "M=!M"]
        self.__write_instructions(instructions)

    def __write_add(self):
        instructions = ["@SP", "M=M-1", "A=M", "D=M", "A=A-1", "M=M+D"]
        self.__write_instructions(instructions)

    def __write_sub(self):
        instructions = [
            "@SP",
            "M=M-1",
            "A=M-1",
            "D=M",
            "A=A+1",
            "D=D-M",
            "A=A-1",
            "M=D",
        ]
        self.__write_instructions(instructions)

    def __write_neg(self):
        instructions = ["@SP", "A=M-1", "M=-M"]
        self.__write_instructions(instructions)

    def __write_eq(self):
        jump_pos = self.instruction_written_count + 23
        instructions = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "A=A-1",
            "D=M-D",
            f"@EQUAL{jump_pos}",
            "D;JEQ",
            f"@NOTEQUAL{jump_pos}",
            "0;JMP",
            f"(EQUAL{jump_pos})",
            " @SP",
            " A=M-1",
            " M=-1",
            f" @EQEND{jump_pos}",
            " 0;JMP",
            f"(NOTEQUAL{jump_pos})",
            " @SP",
            " A=M-1",
            " M=0",
            f" @EQEND{jump_pos}",
            " 0;JMP",
            f"(EQEND{jump_pos})",
            " 0",
        ]
        self.__write_instructions(instructions)

    def __write_gt(self):
        jump_pos = self.instruction_written_count + 23
        instructions = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "A=A-1",
            "D=D-M",
            f"@GREATERTHAN{jump_pos}",
            "D;JLT",
            f"@NOTGREATERTHAN{jump_pos}",
            "0;JMP",
            f"(GREATERTHAN{jump_pos})",
            " @SP",
            " A=M-1",
            " M=-1",
            f" @EQEND{jump_pos}",
            " 0;JMP",
            f"(NOTGREATERTHAN{jump_pos})",
            " @SP",
            " A=M-1",
            " M=0",
            f" @EQEND{jump_pos}",
            " 0;JMP",
            f"(EQEND{jump_pos})",
            " 0",
        ]
        self.__write_instructions(instructions)

    def __write_lt(self):
        jump_pos = self.instruction_written_count + 23
        instructions = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "A=A-1",
            "D=D-M",
            f"@LESSTHAN{jump_pos}",
            "D;JGT",
            f"@NOTLESSTHAN{jump_pos}",
            "0;JMP",
            f"(LESSTHAN{jump_pos})",
            " @SP",
            " A=M-1",
            " M=-1",
            f" @LTEND{jump_pos}",
            " 0;JMP",
            f"(NOTLESSTHAN{jump_pos})",
            " @SP",
            " A=M-1",
            " M=0",
            f" @LTEND{jump_pos}",
            " 0;JMP",
            f"(LTEND{jump_pos})",
            "0",
        ]
        self.__write_instructions(instructions)

    def close(self):
        instructions = ["@END", "0;JMP", "(END)", " @END", " 0;JMP"]
        self.__write_instructions(instructions)
        self.stream.close()
