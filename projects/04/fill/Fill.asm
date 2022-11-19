// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
@KBD
D=A

@count
M=D

@SCREEN
D=A

@count
M=M-D

@LOOP
0;JMP

(EMPTY)
  @curraddr
  A=M
  M=0

  @curraddr
  M=M-1

  @i
  M=M-1
  D=M

  @EMPTY
  D;JNE

  @LOOP
  D;JEQ

(FILL)
  @curraddr
  A=M
  M=-1

  @curraddr
  M=M-1

  @i
  M=M-1
  D=M

  @FILL
  D;JNE

  @LOOP
  D;JEQ
  

(LOOP)
  @count
  D=M

  @i
  M=D

  @KBD
  D=A

  @curraddr
  M=D-1

  @KBD
  D=M

  @FILL
  D;JGT

  @EMPTY
  D;JEQ
