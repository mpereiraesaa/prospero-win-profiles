/* SPDX-License-Identifier: MIT */
/* sa_edges_toggle against sa_edges_toggle_scan (the game's toggle): after
 * every call the count and every listed entry must be the same. */
#include "../plugins/sa-shadow-edges/shadow_edges.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { CAPACITY = 1 << 16 };

static SaEdge want[CAPACITY], got[CAPACITY];
static uint16_t want_count, got_count;
static SaEdgeIndex index_;
static uint64_t state = 0x9e3779b97f4a7c15u;

static uint32_t next(void)
{
    state ^= state << 13; state ^= state >> 7; state ^= state << 17;
    return (uint32_t)state;
}

static void check(const char *what, unsigned step)
{
    if (want_count != got_count || memcmp(want, got, sizeof(SaEdge) * want_count)) {
        fprintf(stderr, "%s: differs at step %u (count %u vs %u)\n", what, step, want_count, got_count);
        exit(1);
    }
}

static void toggle(uint16_t a, uint16_t b)
{
    sa_edges_toggle_scan(want, &want_count, a, b);
    sa_edges_toggle(&index_, got, &got_count, a, b);
}

/* As a shadow is built: the count starts at zero, then each triangle that
 * faces the light toggles its three edges. Vertices come from a small range
 * so edges are shared and cancel. */
static void shadows(unsigned objects, unsigned vertices, unsigned triangles)
{
    for (unsigned o = 0; o < objects; o++) {
        want_count = got_count = 0;
        for (unsigned t = 0; t < triangles; t++) {
            uint16_t v[3];
            for (unsigned k = 0; k < 3; k++) v[k] = (uint16_t)(next() % vertices);
            toggle(v[0], v[1]);
            toggle(v[1], v[2]);
            toggle(v[2], v[0]);
            check("shadow", t);
        }
    }
}

int main(void)
{
    sa_edges_index_init(&index_);

    /* The basics: append, find either way round, the last entry moving into
     * a removed one's place, the only entry removed, a degenerate edge. */
    toggle(1, 2); toggle(3, 4); toggle(5, 6); check("append", 0);
    toggle(2, 1); check("reversed", 1);
    assert(got_count == 2 && got[0].a == 5 && got[0].b == 6 && got[1].a == 3 && got[1].b == 4);
    toggle(3, 4); toggle(6, 5); check("emptied", 2);
    assert(got_count == 0);
    toggle(7, 7); toggle(7, 7); check("degenerate", 3);
    toggle(9, 8); check("one", 4);
    toggle(8, 9); check("only entry", 5);
    assert(got_count == 0 && got[0].a == 9 && got[0].b == 8);  /* left in place, as the game leaves it */

    shadows(200, 24, 300);
    shadows(50, 400, 3000);
    shadows(3, 3000, 12000);

    /* Someone else changes the list, as the game does between shadows: a
     * new count, with new entries (perhaps an edge twice), or a shorter
     * list; and a different list or count variable. (Entries rewritten
     * under an unchanged count would not be noticed; nothing in the game
     * but the toggle writes a shadow's list while it is built.) */
    for (unsigned step = 0; step < 200000; step++) {
        unsigned r = next() % 1000;
        if (r == 0) {
            uint16_t n = (uint16_t)(next() % 64);
            if (n == want_count) n++;
            for (unsigned i = 0; i < n; i++) {
                want[i].a = got[i].a = (uint16_t)(next() % 40);
                want[i].b = got[i].b = (uint16_t)(next() % 40);
            }
            want_count = got_count = n;          /* may hold an edge twice */
        } else if (r == 2 && want_count) {
            want_count = got_count = (uint16_t)(next() % want_count);
        } else {
            toggle((uint16_t)(next() % 40), (uint16_t)(next() % 40));
        }
        check("external", step);
    }
    {   /* A second list and count, interleaved with the first. */
        static SaEdge other_want[64], other_got[64];
        uint16_t other_want_count = 0, other_got_count = 0;
        want_count = got_count = 0;
        for (unsigned step = 0; step < 20000; step++) {
            uint16_t a = (uint16_t)(next() % 10), b = (uint16_t)(next() % 10);
            if (step & 1) {
                sa_edges_toggle_scan(other_want, &other_want_count, a, b);
                sa_edges_toggle(&index_, other_got, &other_got_count, a, b);
                assert(other_want_count == other_got_count &&
                       !memcmp(other_want, other_got, sizeof(SaEdge) * other_want_count));
            } else {
                toggle(a, b);
                check("two lists", step);
            }
        }
    }

    /* Past the index's limit the scan takes over, and the index comes back
     * once the next shadow starts. */
    want_count = got_count = 0;
    for (unsigned i = 0; i < SA_EDGES_INDEX_LIMIT + 100; i++) toggle((uint16_t)i, (uint16_t)(i + 1));
    check("past the limit", 0);
    for (unsigned i = 0; i < 300; i++) toggle((uint16_t)(i * 7), (uint16_t)(i * 7 + 1));
    check("past the limit, toggled", 1);
    shadows(20, 100, 500);

    /* The scan's 16-bit count wraps as the game's does. */
    want_count = got_count = 0xffff;
    toggle(60000, 60001);
    check("wrap", 0);
    assert(got_count == 0);

    printf("sa_edges_toggle matches the game's toggle\n");
    return 0;
}
