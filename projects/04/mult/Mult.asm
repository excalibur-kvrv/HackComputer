// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
@count
M=0

@R2
M=0

@notr0
M=0

@notr1
M=0

@r1andnotr0
M=0

@r0andnotr1
M=0

// R1 Edge cases handling
@r1hasnegative // flag to keep track of negative r1
M=0

@R1
D=M

@R1ISZERO // Handle R1 has a zero value case
D;JEQ

@R1ISNEGATIVE
D;JLT // <0 is negative

(SECTIONR1RETURN)
  @R1 // dummy instructions does not do anything, only acts as a return point
  D=M
// end of R1 edge cases handling

// R0 Edge cases handling
@r0hasnegative // flag to keep track of negative r2
M=0

@R0
D=M

@R0ISZERO // Handle R0 has a zero value case
D;JEQ

@R0ISNEGATIVE
D;JLT // <0 is negative

(SECTIONR0RETURN)
  @R0 // dummy instructions does not do anything, only acts as a return point
  D=M
// end of zero value handling

// Addition loop, negative and positive numbers will both be added and if loop is ending, 
// sign of result is decided and assigned to result
(LOOP) 
  @R1
  D=M

  @count
  D=M-D

  @ASSIGNSIGNTORESULT
  D;JEQ

@count
M=M+1

@R0
D=M

@R2
M=M+D

@LOOP
0;JMP

// Label handling R1 is 0 case
(R1ISZERO)
  @R2
  M=0

  @END
  0;JMP

// Label handling R0 is 0 case
(R0ISZERO)
  @R2
  M=0

  @END
  0;JMP

// Label to negate R1 value
(R1ISNEGATIVE)
  @r1hasnegative
  M=1

  @R1
  M=-M // negate R1

  @SECTIONR1RETURN
  0;JMP

// Label to negate R0 value
(R0ISNEGATIVE)
  @r0hasnegative
  M=1

  @R0
  M=-M // negate R0

  @SECTIONR0RETURN
  0;JMP


(MAKER2NEGATIVE)
  @R2
  M=-M

  @END
  0;JMP


(ASSIGNSIGNTORESULT)
  // to assign sign we need to perform a xor operation if result is 1, 
  // add negative sign otherwise, no sign, xor formula -> (a&!b)|(!a&b)
  @r0hasnegative
  D=M
  
  @notr0
  M=!D

  @r1hasnegative
  D=M

  @notr1
  M=!D

  @r1andnotr0
  M=D

  @notr0
  D=M

  @r1andnotr0
  M=M&D

  @r0hasnegative
  D=M

  @r0andnotr1
  M=D

  @notr1
  D=M

  @r0andnotr1
  M=M&D
  D=M

  @r1andnotr0
  D=M|D

  @MAKER2NEGATIVE
  D-1;JEQ

  @END
  0;JMP


(END)
  @END
  0;JMP