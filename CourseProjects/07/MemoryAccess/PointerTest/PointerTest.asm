@3030
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@THIS
M=D
@3040
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@THAT
M=D
@32
D=A
@SP
A=M
M=D
@SP
M=M+1
@2
D=A
@THIS
A=D+M
D=A
@addr
M=D
@SP
M=M-1
A=M
D=M
@addr
A=M
M=D
@46
D=A
@SP
A=M
M=D
@SP
M=M+1
@6
D=A
@THAT
A=D+M
D=A
@addr
M=D
@SP
M=M-1
A=M
D=M
@addr
A=M
M=D
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
A=A-1
M=M+D
@2
D=A
@THIS
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M-1
D=M
A=A+1
D=D-M
A=A-1
M=D
@6
D=A
@THAT
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
A=A-1
M=M+D
@END
0;JMP
(END)
 @END
 0;JMP