#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <stdalign.h>
#define N 20000000
struct __attribute__((aligned(64))) padded { long v; char pad[56]; };
struct tight { long v; };
struct tight2 { long v[8]; };
static struct tight2 shared_tight;
static struct padded pad[4];
static long plain[4];
static int mode;   /* 0 = tight (cùng cache line), 1 = padded */
void* worker(void* a){
    int i = (int)(long)a;
    for (long k=0;k<N;k++){
        if (mode==0) shared_tight.v[i]++;   /* 4 biến trên 1 dòng 64B */
        else pad[i].v++;
    }
    return NULL;
}
double run(int m){
    mode=m; pthread_t t[4]; struct timespec a,b;
    for(int i=0;i<4;i++) pthread_create(&t[i],NULL,worker,(void*)(long)i);
    clock_gettime(CLOCK_MONOTONIC,&a);
    for(int i=0;i<4;i++) pthread_join(t[i],NULL);
    clock_gettime(CLOCK_MONOTONIC,&b);
    return (b.tv_sec-a.tv_sec)+(b.tv_nsec-a.tv_nsec)/1e9;
}
int main(void){ (void)plain;
    double t0=run(0), t1=run(1);
    printf("false sharing (1 dòng 64B): %.3f s\n", t0);
    printf("padded  (mỗi biến 1 dòng): %.3f s\n", t1);
    printf("chênh: %.1f×\n", t0/t1);
    return 0;
}
