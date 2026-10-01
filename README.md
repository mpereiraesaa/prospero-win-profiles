# prospero-win profiles

Game and benchmark profiles for
[prospero-win](https://github.com/mpereiraesaa/prospero-win), the Windows
compatibility runtime for PS5 homebrew. The configurations here have been run
on a PS5; the table says what was checked. No Windows programs or game files are
included: games are your own copies, and `benchmarks/build.sh` builds the
benchmark programs from their pinned upstream sources.

## Profiles

| Profile | Program | Architecture | Checked on FW 12.02 |
|---|---|---|---|
| `minesweeper` | Wine's Minesweeper (ships with the prefix) | PE64 | Played with the stick-driven pointer |
| `pinball` | Space Cadet Pinball (your own copy, in `C:\Games\Pinball`) | PE32 | Played full-screen with the DualSense |
| `warcraft-iii-reign-of-chaos` | Warcraft III: Reign of Chaos 1.27a (your own copy and CD key; installed from `recipes/`) | PE32, Direct3D 9 | 2026-09-29: plays on RADV, DXVK 2.6.2 (menu, skirmish, cinematics with sound, centred); DualSense (`warcraft3` preset) or USB keyboard and mouse; performance not yet measured |
| `openarena-088` | OpenArena 0.8.8 official Windows build (your copy in `C:\Games\OpenArena`) | PE32, OpenGL | 2026-10-01: `GL_RENDERER: PS5 AGC`, `aggressor` bot match; no GPU present failure or rejected draw; USB keyboard and mouse for input |
| `half-life` | Half-Life 1 (your own copy in `C:\Games\HalfLife`) | PE32, OpenGL | 2026-10-01: `c1a0` scene and audio on the PS5; USB keyboard and mouse for input |
| `counter-strike-16` | Counter-Strike 1.6 (your own copy in `C:\Games\CounterStrike16`, plus winetricks `corefonts`; see the profile's comments) | PE32, OpenGL | 2026-10-01: main menu at 1920x1080 with the core fonts, 60 fps with vsync; USB keyboard and mouse |
| `sevenzip-bench` | 7-Zip 25.01 benchmark, `7za b -mmt1 -md22` | PE32 | 2026-09-28: 3361–3369 total MIPS |
| `nbench-x87` | nbench (BYTEmark 2.2.3), x87 build | PE32 | 2026-09-28: all ten tests; integer index 166.7, FP index 81.6 |
| `pi-x87` | Ooura's `pi_fftca`, 4.2M digits, x87 build | PE32 | 2026-09-28: 13 s, digits written to `pi.dat` |
| `sevenzip-bench-x64` | The same 7-Zip package's x64 `7za.exe` | PE64 | 2026-09-28: 5148–5154 total MIPS |
| `nbench-x64` | nbench, x64 build | PE64 | 2026-09-28: integer index 185.5, FP index 114.9 |
| `pi-x64` | `pi_fftca`, x64 build | PE64 | 2026-09-28: 8 s, same digits |

The PE32 benchmarks measure prospero-win's i386 translator (DBT). The PE64
builds of the same programs run natively on the console, so they are the
baseline: on the host, where both builds run natively, the x64 builds are
1.03–1.36× faster than the i386 ones, and correcting for that puts the DBT
at about 85–93% of native speed on the console. Their output arrives in the title's ps5log
stream as `STDOUT` lines, and each program exits by itself, which returns
the title to the launcher.

## Graphics modes

The profile checker accepts `graphics = auto`, `gdi`, `dxvk` or `opengl`.
`opengl` requires a prospero-win runtime built with the optional PS5 OpenGL
SDK. The runtime forces Wine's builtin `opengl32` for that profile, preserving
any other per-game DLL overrides. SDK 0.6.0 provides an EGL compatibility
profile and OpenGL 4.6 Core; Wine's legacy `wglCreateContext` path uses the
compatibility default so games can call fixed-function APIs. The upstream
compatibility-context gate covers legacy `QUADS` and related draws. OpenArena
0.8.8 and Half-Life 1 have been validated on the PS5; other games and Doom
ports still need individual checks. Both OpenGL profiles set `show_fps = true`
for the backend's small frame-rate counter without the statistics chart.

## Install

The library lives in `/data/prospero-win` on the console:

```text
/data/prospero-win/
  profiles/   *.profile and profiles.lst    ← profiles/
  input/      *.input                       ← input/
  prefix/drive_c/Tools/                     ← the benchmark programs
```

1. Copy `profiles/*.profile` and `input/*.input` there. `profiles.lst` sets
   the launcher's order; if you already have one, add these names to it
   instead of replacing it.
2. For the benchmarks, run `benchmarks/build.sh out` (it needs curl, tar,
   patch, `7z`, `i686-w64-mingw32-gcc` and `x86_64-w64-mingw32-gcc`) and
   copy everything in `out/` except `.cache` to `prefix/drive_c/Tools`.
3. For Pinball, copy your installed game to `prefix/drive_c/Games/Pinball`.
4. For OpenArena or Half-Life, copy your own Windows game files to
   `prefix/drive_c/Games/OpenArena` or `prefix/drive_c/Games/HalfLife`.

## Recipes

Games with an installer are installed on the PC and played on the PS5
(prospero-win's
[docs/INSTALLING_GAMES.md](https://github.com/mpereiraesaa/prospero-win/blob/main/docs/INSTALLING_GAMES.md)).
A recipe is a [Lutris installer
script](https://github.com/lutris/lutris/blob/master/docs/installers.rst),
adapted from lutris.net where one exists, with a `prospero` block for the
console's display and input. It holds no game files and no keys: you give
your installer, and type your key in its window.

```sh
# in prospero-win
python3 tools/pw_install.py ../prospero-win-profiles/recipes/warcraft-iii-reign-of-chaos.yml \
    --library ~/prospero-library --wine <host wine>/usr/bin/wine \
    --file installer=/path/to/War3-ROC-1.27a-Installer/Installer.exe
python3 tools/pw_prefix.py push warcraft-iii-reign-of-chaos --library ~/prospero-library \
    --host <PS5 IP> --cpu-dll <build>/dlls/wowprospero/x86_64-windows/wowprospero.dll
```

| Recipe | Notes |
|---|---|
| `warcraft-iii-reign-of-chaos` | Blizzard's 1.27a installer (it shows its license through Wine Gecko); registers `blizzard.ax`, and LAV Filters (`winetricks lavfilters`) for the cinematics, since the console's Wine has no GStreamer; RenderEdge_Widescreen (pinned by SHA-256) for 16:9; Direct3D 9 through DXVK because that route has been exercised on-console while the new WGL route remains unvalidated; 1920x1080, the console desktop's size |

## Benchmark sources

`benchmarks/build.sh` downloads each source by URL and checks its SHA-256:

- 7-Zip 25.01 "extra" (`7z2501-extra.7z`) from 7-zip.org: the i386
  `7za.exe`, with its `License.txt` (LGPL with the unRAR restriction).
- nbench-byte 2.2.3 from the University of Utah mirror, built with
  `-O2`. The x64 build also applies `benchmarks/nbench-win64.patch`:
  nbench keeps allocation addresses in a `ulong`, which is 32 bits on
  Win64, so the patch makes them `uintptr_t`.
- Takuya Ooura's `pi_fftc6_src.tgz`, with `benchmarks/pi_fftca-args.patch`
  applied: the FFT length comes from the command line instead of standard
  input, and a failed `fopen` of `pi.dat` is reported. Built with
  `-O2 -ffast-math`.

The i386 builds use x87, as engines of the early 2000s did; the x64
builds use SSE2, as every x64 compiler does. i386 SSE2 builds
(`-msse2 -mfpmath=sse`) run on the host but have not been checked on the
console yet, so they have no profiles here.

## Checks

`tools/check_profiles.py` reads every profile, preset and `profiles.lst`
by the rules of prospero-win's own parsers, so a file the title would
refuse fails here first. It also checks that each profile's `id` is its
file name, that its preset exists and that `profiles.lst` lists every
profile. CI runs it with its tests on every change, and builds the
benchmark programs weekly to catch a source that has moved.

## License

The profiles, presets, patch and script are MIT-licensed ([LICENSE](LICENSE)).
The programs they run keep their own licenses and are not distributed here.
