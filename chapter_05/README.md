# Symbol Management

## Exercises

### Exercise 5.1

> Write a C++ program with a lot of functions whose mangled names differ only in the last few characters. See how long
> they take to compile. Change them so the mangled names differ in the first few characters. Time a compile and link
> again. Do you need a new linker?

I didn't notice much of a difference between the two test cases. I suspect modern compiler toolchains have efficient
symbol tables.  Can run

```sh
exercise_5_1 100000 prefix
exercise_5_1 100000 postfix
```

to generate the C++ source files and time compiling and linking them. Both versiosn took around ~13 seconds to compile
and link on my machine.

### Exercise 5.2

> Investigate the debug symbol format that your favorite linker uses. (Some on-line resources are listed in the
> references.) Write a program to dump the debugging symbols from an object file and see how much of the source program
> you can reconstruct from it.

The file, `dump_object.cpp`, contains code to dump the debugging information from a COFF object file. Windows COFF uses
the CodeView debug format.

The following example will build the program and a an object file we can inspect, and run the program to dump the debug
information to a file.

```sh
nmake all
dump_object.exe example.obj > debug.txt
```

## Project

### Project 5.1

> Extend the linker to handle symbol resolution. Make the linker read the symbol tables from each file and create a
> global symbol table that subsequent parts of the linker can use. Each symbol in the global symbol table needs to
> include, along with the name, whether the symbol is defined and which module defines it. Be sure to check for
> undefined and multiply defined symbols.

[Project 5.1](project_5_1.py)

### Project 5.2

> Add symbol value resolution to the linker. Because most symbols are defined relative to segments in linker input
> files, the value of each symbol has to be adjusted to account for the address to which each segment is relocated. For
> example, if a symbol is defined as location 42 within a file's text segment and the segment is relocated to 3710, the
> symbol becomes 3752.

[Project 5.2](project_5_2.py)

### Project 5.3

> Finish the work from Project 4.2; make the linker handle UNIX-style common blocks. Assign location values to each
> common block.

[Project 5.3](project_5_3.py)
