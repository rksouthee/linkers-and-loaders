# Loading and Overlays

## Exercises

### Exercise 8.1

> Compile some small C routines with PIC and non-PIC code. How much slower is the PIC code than the non-PIC code? Is it
> slower enough to be worth having non-PIC versions of libraries for programmers who are in a hurry?

### Exercise 8.2

> In the overlay example, assume that dick and dot each call both edgar and fran, but dick and dot don't call each
> other. Restructure the overlay so that dick and dot share the same space, and adjust the structure so that the call
> tree still works. How much space does the overlay program take now?

### Exercise 8.3

> In the overlay segment table, there's no explicit marking of conflicting segments. When the overlay manager loads a
> segment and the segment's path, how does the manager determine what segments to mark as not present?

### Exercise 8.4

> In an overlay program with no exclusive calls, is it possible that a series of calls could end up jumping to unloaded
> code anyway? In the example in this chapter, what happens if rob calls bill, which calls aaron, which calls chris,
> and then the routines all return? How hard would it be for the linker or overlay manager to detect or prevent that
> problem?

## Project

### Project 8.1

> Add a feature to the linker to wrap routines. Create a linker switch
> ```sh
> -w name
> ```
> that wraps the given routine. Change all references to the named routine in the program to be references to
> `wrap_name`. (Be sure not to miss internal references within the segment in which the name is defined.) Change the
> name of the routine to `real_name`. (This lets the programmer write a wrapper routine called `wrap_name` that can
> call the original routine as `real_name`.)

### Project 8.2

> Starting with the linker skeleton from Chapter 3, write a tool that modifies an object file to wrap a name, that is,
> that causes references to `name` to turn into external references to `wrap_name` and the existing routine to be
> renamed `real_name`. Why would we want to use such a program rather than building the feature into the linker?
> (*Hint:* Consider the case where you're not the author or maintainer of the linker.)

### Project 8.3

> Add support to the linker to produce executables with position-independent code. Add the following new 4-byte
> relocation types:
> ```txt
> loc seg ref GA4
> loc seg ref GP4
> loc seg ref GR4
> loc seg ref ER4
> ```
> The types have the following roles:
> 1. `GA4` (GOT address). At location `loc`, store the distance to the GOT.
> 2. `GP4` (GOT pointer). Put a pointer to symbol `ref` in the GOT, and at location `loc`, store the GOT-relative
>    offset of that pointer.
> 3. `GR4` (GOT relative). Location `loc` contains an address in segment `ref`; replace that with the offset from the
>    beginning of the GOT to that address.
> 4. `ER4` (Executable relative). Location `loc` contains an address relative to the beginning of the executable. The
>    `ref` field is ignored.
> In your linker's first pass, look for `GP4` relocation entries, build a GOT segment with all the required pointers,
> and allocate the GOT segment just before the data and bss segments. In the second pass, handle the `GA4`, `GP4`, and
> `GR4` entries. In the output file, create `ER4` relocation entries for any data that would have to be relocated if
> the output file were loaded at other than its nominal address. This would include anything marked by an `A4` or `AS4`
> relocation entry in the input. (*Hint:* Don't forget the GOT.)

