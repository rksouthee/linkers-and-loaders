all: dump_object.exe example.obj

dump_object.exe: dump_object.cpp
	cl /EHsc /Zi /std:c++20 dump_object.cpp

# Use /Z7 to ensure debug information is stored in the object file
example.obj: example.cpp
	cl /Z7 /c example.cpp

clean:
	if exist dump_object.exe erase dump_object.exe
	if exist dump_object.ilk erase dump_object.ilk
	if exist dump_object.obj erase dump_object.obj
	if exist dump_object.pdb erase dump_object.pdb
	if exist example.obj erase example.obj
	if exist vc140.pdb erase vc140.pdb
