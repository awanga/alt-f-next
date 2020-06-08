/*
 * Make existing programs to use unbuffered stdout.
 * Some CGI scripts need this, as its output is 4KB buffered by the kernel,
 * making its output unsuitable to display as it is generated
 * 
 * Use as:
 * LD_PRELOAD="/usr/lib/unbuffer.so" <program to get its stdout unbuffered>
 */

#include <stdio.h>

__attribute__((constructor)) void f() { setvbuf(stdout,NULL,_IOLBF,0);}
