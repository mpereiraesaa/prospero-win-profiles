; Black Mesa (your own copy, the Definitive Edition of the Half-Life 1
; remake on its own Source branch), Direct3D 9 through DXVK, at the
; console's native 1920x1080. Completes the Source set on the console with
; Half-Life 2, its episodes, Lost Coast and Portal.
;
; Setting it up (recipes/blackmesa.yml in prospero-win-profiles does all of
; it): give the recipe your installed Black Mesa folder (the one that holds
; bms.exe, bin, bms, hl2 and platform); it is copied into C:\Games\BlackMesa
; of a prefix of its own
; (/data/prospero-win/prefixes/blackmesa/drive_c/Games/BlackMesa), about
; 29 GB, with DXVK 2.6.2's DLLs in the prefix. The game itself loads its own
; DXVK (bin\thirdparty\dxvk-windows-x86\d3d9.dll, 2.6.1) unless started with
; -disabledxvk; both run on the console.
;
; - Steam: the game refuses to start without it ("Steam is not running").
;   Copies made for playing without Steam often keep Valve's steam_api.dll
;   and fake the client with a loader that starts bms.exe as a second
;   process; Wine on the console runs one process, so the recipe puts the
;   Goldberg emulator's regular 32-bit steam_api.dll (gbe_fork, pinned by
;   SHA-256) in bin\, with bin\steam_settings (language, offline account),
;   bin\steam_appid.txt (362890) and bin\steam_interfaces.txt listed from the
;   original DLL. Nothing of the game's data is changed.
; - -oldgameui: the 2020 main menu is a Qt QML scene (bin\BlackMesaUI.dll)
;   drawn through ANGLE and handed to the game as a Direct3D shared texture.
;   The console's Vulkan driver has no external memory
;   (VK_KHR_external_memory_win32), so DXVK cannot create it and the menu
;   shows its background map and nothing else. The engine's classic VGUI
;   menu has the same entries, in the game's language, and draws like the
;   HUD; with it Qt is never loaded.
; - The DualSense reaches the engine as an XInput pad. Saves go to bms\SAVE
;   inside the prefix.
;
; Checked on the PS5 2026-10-16: 15 minutes played with the DualSense from
; the classic menu, through Black Mesa Inbound into Anomalous Materials
; (bm_c0a0a to bm_c1a0b): map transitions and autosave loads take 4 to 6 s,
; direct memory peaks at 1.4 GB, and the game exits to the launcher. The
; menu's background map comes up about 40 s after the start. Frame rate not
; yet measured (set show_fps = true under [display] for the counter).
[application]
id = blackmesa
name = Black Mesa
executable = C:\Games\BlackMesa\bms.exe
working_directory = C:\Games\BlackMesa
arguments = -oldgameui -novid -fullscreen -w 1920 -h 1080
dll_overrides = d3d8,d3d9,d3d10core,d3d11,dxgi=n
prefix = blackmesa
runtime = wine-wow64
architecture = pe32
graphics = dxvk

[display]
desktop = 1920x1080

[input]
mode = xinput
