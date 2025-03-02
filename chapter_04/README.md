# Storage Allocation

## Exercises

### Exercise 4.1

> Why does a linker shuffle around segments to put segments of the same type next to each other? Wouldn't it be easier
> to leave them in the original order?

If the linker leaves the segments in the original order, then the linker needs to decide how to align sections that
require different permissions, for example code needs to be readable and executable and data needs to be readable and
writable. If the linker has a code segment followed by a data segment, it can align the data segment on a word boundary
but since they're likely to be in the same page, the page would need to be marked as readable, writable and executable.
If the linker instead decides to align the data to a page boundary and assign the necessary page flags, we'll end up
wasting memory and may cause issues for data and instruction caches.

### Exercise 4.2

> When, if ever, does it matter in what order a linker allocates storage for routines? In our example, what difference
> would it make if the linker allocated newyork, mass, calif, main rather than main, calif, mass, newyork? (We'll ask
> this question again later when we discuss overlays and dynamic linking, so you can disregard those considerations
> here.)

If we allocated newyork, mass, calif, main rather than main, calif, mass, newyork we'd end up with

| Name    | Text      | Data      | bss       |
| ------- | --------- | --------- | --------- |
| newyork | 1000-238f | 5000-6212 | 6a4c-7e4b |
| mass    | 2390-29a4 | 6214-6513 | 7e4c-868b |
| calif   | 29a8-32c7 | 6514-672a | 868c-878b |
| main    | 32c8-42de | 672c-6a4b | 878c-87db |

They seem similar in this case (other than the different locations for each of the modules), but we could imagine a
scenario where the padding to keep word alignment in text would eventually cause the text to go into another page.

### Exercise 4.3

> In most cases, a linker allocates similar sections sequentially, for example, the text of calif, mass, and newyork
> one after another. But it allocates all common sections with the same name on top of each other. Why?

It prevents multiple definitions for the same symbol, and as discussed this was a behaviour of the "common block" model
used by Fortran (and C?).

### Exercise 4.4

> Is it a good idea to permit common blocks to be declared in different input files with the same name but different
> sizes? Why or why not?

If the linker allocates the common block with the largest size then it won't cause any issues at runtime since any code
referencing the symbol shouldn't go past the end. It could be useful if certain modules only require a certain size, it
defers the decision of how large the common block needs at link time, rather than trying to come up with an aribtrary
maximum size beforehand.

### Exercise 4.5

> In Example 4.1, assume that the programmer has rewritten the calif routine so that the object code is now hex 1333
> long. Recompute the assigned segment locations. In Example 4.2, further assume that the data and bss sizes for the
> rewritten calif routine are 975 and 120. Recompute the assigned segment locations.

If the size of of the calif routine was now hex 1333 then we'd have

| Name    | Size |
| ------- | ---- |
| main    | 1017 |
| calif   | 1333 |
| mass    |  615 |
| newyork | 1390 |

Then the allocations might be

| Name    | Location  |
| ------- | --------- |
| main    | 1000-2016 |
| calif   | 2018-334a |
| mass    | 334c-3960 |
| newyork | 3964-4cf3 |

For Example 4.2, if also update the data and bss sizes for the calif routine we'd have

| Name    | Text | Data | bss  |
| ------- | ---- | ---- | ---- |
| main    | 1017 |  320 |   50 |
| calif   | 1333 |  975 |  120 |
| mass    |  615 |  300 |  840 |
| newyork | 1390 | 1213 | 1400 |

Then the assigned segment locations would be

| Name    | Text      | Data      | bss       |
| ------- | --------- | --------- | --------- |
| main    | 1000-2016 | 5000-531f | 71ac-71fb |
| calif   | 2018-334a | 5320-5c94 | 71fc-731b |
| mass    | 334c-3960 | 5c98-5f97 | 731c-7b5b |
| newyork | 3964-4cf3 | 5f98-71aa | 7b5c-8f5b |

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
