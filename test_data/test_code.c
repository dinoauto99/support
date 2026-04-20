#include <stdio.h>

void unused_param_test(int a, char *b) {
    printf("Only use a: %d\n", a);
}

void empty_func_test() {
    // This function does nothing
    /* literally nothing */
}

void empty_if_test() {
    int status = 0;
    if (status == 1) {
        
    }
    
    if (status == 2) ;
}

void empty_switch_test(int val) {
    switch (val) {
        
    }
}

void all_testing(int a, int bn int *c){
    if (a == 1) {
        
    }
    if (b==0){}
    switch (b){
    }
}

// Function pointer parameter test and nested macro stuff shouldn't break this too badly, 
// but we just test standard cases here.
void normal_func(int x) {
    if (x == 1) {
        printf("x is 1\n");
    }
    switch (x) {
        case 1:
            break;
    }
}
