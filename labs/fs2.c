#define _GNU_SOURCE
#include <stdio.h>
#include <pthread.h>
#include <time.h>
#define N 20000000
static volatile long same_line[4];               /* 4 biến chung 1 dòng 64B */
static volatile long padded[4][8];               /* mỗi biến 1 dòng */
static int mode;
void* worker(void* a){
    int i=(int)(long)a;
    if(mode==0) for(long k=0;k<N;k++) same_line[i]=same_line[i]+1;
    else        for(long k=0;k<N;k++) padded[i][0]=padded[i][0]+1;
    return 0;
}
double run(int m){ mode=m; pthread_t t[4]; struct timespec a,b;
    clock_gettime(CLOCK_MONOTONIC,&a);
    for(int i=0;i<4;i++) pthread_create(&t[i],0,worker,(void*)(long)i);
    for(int i=0;i<4;i++) pthread_join(t[i],0);
    clock_gettime(CLOCK_MONOTONIC,&b);
    return (b.tv_sec-a.tv_sec)+(b.tv_nsec-a.tv_nsec)/1e9; }
int main(void){ double a=run(0), b=run(1);
    printf("chung dong 64B : %.3f s\n", a);
    printf("moi bien 1 dong: %.3f s\n", b);
    printf("chenh: %.1fx\n", a/b); return 0; }
