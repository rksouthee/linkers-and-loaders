# Relocation

## Exercises

### Exercise 7.1

> Why does a SPARC linker check for address overflow when relocating branch addresses but not when doing the high and
> low parts of the address in a `SETHI` sequence?

### Exercise 7.2

> In the MIPS example, a `REFHI` relocation item needs a following `PAIR` item, but a `REFLO` doesn't. Why not?

### Exercise 7.3

> References to symbols that are pseudo-registers and thread local storage are resolved as offsets from the start of
> the segment, while normal symbol references are resolved as absolute addresses. Why?

### Exercise 7.4

> We said that a.out and ECOFF relocation doesn't handle references like A - B where A and B are both global symbols.
> Can you come up with a way to fake it?

## Project

### Project 7.1

> Make the linker handle these relocation types. After the linker has created its symbol table and assigned the address
> of all of the segments and symbols, process the relocation items in each input file. Keep in mind that the relocation
> are defined to affect the actual byte values of the object data, not the hexadecimal representation. If you're
> writing your linker in perl, it's probably easiest to convert each segment of object data to a binary string using
> the perl `pack` function, to do the relocations, then to convert back to hexadecimal format using `unpack`.

### Project 7.2

> Which endianness did you assume when you handled your relocations in Project 7.1? Modify your linker to assume the
> other endianness instead.
