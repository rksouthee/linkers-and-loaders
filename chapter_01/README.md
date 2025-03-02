# 1. Linking and Loading

## Linking: A true-life example

The following notes are from following section 1.5 "Linking: A true-life example", tweaked for x64 Windows.

To compile the examples run `nmake` in a Developer Command Prompt.

If we inspect `m.txt`, which is the disassembly of `m.obj`, we see there are 2 relocations. One for the string literal
we pass to `a`, and the other for the call to `a`.

> [!NOTE]
> I thought it was worth pointing out that the name of the text section is `.text$mn` and not `.text` like we see in
> the final image. I did some research to find out why, and it seems that the MSVC linker supports merging similar
> sections by name and sorting them by the suffix used. I'm guessing the particular value of `$mn` as the suffix is
> convenient since `m` is in the middle of the alphabet allowing users to easily place code before or after.

```txt
.text$mn name
       0 physical address
       0 virtual address
      21 size of raw data
     1D3 file pointer to raw data (000001D3 to 000001F3)
     1F4 file pointer to relocation table
       0 file pointer to line numbers
       2 number of relocations
       0 number of line numbers
60500020 flags
         Code
         16 byte align
         Execute Read

main:
  0000000000000000: 48 89 54 24 10     mov         qword ptr [rsp+10h],rdx
  0000000000000005: 89 4C 24 08        mov         dword ptr [rsp+8],ecx
  0000000000000009: 48 83 EC 28        sub         rsp,28h
  000000000000000D: 48 8D 0D 00 00 00  lea         rcx,[?string@?1??main@@9@9]
                    00
  0000000000000014: E8 00 00 00 00     call        a
  0000000000000019: 90                 nop
  000000000000001A: 33 C0              xor         eax,eax
  000000000000001C: 48 83 C4 28        add         rsp,28h
  0000000000000020: C3                 ret
```

Looking at the disassembly of `hello.exe` in `hello.txt` and searching for `main` we can see that the linker has added
the relocations for the string literal and the call to `a`.

```txt
main:
  0000000140001050: 48 89 54 24 10     mov         qword ptr [rsp+10h],rdx
  0000000140001055: 89 4C 24 08        mov         dword ptr [rsp+8],ecx
  0000000140001059: 48 83 EC 28        sub         rsp,28h
  000000014000105D: 48 8D 0D 9C DF 06  lea         rcx,[14006F000h]
                    00
  0000000140001064: E8 97 FF FF FF     call        a
  0000000140001069: 90                 nop
  000000014000106A: 33 C0              xor         eax,eax
  000000014000106C: 48 83 C4 28        add         rsp,28h
  0000000140001070: C3                 ret
  0000000140001071: CC CC CC                                         ÌÌÌ
```

Since `E8` is a call instruction, the following four bytes `97 FF FF FF` are combined to form a signed 32-bit offset
from the following instruction, in this case from `0000000140001069`. In our case the offset is -105, so if we look at
the code at the address `0x140001000` we would expect to see the code for `a`.

```txt
a:
  0000000140001000: 48 89 4C 24 08     mov         qword ptr [rsp+8],rcx
```

### Incremental linking

If we don't disable incremental linking then the call to `a` has a level indirection through the ILT (Import Lookup
Table). In the output we can search for `main:`

```txt
main:
  0000000140007190: 48 89 54 24 10     mov         qword ptr [rsp+10h],rdx
  0000000140007195: 89 4C 24 08        mov         dword ptr [rsp+8],ecx
  0000000140007199: 48 83 EC 28        sub         rsp,28h
  000000014000719D: 48 8D 0D 5C DE 08  lea         rcx,[140095000h]
                    00
  00000001400071A4: E8 D6 B0 FF FF     call        @ILT+4730(a)
  00000001400071A9: 90                 nop
  00000001400071AA: 33 C0              xor         eax,eax
  00000001400071AC: 48 83 C4 28        add         rsp,28h
  00000001400071B0: C3                 ret
  00000001400071B1: CC CC CC CC CC CC CC CC CC CC CC                 ÌÌÌÌÌÌÌÌÌÌÌ
```

Here we see that the call to `a` has been relocated to `D6 B0 FF FF` which the disassembly shows as `@ILT+4730(a)`.

```txt
@ILT+4730(a):
  000000014000227F: E9 AC 4E 00 00     jmp         a
```

Where `a` is:

```txt
a:
  0000000140007130: 48 89 4C 24 08     mov         qword ptr [rsp+8],rcx
```

## Exercises

### Exercise 1.1

> What is the advantage of separating linker and loader into separate programs? Under what circumstances would a
> combined linking loader be useful?

Advantages of separating linker and loader

1. Performance - Pre-linked executables reduce runtime overhead. The linker resolves addresses and sybmols beforehand,
   making program loading faster.
2. Modularity - Separating the linker and loader allows the linker to be used independently for different purposes,
   such as static linking for libraries or debugging.
3. Flexibility - Different linking strategies (static, dynamic, or relocatable linking) can be applied without
   modifying the loader. The loader simply loads the linked program.

A combined linking loader is advantageous when runtime adaptability are required. It might be useful for Just-In-Time
(JIT) compilation.

### Exercise 1.2

> Nearly every programming language system produced in the past 50 years includes a linker. Why?

Most projects are typically divided into multiple source files and/or modules to promote reusability and
maintainability. The linker can combine these components into a single executable allowing developers to build large
programs in a modular fashion.

During development when changing a single component, only the object file for that component needs to be built and the
linker can reuse existing object files for the other components. This can improve iteration times by reducing the
amount of work to build large programs.

### Exercise 1.3

> In this chapter we've discussed linking and loading assembled or compiled machine code. Would a linker or loader be
> useful in a purely interpretive system that directly interprets source language code? How about in an interpretive
> system that turns the source into an intermediate representation like P-code or the Java Virtual Machine?

A linker or loader wouldn't be useful in a purely interpretive system since it directly reads and executes the source
code line-by-line or statement-by-statement. There is no need to resolve external references at the machine code level
since the intepreter handles function calls and variable lookups dynamically.

In an IR-based system, a linker and loader can be beneficial for module resolution, dynamic linking, and efficient
execution within the virtual machine. The linker can resolve external references between different modules of bytecode
or IR. The loader is responsible for loading the intermediate code into memory for execution by the virtual machine
(e.g. the JVM loads `.class` files).
