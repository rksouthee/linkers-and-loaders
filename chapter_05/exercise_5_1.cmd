@echo off
setlocal

set count=%1
set kind=%2

python exercise_5_1.py my_function %1 %2 > %2.cpp
echo %time%
cl -nologo %2.cpp main.cpp
echo %time%
erase %2.cpp
erase %2.exe
erase %2.obj
erase main.obj
