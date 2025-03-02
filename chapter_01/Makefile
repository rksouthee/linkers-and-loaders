
all: hello.txt a.txt m.txt

a.obj: a.c
	cl -nologo -c a.c

a.txt: a.obj
	dumpbin -nologo -section:.text$$mn -disasm -out:a.txt a.obj

m.obj: m.c
	cl -nologo -c m.c

m.txt: a.obj
	dumpbin -nologo -section:.text$$mn -disasm -out:m.txt m.obj

# We use /DEBUG so that we can search the disassembly for functions.
# We use /INCREMENTAL:NO so that we don't have any indirection for function
# calls, and we can just calculate the offset and jump to the necessary
# function.
hello.exe: a.obj m.obj
	link -nologo -debug -incremental:no -out:hello.exe a.obj m.obj

hello.txt: hello.exe
	dumpbin -nologo -section:.text -disasm -out:hello.txt hello.exe

clean:
	if exist a.txt erase a.txt
	if exist a.obj erase a.obj
	if exist m.txt erase m.txt
	if exist m.obj erase m.obj
	if exist hello.txt erase hello.txt
	if exist hello.obj erase hello.obj
	if exist hello.ilk erase hello.ilk
	if exist hello.pdb erase hello.pdb
	if exist hello.exe erase hello.exe
