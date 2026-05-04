#include <stdio.h>

void returns_void(int x) {
    if (x > 0) {
        printf("Positive");
    }
}

int returns_int() {
    return 42;
}

void test_unused_local() {
    int unused_var = 10;
    int used_var = 20;
    
    printf("%d", used_var);
}

void test_identical_branches(int flag) {
    if (flag == 1) {
        returns_void(1);
        returns_int();
    } else if (flag == 2) {
        returns_void(1);
        returns_int();
    } else {
        printf("Default");
    }
}

void test_redundant_cast() {
    (void)returns_void(1);
}

void test_missing_cast() {
    returns_int();
}
