#include <stdio.h>

/* Multi-line comment
int fake_var = 0;
*/

char g1, g2 = 'z';
int g3 = ((-999 + 999) - 1)*2/2+1;
// g3 = -1000 - (-999);
int g4 = 9;
// g3 = -1000;
char global_var = 'a';
g1, g2 = 'y';

int f1();
int f2();
void f3();
float f4();
char f5();

int main() {
    f1();
    return 0;
}

int f1() {
    int a = -f2(), c = 9999;
    int b = -a;
    int d = -c;
    int e;
    return a + b + c;
}

int f2() {
    int a = g4;
    a = a + 1;
    int b = a;
    return g3;
}

void f3() {
    return;
}

float f4() {
    return 0.1;
}

char f5() {
    return 'z';
}

int f6(int a1, int a2) {
    return f1();
}