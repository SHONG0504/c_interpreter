#include <stdio.h>

int rec(int a) {
    if (a < 20) {
        rec(a + 1);
    }
    printf("%d\n", a);
    return 0;
}

int main() {
    rec(0);
}