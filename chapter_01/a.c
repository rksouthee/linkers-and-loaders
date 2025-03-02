#include <windows.h>
#include <string.h>

void a(char* s)
{

	WriteFile(GetStdHandle(STD_OUTPUT_HANDLE), s, strlen(s), 0, 0);
}
