# Storage Allocation

## Exercises

### Exercise 4.1

> Why does a linker shuffle around segments to put segments of the same type next to each other? Wouldn't it be easier
> to leave them in the original order?

### Exercise 4.2

> When, if ever, does it matter in what order a linker allocates storage for routines? In our example, what difference
> would it make if the linker allocated newyork, mass, calif, main rather than main, calif, mass, newyork? (We'll ask
> this question again later when we discuss overlays and dynamic linking, so you can disregard those considerations
> here.)

### Exercise 4.3

> In most cases, a linker allocates similar sections sequentially, for example, the text of calif, mass, and newyork
> one after another. But it allocates all common sections with the same name on top of each other. Why?

### Exercise 4.4

> Is it a good idea to permit common blocks to be declared in different input files with the same name but different
> sizes? Why or why not?

### Exercise 4.5

> In Example 4.1, assume that the programmer has rewritten the calif routine so that the object code is now hex 1333
> long. Recompute the assigned segment locations. In Example 4.2, further assume that the data and bss sizes for the
> rewritten calif routine are 975 and 120. Recompute the assigned segment locations.

## Project

### Project 4.1

> Extend the linker skeleton from Project 3.1 to do simple UNIX-style storage allocation. Assume that the only
> interesting segments are .text, .data, and .bss. In the output file, text starts at hex 1000, the data start at the
> next multiple of 1000 after the text, and bss starts on a 4-byte boundary after the data. Your linker needs to write
> out a partial object file with the segment definitions for the output file. (You need not generate symbols,
> relocations, or data at this point.) Within your linker, be sure you have a data structure that will let you
> determine what address each segment in each input file has been assigned, because you'll need that to continue the
> project in subsequent chapters. Use the sample routines in Example 4.2 to test your allocator.

[Project 4.1](project_4_1.py)

### Project 4.2

> Implement UNIX-style common blocks, that is, scan the symbol table for undefined symbols with nonzero values and add
> space of appropriate size to the .bss segment. Don't worry about adjusting the symbol table entries (that comes in
> Chapter 5).

[Project 4.2](project_4_2.py)

### Project 4.3

> Extend the allocator developed in Project 4.1 to handle arbitrary segments in input files, combining all segments
> with identical names. A reasonable allocation strategy would be to put at location 1000 the segments with RP
> attributes, then starting at the next 1000 boundary those with RWP attributes, then on a 4-byte boundary thos with RW
> attributes. Allocate common blocks in .bss with attribute RW.

[Project 4.3](project_4_3.py)
