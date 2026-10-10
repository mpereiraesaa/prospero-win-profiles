; Grand Theft Auto IV: The Complete Edition (your own copy, version
; 1.2.0.59, with The Lost and Damned and The Ballad of Gay Tony), Direct3D 9
; through DXVK 2.6.2 (our 2.6.2-prospero2 build), at the console's native 1920x1080 and 60 Hz.
;
; How it runs on the PS5 (prospero-win main, October 2026): the open city
; plays at roughly 54 to 55 fps. Quiet streets come close to 59 fps, while
; gunfights and crowded areas dip into the mid-40s. Getting into the game
; takes about 90 to 95 seconds of loading. Tested with the DualSense.
;
; Setting it up (recipes/gtaiv.yml in prospero-win-profiles does all of it):
; - Copy the GTAIV folder of your installed copy (the folder that holds
;   GTAIV.exe, common, pc, TLAD and TBoGT) into C:\Games\GTAIV of a prefix of
;   its own (/data/prospero-win/prefixes/gtaiv/drive_c/Games/GTAIV).
; - Put our DXVK build 2.6.2-prospero2's 32-bit DLLs (github.com/mpereiraesaa/dxvk,
;   the release's x32 folder; stock 2.6.2 also runs it) in that prefix's
;   C:\windows\syswow64, as for Half-Life 2. With the prospero2 build a
;   dxvk.conf in the game's folder holding d3d9.weakRenderTargetFlushHint =
;   True (README, "DXVK options we use") looked better; the recipe writes it.
; - The game also reads its options from commandline.txt in its own folder.
;   Put the same options there as in "arguments" below. The first three stop
;   the game from capping its settings to the video memory it detects;
;   -rglLanguage en-US picks English whatever the system's language is.
;   -width and -height keep the game at 1920x1080. Without them you can pick
;   another resolution in the game's menu; prospero-win #369 and later scale
;   it to the screen. Lower resolutions didn't make the city faster.
;
; The game saves its graphics settings in
; C:\users\prospero\AppData\Local\Rockstar Games\GTA IV\Settings\SETTINGS.CFG.
; On the console Wine runs as the user "prospero", so a prefix you made by
; hand on your PC needs C:\users\prospero folders. pw_prefix.py push creates
; them when they are missing (prospero-win #348 and later).
;
; The profile starts GTAIV.exe directly. PlayGTAIV.exe is only a 64-bit
; Rockstar Games Launcher stub that starts GTAIV.exe as a second process,
; which Wine on the console does not do.
;
; Optional mods (see the README for the details):
; - Ultimate ASI Loader, as dinput8.dll in the game's folder, loads plugins.
;   The dinput8=n,b override below lets it load and is harmless without it.
; - FusionFix 5.1.1 works, but needs Microsoft's d3dx9_43 and
;   d3dcompiler_43 (winetricks d3dx9_43 d3dcompiler_43) and
;   d3dx9_43,d3dcompiler_43=n added to dll_overrides; without them the game
;   hangs at the end of loading. We play without it for now: even with the
;   tips in the README, the city runs at about 40 fps with it instead of
;   54 to 55, and most of that cost can't be switched off in its menu.
;
; The test runs used a small god-mode plugin of our own to keep long drives
; going; it isn't needed and isn't published.
[application]
id = gtaiv
name = Grand Theft Auto IV
executable = C:\Games\GTAIV\GTAIV.exe
working_directory = C:\Games\GTAIV
arguments = -availablevidmem 1536 -nomemrestrict -norestrictions -width 1920 -height 1080 -refreshrate 60 -fullscreen -rglLanguage en-US
dll_overrides = d3d8,d3d9,d3d10core,d3d11,dxgi=n;dinput8=n,b
prefix = gtaiv
runtime = wine-wow64
architecture = pe32
graphics = dxvk

[display]
desktop = 1920x1080

[input]
mode = xinput
