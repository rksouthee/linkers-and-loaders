# Dynamic Linking and Loading

## Exercises

### Exercise 10.1

> ELF shared libraries are often linked so that calls from one routine to another within a single shared library go
> through the PLT and have their addresses bound at run time. Is this useful? Why or why not?

### Exercise 10.2

> Imagine that a program calls a library routing `plugh()` that is found in a shared library, and the programmer builds
> a dynamically linked program that uses that library. Later, the system manager notices that `plugh()` is a silly name
> for a routine and installs a new version of the library that names the routine `xsazq` instead. What happens the next
> time the the programmer runs the program?

### Exercise 10.3

> If the run-time environment variable `LD_BIND_NOW` is set, the ELF dynamic loader binds all of the program's PLT
> entries at load time. What would happen in the situation in Exercise 10.2 if `LD_BIND_NOW` were set?

### Exercise 10.4

> Microsoft implemented lazy procedure binding without operating system assistance by adding some extra cleverness in
> the linker and by using the existing facilities in the operating system. How hard would it be to provide transparent
> access to shared data, avoiding the extra level of explicit pointers that the current scheme uses?

## Project

### Project 10.1

> Starting with the version of the linker from Project 8.3, extend the linker to produce shared libraries and
> executables that need shared libraries. The linker needs to take as input a list of input files to combine into the
> output executable or library as well as other shared libraries to search. The output file contains a symbol table
> with defined (exported) and undefined (imported) symbols. Relocation types are the ones for PIC files along with
> `AS4` and `RS4` for references to imported symbols.

### Project 10.2

> Write a run-time binder, that is, a program that takes an executable that uses shared libraries and resolves its
> references. It should read in the executable, then read in the necessary libraries, relocate them to non-overlapping
> available addresses, and create a logically merged symbol table. (You may want to actually create such a table, or
> you may use a list of per-file tables as ELF does.) Then resolve all of the relocations and external references. When
> you're done, all code and data should be assigned memory addresses, and all addresses in the code and data should be
> resolved and relocated to the assigned addresses.
