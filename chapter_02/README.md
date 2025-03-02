# 2. Architectural Issues

## Exercises

### Exercise 2.1

> Using these SPARC program instructions to answer the following questions. (These instructions aren't intended as a
> useful program, just as some instruction format examples.)
>
> ```txt
> Loc  Hex          Symbolic
> 1000 40 00 03 00  CALL X
> 1004 01 00 00 00  NOP ; no operation, for delay
> 1008 7F FF FE ED  CALL Y
> 100C 01 00 00 00  NOP
> 1010 40 00 00 02  CALL Z
> 1014 01 00 00 00  NOP
> 1018 03 37 AB 6F  SETHI r1,3648367    ; set high 22 bits of r1
> 101C 82 10 62 EF  ORI r1,r1,751       ; OR in low 10 bits of r1
> ```
>
> 1. In a `CALL` instruction, the high 2 bits are the instruction code and the low 30 bits are a signed word (not byte)
>    offset. What are the hex addresses for `X`, `Y`, and `Z`?
> 2. What does the call to `Z` at location 1010 accomplish?
> 3. The two instructions at 1018 and 101C load a 32-bit address into register 1. The `SETHI` loads the low 22 bits of
>    the register, and the `ORI` logically ORs the low 13 bits of the instruction into the register. What address will
>    register 1 contain?
> 4. If the linker moves `X` to be at location hex 2504 but doesn't change the location of the code in the example, to
>    what will it change the instruction at location 1000 so that it still refers to `X`?

1. The address for `X` is 1C04, `Y` is 0BC0, and `Z` is 101C.
2. The call to `Z` skips the `SETHI` instruction at 1018.
3. Register 1 will contain the address DEADBEEF.
4. `1000 40 00 05 40` will call `X` located at hex 2504.

### Exercise 2.2

> Use these Pentium program instructions to answer the following questions. Don't forget that the x86 is little-endian.
> ```txt
> Loc  Hex                  Symbolic
> 1000 E8 12 34 00 00       CALL A
> 1005 E8 ?? ?? ?? ??       CALL B
> 100A A1 12 34 00 00       MOV %EAX,P
> 100F 03 05 ?? ?? ?? ??    ADD %EAX,Q
> ```
>
> 1. At what location are routine `A` and data word `P` located? (*Tip:* On the x86, relative addresses are computed
>    relative to the byte address *after* the instruction.)
> 2. If routine `B` is located at address 0F00 and data word `Q` is located at address 3456, what are the byte values
>    of the `??` bytes in the example?

1. Routine `A` is located at 4417 and word `P` is located at 3412.
2.  ```txt
    Loc
    1005 E8 F6 FE FF FF
    ...
    100F 03 05 56 34 00 00
    ```

### Exercise 2.3

> Does a linker or loader need to understand every instruction in the target architecture's instruction set? If a new
> model of the target adds new instructions, will the linker need to be changed to support them? What if the model adds
> new addressing modes to existing instructions, as the 386 did relative to the 286?

A linker or loader does not need to understand every instruction in the target architecture's instruction set. They're
mainly concerned with fixing up relocations, so the linker and loader are interested in addressing modes. If a new
model of the target adds new instructions, the linker does not need to be changed to support them. If the model adds
new addressing modes to existing instructions, the linker will need to be changed to support these addressing modes.

### Exercise 2.4

> Back in the Golden Age of computing, when programmers worked in the middle of the night because that was the only
> time they could get computer time, rather than because that's when they were awake, many computers used word rather
> than byte addresses. The PDP-6 and -10, for example, had 36-bit words and 18-bit addressing, in which each
> instruction was a word with the operand address in the low half of the word. (Programs could also store addresses in
> the high half of a data word, although there was no direct instruction set support for that.) How different is
> linking for a word-addressed architecture compared to linking for a byte-addressed architecture?

The main difference lies in how addresses are treated (word vs. byte) and how relocation is performed in terms of these
units. The linker for a word-addressed machine must handle word-alignment and word-addressing, while a byte-addressed
linker deals with byte-alignment and byte-addressing.

### Exercise 2.5

> How hard would it be to build a retargatable linker, that is, one that could be built to handle different target
> architectures by changing a few specific parts of the source code for the linker? How about a multitarget linker, to
> handle code for a variety of different architectures (although not in the same linker job)?

I think that it would be quite difficult to build a retargatable or multitarget linker. That being said [LLD - The LLVM
Linker](https://lld.llvm.org/) supports a variety of architectures and operating systems.
