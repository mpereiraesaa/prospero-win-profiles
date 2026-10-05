/* SPDX-License-Identifier: MIT */
/* ShadowEdgeIndex.asi: replaces San Andreas 1.0's stencil-shadow edge toggle
 * (0x70FA70) with sa_edges_toggle. The Ultimate ASI Loader loads it from the
 * game's scripts folder. It checks the function's first bytes and leaves the
 * game alone if they are not the 1.0 executable's. */
#include <windows.h>
#include "shadow_edges.h"

#define TOGGLE_ADDRESS 0x70FA70u

/* The start of the 1.0 function: push ebx; movzx ebx, word [edx]; push ebp;
 * mov bp, [esp+0xc]; xor eax, eax; test ebx, ebx; push esi; jle. */
static const unsigned char expected[] = {
    0x53, 0x0f, 0xb7, 0x1a, 0x55, 0x66, 0x8b, 0x6c, 0x24, 0x0c,
    0x33, 0xc0, 0x85, 0xdb, 0x56, 0x7e,
};

static SaEdgeIndex edge_index;
static DWORD owner;

static DWORD current_thread(void)
{
    DWORD id;
    __asm__ volatile("movl %%fs:0x24, %0" : "=r"(id));
    return id;
}

/* The game's shadow code runs on its main thread; a call from any other
 * thread gets the game's own scan, so the index is never shared. */
void __cdecl sa_shadow_edge_toggle(SaEdge *edges, uint16_t *count, uint32_t a, uint32_t b)
{
    DWORD thread = current_thread();

    if (!owner) owner = thread;
    if (thread != owner) {
        sa_edges_toggle_scan(edges, count, (uint16_t)a, (uint16_t)b);
        return;
    }
    sa_edges_toggle(&edge_index, edges, count, (uint16_t)a, (uint16_t)b);
}

/* The game calls the toggle with the list in ecx, the count's address in
 * edx, one end in di and the other as its only stack argument, which the
 * caller pops. It keeps ebx, esi, edi, ebp, ecx and edx (a caller relies on
 * ecx between two calls); this keeps them all and changes only eax. */
__attribute__((naked)) void sa_shadow_edge_thunk(void)
{
    __asm__ volatile(
        "push %ecx\n\t"
        "push %edx\n\t"
        "movl 12(%esp), %eax\n\t"   /* the stack argument: the other end */
        "push %eax\n\t"
        "push %edi\n\t"
        "push %edx\n\t"
        "push %ecx\n\t"
        "call _sa_shadow_edge_toggle\n\t"
        "addl $16, %esp\n\t"
        "pop %edx\n\t"
        "pop %ecx\n\t"
        "ret\n\t");
}

static void install(void)
{
    unsigned char *target = (unsigned char *)(uintptr_t)TOGGLE_ADDRESS;
    MEMORY_BASIC_INFORMATION info;
    DWORD old;
    LONG rel;

    if (!VirtualQuery(target, &info, sizeof(info)) || info.State != MEM_COMMIT ||
        memcmp(target, expected, sizeof(expected))) {
        OutputDebugStringA("ShadowEdgeIndex: not San Andreas 1.0's edge toggle at 0x70FA70; left alone\n");
        return;
    }
    if (!VirtualProtect(target, 5, PAGE_EXECUTE_READWRITE, &old)) return;
    rel = (LONG)((uintptr_t)sa_shadow_edge_thunk - ((uintptr_t)target + 5));
    target[0] = 0xe9;
    memcpy(target + 1, &rel, sizeof(rel));
    VirtualProtect(target, 5, old, &old);
    FlushInstructionCache(GetCurrentProcess(), target, 5);
    OutputDebugStringA("ShadowEdgeIndex: edge toggle replaced\n");
}

BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved)
{
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(instance);
        sa_edges_index_init(&edge_index);
        install();
    }
    return TRUE;
}
