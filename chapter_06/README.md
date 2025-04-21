# Libraries

## Exercises

### Exercise 6.1

> What should a linker do if two modules in different libraries define the symbol? Is it an error?

If two libraries define the same strong symbol, then this should be considered an error. Some linkers, `ld`, have an
option, `--allow-multiple-definition` that allows multiple definitions and the first definition will be used.

If at least one of the definitions is marked as a weak symbol the linker can use the strong symbol. If both symbols are
weak the linker can use either one or report this as another error case.

### Exercise 6.2

> Library symbol directories generally include only defined global symbols. Would it be useful to include undefined
> symbols as well?

I'm not sure on this, including undefined symbols would increase the size of the symbol directory which may not be
desired. Including undefined symbols may help provide diagnostics if we know that certain libraries are looking for
particular symbols.

### Exercise 6.3

> When sorting object files using lorder and tsort, it's possible that tsort won't be able to come up with a total
> order for the files. When will this happen, and is it a problem?

`tsort` will fail to produce an order if there is a cycle, A needs a symbol from B which needs a symbol from A. To
resolve this, the library A would need to be added multiple times to the linker, or the cyclic dependency would need to
be broken.

### Exercise 6.4

> Some library formats put the directory at the front of the library while others put it at the end. What practical
> difference does it make?

Symbol lookup might be quicker if the directory is at the front of the library since it doesn't need to read in the
whole file. Having the directory at the back may help speedup updates since it may not need to reorganize the entire
file.

### Exercise 6.5

> Describe some other situations where weak externals and weak definitions are useful.

Another case where a weak definition might be useful is providing a default implementation that can be overriden
depending on the operating system or architecture. For example one could provide a default implementation of some
algorithm, and on x64 provide an implementation that uses vector instructions. Any new platforms that would be added
could use the fallback implementation or provide their own specific implementation.

## Project

### Project 6.1

> Write a librarian that creates a directory format library from a set of object files. Be sure to do something
> reasonable with duplicate symbols. Optionally, extend the libraries so that it can take an existing library and add,
> replace, or delete modules in place.

[Project 6.1](project_6_1.py)

### Project 6.2

> Extend the linker to handle directory format libraries. When the linker encounters a library in its list of input
> files, search the library and include each module in the library that defines an undefined symbol. Be sure you
> correctly handle library modules that depend on symbols defined in other library members.

[Project 6.2](project_6_2.py)

### Project 6.3

> Write a librarian that creates a file format library from a set of object files. Note that you can't correctly write
> the `LIBRARY` line at the front of the file until you know the sizes of all of the modules. Reasonable approaches
> include writing a dummy library line, then seeking back and rewriting the line in place with the correct values;
> collecting the sizes of the input files and computing the size; or buffering the entire file in main memory.
> Optionally, extend the librarian to update an existing library (note that it's a lot harder than updating a directory
> format library).

[Project 6.3](project_6_3.py)

### Project 6.4

> Extend the linker to handle file format libraries. When the linker encounters a library in its listof input files,
> search the library and include each module in the library that defines an undefined symbol. You'll have to modify
> your routines that read object files so that they can read an object module from the middle of a library.

[Project 6.4](project_6_4.py)
