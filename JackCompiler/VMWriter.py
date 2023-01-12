from vmtokens import CommandType, VirtualMemorySegmentType


class VMWriter:
    def __init__(self, output_file=None):
        pass

    def writePush(self, segment: VirtualMemorySegmentType, index: int):
        pass

    def writePop(self, segment: VirtualMemorySegmentType, index: int):
        pass

    def writeArithmetic(self, command: CommandType):
        pass

    def writeLabel(self, label: str):
        pass

    def writeGoto(self, label: str):
        pass

    def writeIf(self, label: str):
        pass

    def writeCall(self, name: str, nArgs: int):
        pass

    def writeFunction(self, name: str, nArgs: int):
        pass

    def writeReturn(self):
        pass

    def close(self):
        pass
