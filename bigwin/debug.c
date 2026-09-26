#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define SLOTS 7
struct gambler { int win; int numbers[SLOTS]; };

void challenge(void) {
    struct gambler noob;
    noob.win = 0x67;
    fprintf(stderr, "[dbg] &noob        = %p\n", (void*)&noob);
    fprintf(stderr, "[dbg] &noob.win    = %p\n", (void*)&noob.win);
    fprintf(stderr, "[dbg] &numbers[0]  = %p\n", (void*)&noob.numbers[0]);
    fprintf(stderr, "[dbg] &numbers[6]  = %p\n", (void*)&noob.numbers[6]);
    fprintf(stderr, "[dbg] win - num[0] offset = %ld ints\n",
            ((char*)&noob.win - (char*)&noob.numbers[0]) / (long)sizeof(int));
    // which index hits win? numbers[idx] == &win => idx = (&win - &numbers[0])/4
    long idx = ((char*)&noob.win - (char*)&noob.numbers[0]) / (long)sizeof(int);
    fprintf(stderr, "[dbg] numbers[%ld] aliases win\n", idx);

    int i = 0, accum = 0;
    while (i != SLOTS) {
        int v; 
        if (scanf("%d", &v) != 1) break;
        noob.numbers[i] = v;
        accum += noob.numbers[i];
        fprintf(stderr, "[dbg] wrote numbers[%d] at %p (=%d), accum=%d, win=%#x\n",
                i, (void*)&noob.numbers[i], v, accum, noob.win);
        if (accum == 67) { fprintf(stderr,"[dbg] hit 67 -> i++\n"); i++; }
        i++;
        if (i > 20) { fprintf(stderr,"[dbg] runaway i=%d, stop\n", i); break; }
    }
    fprintf(stderr, "[dbg] final win = %#x\n", noob.win);
    if (noob.win == 0x67) puts("LOSE");
    else puts("WIN");
}
int main(){ setbuf(stdout,NULL); setbuf(stderr,NULL); challenge(); return 0; }
