#include <stdio.h>

float avg(int count, int *value) {
    printf("Value = [%d, %d, %d]\n", value[0], value[1], value[2]);
    int total = 0;
    int sum = 0;
    for (int i = 0; i < count; i++) {
        total = total + value[i];
    }
    return total/count;
}

int main(void) {
    int studentNumber, count, i, sum;
    int mark[4] = {0};
    float average;

    count = 4;
    sum = 0;
    for (i = 0; i < count; i++) {
        mark[i] = (i+1)*30;
        sum = sum + mark[i];
        average = avg(i+1, mark);
        if (average > 40) {
            printf("%f [%d, %d, %d, %d]\n", average, mark[0], mark[1], mark[2], mark[3]);
        }
    }

    return 0;
}