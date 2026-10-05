/* SPDX-License-Identifier: MIT */
/* San Andreas's stencil shadows build each shadow volume's silhouette with a
 * function (gta_sa.exe 1.0, 0x70FA70) that toggles one edge in a list: the
 * edge is removed if the list holds it, in either direction, and appended
 * otherwise. It finds the edge by scanning the whole list, so a shadow with
 * n edges costs O(n^2). This is the same toggle with an index from edge to
 * position, so each call is O(1), and the list it leaves is the same, entry
 * for entry, as the game's own. */
#ifndef SA_SHADOW_EDGES_H
#define SA_SHADOW_EDGES_H
#include <stdint.h>

typedef struct SaEdge {
    uint16_t a, b;
} SaEdge;

/* The game's toggle, as it is: a linear scan for the first entry equal to
 * (a, b) or (b, a). Found: the last entry moves into its place (unless it is
 * the only one) and the count drops by one. Not found: (a, b) goes at the
 * end and the count grows by one, wrapping at 16 bits as the game's does. */
void sa_edges_toggle_scan(SaEdge *edges, uint16_t *count, uint16_t a, uint16_t b);

/* The index's capacity: lists longer than SA_EDGES_INDEX_LIMIT entries are
 * toggled by the scan. */
enum { SA_EDGES_INDEX_SLOTS = 1 << 14, SA_EDGES_INDEX_LIMIT = SA_EDGES_INDEX_SLOTS / 2 };

typedef struct SaEdgeSlot {
    uint32_t key;        /* the edge's ends, smaller one high */
    uint16_t position;   /* its entry in the list */
    uint16_t generation; /* the slot is in use when this is the index's */
} SaEdgeSlot;

/* Which list the index describes: its entries, its count and the count it
 * last left there. Any call that finds a different list, or the count
 * changed by someone else (the game starts each shadow at zero), re-reads
 * the list before toggling. */
typedef struct SaEdgeIndex {
    SaEdge *edges;
    uint16_t *count;
    uint32_t expected;
    uint16_t generation;
    uint8_t valid;
    SaEdgeSlot slots[SA_EDGES_INDEX_SLOTS];
} SaEdgeIndex;

void sa_edges_index_init(SaEdgeIndex *index);
/* The game's toggle, through the index; the list and count it leaves are the
 * same as sa_edges_toggle_scan's. */
void sa_edges_toggle(SaEdgeIndex *index, SaEdge *edges, uint16_t *count, uint16_t a, uint16_t b);

#endif
