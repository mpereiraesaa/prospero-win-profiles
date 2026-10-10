# prospero-win profiles

Game and benchmark profiles for
[prospero-win](https://github.com/mpereiraesaa/prospero-win), the Windows
compatibility runtime for PS5 homebrew. The configurations here have been run
on a PS5; the table says what was checked. No Windows programs or game files are
included: games are your own copies, and `benchmarks/build.sh` builds the
benchmark programs from their pinned upstream sources.

## Profiles

The benchmark rows (`sevenzip-bench`, `nbench-*`, `pi-*`) have their profiles in
`benchmarks/profiles/`, outside the launcher's catalog.

| Profile | Program | Architecture | Checked on FW 12.02 |
|---|---|---|---|
| `minesweeper` | Wine's Minesweeper (ships with the prefix) | PE64 | Played with the stick-driven pointer |
| `pinball` | Space Cadet Pinball (your own copy, in `C:\Games\Pinball`) | PE32 | Played full-screen with the DualSense |
| `warcraft-iii-reign-of-chaos` | Warcraft III: Reign of Chaos 1.27a (your own copy and CD key; installed from `recipes/`) | PE32, Direct3D 9 | 2026-09-29: plays on RADV, DXVK 2.6.2 (menu, skirmish, cinematics with sound, centred); DualSense (`warcraft3` preset) or USB keyboard and mouse; performance not yet measured |
| `openarena-088` | OpenArena 0.8.8 official Windows build (your copy in `C:\Games\OpenArena`) | PE32, OpenGL (Zink) | 2026-10-10: the bot match it starts by itself runs at 58.5 fps on average through Zink, no window or device errors; USB keyboard and mouse for input |
| `half-life` | Half-Life 1 (your own copy in `C:\Games\HalfLife`) | PE32, OpenGL (Zink) | 2026-10-10: menu, cursor and the `c1a0` opening played through Zink with the DualSense, 56.4 fps on average in the scripted scene; USB keyboard and mouse work too |
| `counter-strike-16` | Counter-Strike 1.6 (your own copy in `C:\Games\CounterStrike16`, plus winetricks `corefonts`; see the profile's comments) | PE32, OpenGL (Zink) | 2026-10-10: menu with the core fonts and de_dust2 with nine bots at 59.9 fps through Zink; DualSense (goldsrc preset) or USB keyboard and mouse |
| `half-life-2` | Half-Life 2 (your own copy in `C:\Games\HalfLife2` of its own prefix, with DXVK 2.6.2; see the profile's comments) | PE32, Direct3D 9 | 2026-10-02: `d1_trainstation_01` and `d1_canals_01` load in about 25 s and render; a 91 s recorded train-station demo plays at 59.7 fps on average, never under 56; keyboard checked (flashlight, pause menu); needs prospero-win #289 and #296. Mouse and DualSense not yet checked |
| `gtaiv` | Grand Theft Auto IV: The Complete Edition 1.2.0.59 (your own copy in `C:\Games\GTAIV` of its own prefix, with DXVK 2.6.2; installed from `recipes/`) | PE32, Direct3D 9 | 2026-10: the open city at 1920x1080 and 60 Hz runs at roughly 54–55 fps, close to 59 on quiet streets and in the mid-40s in fights and crowds; about 90–95 s of loading to get into the game; DualSense. FusionFix works as an optional mod (see below) |
| `gta-san-andreas` | Grand Theft Auto: San Andreas 1.0 (your own copy in `C:\Games\GTASA` of its own prefix, with DXVK 2.6.2, LAV Filters and mods; installed from `recipes/`) | PE32, Direct3D 9 | 2026-10-05: 60 fps at 1920x1080 in Grove Street and on the road, intro movies with sound, DualSense through GInput; with CLEO 4, Mod Loader and Proper Shaders (preset 0) 59.3 fps average on a Los Santos drive; needs prospero-win #373 and #374, plus #380, #382, #385 and #387 for CLEO, Mod Loader and Proper Shaders |
| `sdlpop` | Prince of Persia through SDLPoP 1.23 (your own copy in `C:\Games\SDLPoP` of its own prefix; installed from `recipes/`) | PE32 | 2026-10, on FW 10.01 (not 12.02), ShadowMountPlus 1.7beta3: plays with the DualSense (XInput), L3 quicksaves, R3 quickloads and the touchpad shows the time left; software rendering (`gdi`), performance not measured |
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
`opengl` means Mesa's WGL/Zink: the game's OpenGL calls are translated to
Vulkan and drawn by the console's Vulkan driver. prospero-win's installer
puts the Zink DLLs into the game's prefix (`pw_install.py --mesa-zink DIR`,
see its `docs/INSTALLING_GAMES.md`) and the runtime selects them for that
profile while keeping any other per-game DLL overrides. The runtime also takes
`graphics = zink` as an older spelling of the same thing. OpenArena 0.8.8,
Half-Life 1 and Counter-Strike 1.6 have been played this way on the PS5 (see
the table); other games and Doom ports still need individual checks. The three
OpenGL profiles set `show_fps = true` for the small frame-rate counter.

The PS5 OpenGL SDK backend that these games used before October 2026 is gone
from prospero-win, and with it the `refresh` and `opengl_thread` display
settings: a current runtime ignores both (it logs
`PW_WINE64 ignored display refresh=... opengl_thread=...`), so the profiles
here no longer set them; the output rate is no longer a per-game setting.

## DXVK options we use

TL;DR: a few `dxvk.conf` lines (in the game's folder, or point `DXVK_CONFIG_FILE`
at a file from a profile's `[debug] env`) smooth Direct3D 9 games on the PS5.
They need the DXVK build from `github.com/mpereiraesaa/dxvk`, branch
`prospero/v2.6.2` at `a6f6dcc1` or later; older builds ignore lines they don't
know. Each was judged by playing on the console (2026-10-10).

| Line | What it does | Where it helped |
|---|---|---|
| `d3d9.padVsOutputs = True` | Programmable vertex shaders export zero for the TEXCOORD/FOG outputs they never write, so fixed-function pixel shaders can be fast-linked from precompiled parts instead of compiled in full | GTA SA with Proper Shaders: most of the hitching gone |
| `dxvk.numCompilerThreads = 4` | More pipeline-compile workers, so a new shader is ready sooner (the compile gate in winevulkan, prospero-win #676, keeps them from blocking the render thread) | GTA SA with Proper Shaders |
| `d3d9.asyncSmallReadback = True` | A small per-frame GPU readback uses the previous frame's value instead of making DXVK wait for the GPU | GTA SA (the sky colour Proper Shaders reads) |
| `d3d9.weakRenderTargetFlushHint = True` | A change of render target 0 counts as a weak hint to submit the queued work sooner | GTA IV: looked better |

Also in that build, with no option to set: threads are woken after the queue
lock is released, a texture bind only dirties its own shader stage, and no-op
depth-stencil changes are skipped. They lower the cost of DXVK's command
thread, which sat at 90 to 95% in GTA SA and GTA IV. Available but not used:
`dxvk.implicitFlushChunkScale` (when DXVK flushes by itself) and
`dxvk.logFastLinkFailures` (logs what blocked a fast link; handy to see why a
new game still compiles shaders in full).

To explore a new game: add one line at a time, play the part that hitched, and
keep only what you can see or measure. A profile can also set
`thread_scheduling`, `shared_input` and `fast_clock` under `[runtime]`, which
the GTA profiles use.

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
   instead of replacing it. The launcher reads at most 16 entries and drops
   the whole list above that, so `profiles.lst` is kept to games.
2. For the benchmarks, run `benchmarks/build.sh out` (it needs curl, tar,
   patch, `7z`, `i686-w64-mingw32-gcc` and `x86_64-w64-mingw32-gcc`) and
   copy everything in `out/` except `.cache` to `prefix/drive_c/Tools`. Their
   profiles are in `benchmarks/profiles/` and are not in `profiles.lst`: copy
   the ones you want to `profiles/` on the console and add them to its list
   while you run them.
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
| `gtaiv` | No installer: give it the GTAIV folder of your installed Complete Edition (`--file game=<that folder>`). Copies it to `C:\Games\GTAIV`, records the install folder in the registry, installs DXVK 2.6.2, and writes a `commandline.txt` with the profile's options (video memory limits lifted, 1920x1080 at 60 Hz, fullscreen, English) |

### Grand Theft Auto IV: settings and optional mods

The game keeps its graphics settings in
`C:\users\prospero\AppData\Local\Rockstar Games\GTA IV\Settings\SETTINGS.CFG`.
On the console, Wine runs as a user called `prospero`, so the game looks for
that folder rather than one named after you. The recipe makes the prefix as
that user already. If you set up a prefix by hand on your PC instead,
`pw_prefix.py push` creates the `C:\users\prospero` folders when they are
missing (prospero-win #348 and later), and you can copy your own
`SETTINGS.CFG` there.

Neither mod below is needed to play, and the recipe doesn't install them.

- **[Ultimate ASI Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader)**
  is what loads plugins (`.asi` files) into the game. It goes in the game's
  folder as `dinput8.dll`; the profile's `dinput8=n,b` override makes Wine
  use it when it is there, and changes nothing when it isn't. FusionFix's
  release includes it.
- **[FusionFix](https://github.com/ThirteenAG/GTAIV.EFLC.FusionFix)**
  fixes many of the PC version's bugs and adds options of its own. Version
  5.1.1 was tested. Unpack its release archive into the game's folder, then:
  1. Install Microsoft's D3DX9 and shader compiler DLLs in the prefix with
     [winetricks](https://github.com/Winetricks/winetricks), which takes
     them from Microsoft's DirectX June 2010 redistributable:
     `WINEPREFIX=<your library>/prefixes/gtaiv winetricks d3dx9_43 d3dcompiler_43`.
     Without them, the game hangs at the end of loading: FusionFix assembles
     its shaders with `D3DXAssembleShader`, and Wine's own version can't
     read them.
  2. Add `d3dx9_43,d3dcompiler_43=n` to the profile's `dll_overrides`, so it
     reads
     `d3d8,d3d9,d3d10core,d3d11,dxgi=n;dinput8=n,b;d3dx9_43,d3dcompiler_43=n`.

  3. If you keep FusionFix, add a `.pw-symlinks` file in its `update` folder
     (`C:\Games\GTAIV\update`) with this one line, a tab between the two
     names:

     ```
     socialclub_LOG.txt	/dev/null
     ```

     The Ultimate ASI Loader that comes with FusionFix checks `update\` for
     every file the game opens before it opens the real one. The Social Club
     log is opened over and over while you play, and prospero-win already
     sends the copy in the game's own folder to `/dev/null`. This line gives
     the check a matching link, so it finds one instead of searching the
     folder each time.

  **We play without FusionFix for now, because it costs a lot of frame rate
  on the console.** These are measured on the PS5:

  - In a side-by-side test in the city on the same build, with FusionFix's
    default settings, the game ran at 25.8 fps with it and 33.3 fps without
    it, about 22% slower.
  - Driving the same daytime save on prospero-win from October 2026, with
    the link above and prospero-win #370, which makes missed file lookups
    cheaper, the game averaged about 40 fps with FusionFix. Without it, the
    open city runs at 54–55 fps in our usual test drive. That is a different
    route, so take the gap as rough.

  Most of what remains comes from FusionFix's code hooks in the game's
  per-object work on the main and render threads, and none of its menu
  options turn those off. Turning its effects down in the menu helps only
  a little. To go back to the plain game, take FusionFix's `d3d9.dll`,
  `vulkan.dll`, `update` folder and `plugins\GTAIV.EFLC.FusionFix.*` files
  out of the game's folder and remove `;d3dx9_43,d3dcompiler_43=n` from the
  profile again.

Microsoft's DLLs and the game's files are never part of this repository;
winetricks downloads the redistributable from Microsoft.

The test runs used a small god-mode plugin of our own so long drives weren't
cut short. It isn't needed and isn't published.

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
