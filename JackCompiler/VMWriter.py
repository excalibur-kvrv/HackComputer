from vmtokens import CommandType, VirtualMemorySegmentType


class VMWriter:
    def __init__(self, output_file: str = None):
        self.output_file = open(output_file, "w")

    def __file_write(self, content):
        self.output_file.write(f"{content}\n")

    def writePush(self, segment: VirtualMemorySegmentType, index: int):
        self.__file_write(f"push {segment.value} {index}")

    def writePop(self, segment: VirtualMemorySegmentType, index: int):
        self.__file_write(f"pop {segment.value} {index}")

    def writeArithmetic(self, command: CommandType):
        self.__file_write(f"{command.value}")

    def writeLabel(self, label: str):
        self.__file_write(f"label {label}")

    def writeGoto(self, label: str):
        self.__file_write(f"goto {label}")

    def writeIf(self, label: str):
        self.__file_write(f"if-goto {label}")

    def writeCall(self, name: str, nArgs: int):
        self.__file_write(f"call {name} {nArgs}")

    def writeFunction(self, name: str, nVars: int):
        self.__file_write(f"function {name} {nVars}")

    def writeReturn(self):
        self.__file_write("return")

    def close(self):
        self.output_file.close()
