/* SPDX-License-Identifier: MIT */
/* The plugin's entry, called as the game calls its toggle (i686 Windows
 * program, built with plugin.c; run under Wine): the list and count come out
 * as the scan leaves them, and every register but eax is kept. */
#include "../plugins/sa-shadow-edges/shadow_edges.h"
#include <stdio.h>
#include <string.h>

void sa_shadow_edge_thunk(void);

static SaEdge got[4096], want[4096];
static uint16_t got_count, want_count;

static uint32_t in[6], out[6], stack_argument;

static int call(uint16_t a, uint16_t b)
{
    const uint32_t start[6] = { 0x11111111u, 0x22222222u, 0x33330000u | a, 0x44444444u,
                                (uint32_t)(uintptr_t)got, (uint32_t)(uintptr_t)&got_count };
    memcpy(in, start, sizeof(in));                   /* ebx esi edi ebp ecx edx; only di is the vertex */
    stack_argument = 0xabcd0000u | b;                /* only its low word is the vertex */
    __asm__ volatile(
        "pushl %%ebp\n\t"
        "pushl %%ebx\n\t"
        "pushl %%esi\n\t"
        "pushl %%edi\n\t"
        "movl %[in]+0, %%ebx\n\t"
        "movl %[in]+4, %%esi\n\t"
        "movl %[in]+8, %%edi\n\t"
        "movl %[in]+12, %%ebp\n\t"
        "movl %[in]+16, %%ecx\n\t"
        "movl %[in]+20, %%edx\n\t"
        "pushl %[arg]\n\t"
        "call _sa_shadow_edge_thunk\n\t"
        "addl $4, %%esp\n\t"
        "movl %%ebx, %[out]+0\n\t"
        "movl %%esi, %[out]+4\n\t"
        "movl %%edi, %[out]+8\n\t"
        "movl %%ebp, %[out]+12\n\t"
        "movl %%ecx, %[out]+16\n\t"
        "movl %%edx, %[out]+20\n\t"
        "popl %%edi\n\t"
        "popl %%esi\n\t"
        "popl %%ebx\n\t"
        "popl %%ebp\n\t"
        : [out] "=m"(out)
        : [in] "m"(in), [arg] "m"(stack_argument)
        : "eax", "ecx", "edx", "memory", "cc");
    sa_edges_toggle_scan(want, &want_count, a, b);
    return !memcmp(in, out, sizeof(in)) && want_count == got_count &&
           !memcmp(want, got, sizeof(SaEdge) * want_count);
}

int main(void)
{
    uint32_t state = 12345;
    for (unsigned shadow = 0; shadow < 50; shadow++) {
        got_count = want_count = 0;
        for (unsigned t = 0; t < 600; t++) {
            uint16_t v[3];
            for (unsigned k = 0; k < 3; k++) { state = state * 1664525u + 1013904223u; v[k] = (uint16_t)((state >> 16) % 50); }
            if (!call(v[0], v[1]) || !call(v[1], v[2]) || !call(v[2], v[0])) {
                printf("thunk: differs at shadow %u triangle %u\n", shadow, t);
                return 1;
            }
        }
    }
    printf("thunk: list, count and registers as the game expects\n");
    return 0;
}
