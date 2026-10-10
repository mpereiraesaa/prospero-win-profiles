; Counter-Strike 1.6 (your own copy), drawing its OpenGL through Mesa's Zink on
; the console's Vulkan driver, at the console's native 1920x1080, starting at
; the main menu.
;
; Setting it up:
; - Install the game on your PC with prospero-win's host Wine
;   (tools/build_host_wine.sh) into a prefix, and choose the folder
;   C:\Games\CounterStrike16 in the installer. Untick its desktop and start
;   menu shortcuts: Wine would put them on your PC's own desktop and menu.
;   Tested with a non-Steam "Counter Strike Cataclysm 1.04" package (a Smart
;   Install Maker installer); it doesn't need its CD key file.
; - The menus use Verdana, Arial and Trebuchet MS, which Wine doesn't ship:
;   without them the text falls back to another font and looks wrong. Run
;   `winetricks corefonts` on that PC prefix and copy the font files from its
;   C:\windows\Fonts into the same folder of the console's prefix.
; - Copy C:\Games\CounterStrike16 into the console's prefix
;   (/data/prospero-win/prefix/drive_c/Games/CounterStrike16).
;
; hl.exe is started directly: the package's "Counter Strike.exe" launcher
; starts it as a second process, which Wine on the console doesn't do. The
; arguments are its batch file's, without -nojoy, so the DualSense works.
;
; Bots: the official bots only take bot_quota once a map's game code has
; loaded, so a +bot_quota argument does nothing. Put the lines
; "bot_join_after_player 0" and "bot_quota 9" at the end of
; cstrike\listenserver.cfg instead, and start a game from the menu.
;
; With nine bots on de_dust2 it holds 60 fps; the first seconds of a map,
; while the bots spawn and the shaders compile, can still dip.
;
; Needs prospero-win main from October 2026 or later: OpenGL games run through
; Zink (the PS5 OpenGL SDK backend is gone), the menu draws and takes the
; cursor on the current PS5 Vulkan driver, and the DualSense moves and clicks
; the menu cursor through the goldsrc preset. Older runtimes wanted an
; opengl_thread line here; current ones ignore it, so the profile no longer
; sets it.
[application]
id = counter-strike-16
name = Counter-Strike 1.6
executable = C:\Games\CounterStrike16\hl.exe
working_directory = C:\Games\CounterStrike16
arguments = -steam -game cstrike -noipx -window -w 1920 -h 1080 -gl
prefix = default
runtime = wine-wow64
architecture = pe32
graphics = opengl

[display]
desktop = 1920x1080
show_fps = true

[input]
preset = goldsrc
