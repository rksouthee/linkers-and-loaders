# Advanced Techniques

## Exercises

### Exercise 11.1

> How long does the linker you use take to link a fairly large program? Test your linker to see what it sepnds its time
> doing. (Even without linker source code you can probably do a system call trace, which should give you a pretty good
> idea.)

### Exercise 11.2

> Look at the generated code from a compiler for C++ or another object-oriented language. How much better could a
> link-time optimizer make it? What information could the compiler put in the object module to make it easier for the
> linker to do interesting optimizations? How badly do shared libraries mess up this plan?

### Exercise 11.3

> Sketch out a tokenized assembler language for your favorite CPU to use as an object language. What's a good way to
> handle symbols in the program?

### Exercise 11.4

> The AS/400 uses binary translation to provide binary code compatibility among different machine models. Other
> architectures--including the IBM 360/370/390, the DEC VAX, and the Intel x86--use microcode to implement the same
> instruction set on different underlying hardware. What are the advantages of the AS/400 scheme? Of microcoding? If
> you were defining a computer architecture today, which would you use?

## Project

### Project 11.1

> Add a garbage collector to your linker. Assume that each input file may have multiple text segments names `.text1`,
> `.text2`, and so forth. Build a global definition/reference data structure using the symbol table and relocation
> entries and identify the sections that are unreferenced. You'll have to add a command line flag to mark the startub
> stub as referenced. (What would happen if you didn't?) After the garbage collector runs, update the segment
> allocations to squeeze out space used by deleted segments.
>
> Improve the garbage collector to make it iterative. After each pass, update the definition/reference structure to
> remove references from logically deleted segments and run it again, repeating until nothing further is deleted.
