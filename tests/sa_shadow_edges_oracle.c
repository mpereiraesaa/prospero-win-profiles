/* SPDX-License-Identifier: MIT */
/* The game's own edge toggle, run from your gta_sa.exe 1.0 (32-bit Linux
 * build, gcc -m32), against sa_edges_toggle_scan and sa_edges_toggle. The
 * function's code is read from the executable at run time; none of it is in
 * this repository.
 *
 *   sa_shadow_edges_oracle <path to gta_sa.exe> */
#define _GNU_SOURCE
#include "../plugins/sa-shadow-edges/shadow_edges.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>

enum { TOGGLE = 0x70FA70, TOGGLE_BYTES = 0x6b, CAPACITY = 1 << 16 };

static SaEdge game[CAPACITY], scan[CAPACITY], indexed[CAPACITY];
static uint16_t game_count, scan_count, indexed_count;
static SaEdgeIndex index_;
static void *code;

static uint32_t rd32(const unsigned char *p) { return p[0] | p[1] << 8 | p[2] << 16 | (uint32_t)p[3] << 24; }

static void load(const char *path)
{
    FILE *f = fopen(path, "rb");
    static unsigned char image[16 << 20];
    size_t size;
    uint32_t pe, sections, base;
    const unsigned char *section;

    if (!f) { perror(path); exit(2); }
    size = fread(image, 1, sizeof(image), f);
    fclose(f);
    pe = rd32(image + 0x3c);
    assert(size > pe + 0x100 && !memcmp(image + pe, "PE\0\0", 4));
    sections = image[pe + 6] | image[pe + 7] << 8;
    base = rd32(image + pe + 0x34);
    section = image + pe + 0x18 + (image[pe + 0x14] | image[pe + 0x15] << 8);
    for (uint32_t i = 0; i < sections; i++, section += 40) {
        uint32_t va = base + rd32(section + 12), raw = rd32(section + 16), offset = rd32(section + 20);
        if (TOGGLE >= va && TOGGLE + TOGGLE_BYTES <= va + raw) {
            code = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
            assert(code != MAP_FAILED);
            memcpy(code, image + offset + (TOGGLE - va), TOGGLE_BYTES);
            return;
        }
    }
    fprintf(stderr, "no code at 0x%x in %s\n", TOGGLE, path);
    exit(2);
}

/* The game's calling convention: list in ecx, count's address in edx, one
 * end in di, the other on the stack. ecx and edx must come back unchanged. */
static void game_toggle(uint16_t a, uint16_t b)
{
    uint32_t ecx = (uint32_t)(uintptr_t)game, edx = (uint32_t)(uintptr_t)&game_count;
    uint32_t ecx_after, edx_after;
    __asm__ volatile(
        "pushl %[b]\n\t"
        "call *%[fn]\n\t"
        "addl $4, %%esp\n\t"
        : "=c"(ecx_after), "=d"(edx_after)
        : "c"(ecx), "d"(edx), "D"((uint32_t)a), [b] "r"((uint32_t)b), [fn] "r"(code)
        : "eax", "memory", "cc");
    assert(ecx_after == ecx && edx_after == edx);
}

static uint64_t state = 0x2545f4914f6cdd1du;
static uint32_t next(void) { state ^= state << 13; state ^= state >> 7; state ^= state << 17; return (uint32_t)state; }

static void toggle(uint16_t a, uint16_t b, unsigned step)
{
    game_toggle(a, b);
    sa_edges_toggle_scan(scan, &scan_count, a, b);
    sa_edges_toggle(&index_, indexed, &indexed_count, a, b);
    if (game_count != scan_count || game_count != indexed_count ||
        memcmp(game, scan, sizeof(SaEdge) * game_count) || memcmp(game, indexed, sizeof(SaEdge) * game_count)) {
        fprintf(stderr, "differs from the game's toggle at step %u\n", step);
        exit(1);
    }
}

int main(int argc, char **argv)
{
    static const unsigned char start[] = { 0x53, 0x0f, 0xb7, 0x1a, 0x55, 0x66, 0x8b, 0x6c, 0x24, 0x0c,
                                           0x33, 0xc0, 0x85, 0xdb, 0x56, 0x7e };
    unsigned step = 0;

    if (argc != 2) { fprintf(stderr, "usage: %s gta_sa.exe\n", argv[0]); return 2; }
    load(argv[1]);
    if (memcmp(code, start, sizeof(start))) { fprintf(stderr, "not the 1.0 edge toggle\n"); return 2; }
    sa_edges_index_init(&index_);
    for (unsigned shadow = 0; shadow < 400; shadow++) {
        unsigned vertices = 4 + next() % 600, triangles = next() % 2000;
        game_count = scan_count = indexed_count = 0;
        for (unsigned t = 0; t < triangles; t++) {
            uint16_t v[3];
            for (unsigned k = 0; k < 3; k++) v[k] = (uint16_t)(next() % vertices);
            toggle(v[0], v[1], step++);
            toggle(v[1], v[2], step++);
            toggle(v[2], v[0], step++);
        }
    }
    printf("%u toggles: sa_edges_toggle and the scan match the game's code\n", step);
    return 0;
}
