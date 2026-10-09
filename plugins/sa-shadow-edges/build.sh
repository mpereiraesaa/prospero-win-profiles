#!/usr/bin/env bash
# Builds ShadowEdgeIndex.asi, the optional San Andreas plugin in this folder.
#
#   plugins/sa-shadow-edges/build.sh [output directory, default ./out]
#
# Needs i686-w64-mingw32-gcc.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
out=$(mkdir -p "${1:-out}" && cd "${1:-out}" && pwd)
i686-w64-mingw32-gcc -std=gnu11 -O2 -Wall -Wextra -Werror -shared -static-libgcc \
    -o "$out/ShadowEdgeIndex.asi" "$here/plugin.c" "$here/shadow_edges.c"
i686-w64-mingw32-strip "$out/ShadowEdgeIndex.asi"
