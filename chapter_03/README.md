# Object Files

## Exercises

### Exercise 3.1

> After studying the project section following, consider whether such a text object format would be practical. (*Hint:*
> See Fraser and Hanson's paper, "A Machine-Independent Linker," in the references.)

[A Machine-Independent Linker](https://www.researchgate.net/publication/220281730_A_Machine-Independent_Linker)

## Project

### Project 3.1

> Write a perl program that reads an object file in this format and stores the contents in a suitable form in perl
> tables and arrays, then writes the file back out. The output file need not be identical to the input, although it
> should be semantically equivalent. (For example, the symbols need not be written in the same order they were read,
> although if they're reordered, the relocation entries must be adjusted to reflect the new order of the symbol table.)

> [!NOTE]
> Instead of using Perl I'll be doing the project in Python.

[Project 3.1](project_3_1.py)

#### Usage

```sh
python project_3_1.py ..\ch4main.lk ..\ch4main_copy.lk
```

Running the previous command will output

```txt
LINK
3 2 0
.text 0 1017 R
.data 2000 320 RW
.bss 2320 50 RW
main 0 1 D
wiggleroom 100 0 U
```
