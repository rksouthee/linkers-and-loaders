# Shared Libraries

## Exercises

### Exercise 9.1

> If you look in a `/shlib` directory on a UNIX system with shared libraries, you'll usually see three or four versions
> of each library with names like `libc_s.2.0.1` and `libc_s.3.0.0`. Why not just have the most recent one?

### Exercise 9.2

> In a stub library, why is it important to include all of the undefined globals for each routine, even if the
> undefined global refers to another routine in the shared library?

### Exercise 9.3

> What difference does it make whether a stub library is a single large executable with all of the library's symbols
> (as in COFF or Linux) or an actual library with separate modules?

## Project

### Project 9.1

> Make the linker produce static shared libraries and stub libraries from regular directory or file format libraries.
> If you haven't already done so, you'll have to add a linker flag to set the base address at which the linker
> allocates the segments. The input is a regular library and stub libraries for any other shared libraries on which
> this one depends. The output is an executable-format shared library containing the segments of all of the members of
> the input library and a stub library with a stub member corresponding to each member of the input library.

### Project 9.2

> Extend the linker to create executables using static shared libraries. Project 9.1 already has most of the work for
> searching stub libraries for symbol resolution, because the way that an executable refers to symbols in a shared
> library is the same as the way that one shared library refers to another. The linker needs to put the names of the
> required libraries in the output file, so that the run-time loader knows what to load. Have the linker create a
> segment called `.lib` that contains the names of the shared libraries as strings with a null byte separating the
> strings and two null bytes at the end. Create a symbol `_SHARED_LIBRARIES` that refers to the beginning of the `.lib`
> section, to which code in the startup routine can refer.
