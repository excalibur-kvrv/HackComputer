# Hack Computer

This repo contains the WIP implementation of the Hack Computer based on the book "Elements of computing systems 2nd edition".

Constuction of the computer is divided into two parts:-
1. Hardware System
2. Software System

## The Hardware System contains the below implementations
- [x] Elementary circuits like DMUX, XOR, MUX, etc implemented in a Hardware description language.
- [ ] ALU, Adder, etc ciruits for performing boolean arithmetic based on input bits.
- [ ] Memory ciruits like RAM, Registers, etc for storing bits.
- [ ] A Computer architecture for connecting the Arithmetic and Memory circuits to realize the Hack Computer.


## The Software System contains the below implementations

- [x] A HackAssembler for translating Assembly programs to 16-bit words that can run on the Hack computer.
- [x] A VM translator for translating VM(Virtual machine) code to Assembly.
- [x] A Compiler for the Jack programming language which generates VM(Virtual machine) code.
- [ ] JackOS containing key algorithms/libraries for Memory management, Math, I/O, String and Array processing support written in Jack.
- [x] A Tic Tac Toe game written in Jack that runs on top of the Hack computer. 