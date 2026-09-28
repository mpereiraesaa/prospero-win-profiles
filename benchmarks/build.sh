#!/usr/bin/env bash
# Builds the benchmark programs the profiles run, from pinned upstream
# sources, into an output directory whose contents go in the prefix's
# drive_c/Tools. Nothing downloaded or built here is committed.
#
#   benchmarks/build.sh [output directory, default ./out]
#
# Needs curl, tar, patch, 7z (p7zip), i686-w64-mingw32-gcc and
# x86_64-w64-mingw32-gcc. The x64 builds run natively on the console and
# are the baseline the i386 builds, which go through the DBT, compare with.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
out=$(mkdir -p "${1:-out}" && cd "${1:-out}" && pwd)
cache=$out/.cache
mkdir -p "$cache"
cc=i686-w64-mingw32-gcc
cc64=x86_64-w64-mingw32-gcc

fetch() {  # url sha256 file
    [[ -f $cache/$3 ]] || curl -fsSL -o "$cache/$3" "$1"
    echo "$2  $cache/$3" | sha256sum -c --quiet - || {
        echo "checksum mismatch for $3" >&2; exit 1; }
}

# 7-Zip 25.01 "extra": the i386 7za.exe and the x64 one. LGPL with the
# unRAR restriction; its License.txt goes beside them.
fetch https://www.7-zip.org/a/7z2501-extra.7z \
    cd3cf38085c2cc6839cf72716dafb3175ae425f4fd34faafc6c0b64d618d307f 7z2501-extra.7z
7z x -y -o"$cache/7z" "$cache/7z2501-extra.7z" 7za.exe x64/7za.exe License.txt >/dev/null
cp "$cache/7z/7za.exe" "$out/7za.exe"
cp "$cache/7z/x64/7za.exe" "$out/7za-x64.exe"
cp "$cache/7z/License.txt" "$out/7za-License.txt"

# nbench (BYTEmark 2.2.3), x87 and x64 builds. NNET.DAT and COM.DAT are its
# inputs. nbench-win64.patch keeps allocation addresses in uintptr_t, not a
# 32-bit ulong (Win64's long is 32 bits); the x87 build is made without it.
fetch https://www.math.utah.edu/~mayer/linux/nbench-byte-2.2.3.tar.gz \
    723dd073f80e9969639eb577d2af4b540fc29716b6eafdac488d8f5aed9101ac nbench-byte-2.2.3.tar.gz
rm -rf "$cache/nbench-byte-2.2.3"
tar xzf "$cache/nbench-byte-2.2.3.tar.gz" -C "$cache"
(
    cd "$cache/nbench-byte-2.2.3"
    : > pointer.h                     # 32-bit pointers: nothing to define
    cp sysinfo.c.example sysinfo.c    # no host description in the report
    cp sysinfoc.c.example sysinfoc.c
    $cc -O2 -w -o "$out/nb-x87.exe" nbench0.c nbench1.c emfloat.c misc.c sysspec.c -lm
    patch -s -p1 < "$here/nbench-win64.patch"
    $cc64 -O2 -w -o "$out/nb-x64.exe" nbench0.c nbench1.c emfloat.c misc.c sysspec.c -lm
    cp NNET.DAT COM.DAT "$out/"
)

# pi: Takuya Ooura's pi_fftca with the FFT length taken from the command
# line and a checked fopen (pi_fftca-args.patch), x87 and x64 builds.
fetch https://www.kurims.kyoto-u.ac.jp/~ooura/pi_fftc6_src.tgz \
    1b71a8dd76c964071352ddf4604aba0a348dfd4a5e4d7455bf0670a7ce097cb9 pi_fftc6_src.tgz
rm -rf "$cache/pi" && mkdir -p "$cache/pi"
tar xzf "$cache/pi_fftc6_src.tgz" -C "$cache/pi"
(
    cd "$cache/pi"/pi_fftc6
    patch -s -p1 < "$here/pi_fftca-args.patch"
    $cc -O2 -ffast-math -o "$out/pi-x87.exe" pi_fftca.c fftsgx.c -lm
    $cc64 -O2 -ffast-math -o "$out/pi-x64.exe" pi_fftca.c fftsgx.c -lm
)

echo "built into $out:"
ls "$out"
