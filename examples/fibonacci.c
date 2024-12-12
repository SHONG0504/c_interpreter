#include <stdio.h>

void fib(int n, int prev1, int prev2) {
    // Base Case: when n gets less than 3
    if (n < 3) {
        return;
    }
      
    int curr = prev1 + prev2;
    prev2 = prev1;
    prev1 = curr;
    printf("%d ", curr);
    return fib(n - 1, prev1, prev2);
}

void printFib(int n) {
    // When the number of terms is less than 1
    if (n < 1) {
        printf("Invalid number of terms\n");
        return;
    }
    // When the number of terms is 1
    if (n == 1) {
        printf("%d ", 0);
        return;
    }
    // When the number of terms is 2
    if (n == 2) {
        printf("%d %d", 0, 1);
        return;
    }
    // When number of terms greater than 2
    printf("%d %d ", 0, 1);
    fib(n, 0, 1);
    return;
}

int main() {
    int n = 9;
    printFib(n);
  
    return 0;
}