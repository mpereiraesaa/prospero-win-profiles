/* SPDX-License-Identifier: MIT */
#include "shadow_edges.h"
#include <string.h>

void sa_edges_toggle_scan(SaEdge *edges, uint16_t *count, uint16_t a, uint16_t b)
{
    uint32_t n = *count;

    for (uint32_t i = 0; i < n; i++) {
        if ((edges[i].a == a && edges[i].b == b) || (edges[i].a == b && edges[i].b == a)) {
            if (n > 1) edges[i] = edges[n - 1];
            *count = (uint16_t)(n - 1);
            return;
        }
    }
    edges[n].a = a;
    edges[n].b = b;
    *count = (uint16_t)(n + 1);
}

static uint32_t edge_key(uint16_t a, uint16_t b)
{
    return a < b ? (uint32_t)a << 16 | b : (uint32_t)b << 16 | a;
}

static uint32_t home(uint32_t key)
{
    return (key * 2654435761u) >> (32 - 14);
}

_Static_assert(SA_EDGES_INDEX_SLOTS == 1 << 14, "home() takes the top 14 bits");

/* The slot holding key, or the empty slot where it would go (*found 0). */
static uint32_t find(const SaEdgeIndex *index, uint32_t key, int *found)
{
    uint32_t slot = home(key);

    while (index->slots[slot].generation == index->generation) {
        if (index->slots[slot].key == key) {
            *found = 1;
            return slot;
        }
        slot = (slot + 1) & (SA_EDGES_INDEX_SLOTS - 1);
    }
    *found = 0;
    return slot;
}

/* Linear probing's deletion: later entries of the run move back, so every
 * key stays reachable from its home slot without tombstones. */
static void erase(SaEdgeIndex *index, uint32_t slot)
{
    const uint32_t mask = SA_EDGES_INDEX_SLOTS - 1;
    uint32_t next = (slot + 1) & mask;

    while (index->slots[next].generation == index->generation) {
        uint32_t want = home(index->slots[next].key);
        /* next may move to slot when its home is not in (slot, next]. */
        if (((next - want) & mask) >= ((next - slot) & mask)) {
            index->slots[slot] = index->slots[next];
            slot = next;
        }
        next = (next + 1) & mask;
    }
    index->slots[slot].generation = (uint16_t)(index->generation - 1);
}

static void new_generation(SaEdgeIndex *index)
{
    if (++index->generation == 0) {
        memset(index->slots, 0, sizeof(index->slots));
        index->generation = 1;
    }
}

void sa_edges_index_init(SaEdgeIndex *index)
{
    memset(index, 0, sizeof(*index));
    index->generation = 1;
}

/* Index the list as it is now. A list the game's own toggles could not have
 * made (an edge twice) or one past the limit stays with the scan. */
static int rebuild(SaEdgeIndex *index, SaEdge *edges, uint16_t *count)
{
    uint32_t n = *count;

    index->edges = edges;
    index->count = count;
    index->expected = n;
    index->valid = 0;
    if (n > SA_EDGES_INDEX_LIMIT) return 0;
    new_generation(index);
    for (uint32_t i = 0; i < n; i++) {
        int found;
        uint32_t slot = find(index, edge_key(edges[i].a, edges[i].b), &found);
        if (found) return 0;
        index->slots[slot].key = edge_key(edges[i].a, edges[i].b);
        index->slots[slot].position = (uint16_t)i;
        index->slots[slot].generation = index->generation;
    }
    index->valid = 1;
    return 1;
}

void sa_edges_toggle(SaEdgeIndex *index, SaEdge *edges, uint16_t *count, uint16_t a, uint16_t b)
{
    const uint32_t key = edge_key(a, b);
    uint32_t n = *count, slot;
    int found;

    if (index->edges != edges || index->count != count || index->expected != n || !index->valid) {
        if (index->edges == edges && index->count == count && index->expected == n && !index->valid) {
            /* A list the index gave up on: the scan, until it changes. */
            sa_edges_toggle_scan(edges, count, a, b);
            index->expected = *count;
            return;
        }
        if (!rebuild(index, edges, count)) {
            sa_edges_toggle_scan(edges, count, a, b);
            index->expected = *count;
            return;
        }
    }
    slot = find(index, key, &found);
    if (found) {
        uint32_t i = index->slots[slot].position;
        if (i >= n || edge_key(edges[i].a, edges[i].b) != key) {
            /* Not what the index left there: someone else wrote the list. */
            if (!rebuild(index, edges, count)) {
                sa_edges_toggle_scan(edges, count, a, b);
                index->expected = *count;
                return;
            }
            slot = find(index, key, &found);
            i = index->slots[slot].position;
        }
        if (found) {
            if (n > 1) {
                if (i != n - 1) {
                    int last_found;
                    uint32_t last = find(index, edge_key(edges[n - 1].a, edges[n - 1].b), &last_found);
                    index->slots[last].position = (uint16_t)i;
                }
                edges[i] = edges[n - 1];
            }
            erase(index, slot);
            *count = (uint16_t)(n - 1);
            index->expected = n - 1;
            return;
        }
    }
    edges[n].a = a;
    edges[n].b = b;
    *count = (uint16_t)(n + 1);
    index->expected = n + 1;
    if (n + 1 > SA_EDGES_INDEX_LIMIT) {
        index->valid = 0;
        return;
    }
    index->slots[slot].key = key;
    index->slots[slot].position = (uint16_t)n;
    index->slots[slot].generation = index->generation;
}
