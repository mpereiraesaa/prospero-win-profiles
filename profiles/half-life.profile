; Half-Life 1: copy your own installed Windows game to C:\Games\HalfLife.
; Starts at the main menu, at the console's native 1920x1080. The DualSense is
; Half-Life's own gamepad (XInput); a USB keyboard and mouse work alongside it.
; The game's OpenGL goes through Mesa's Zink on the console's Vulkan driver
; (prospero-win main from October 2026 or later; the PS5 OpenGL SDK backend is
; gone, and the opengl_thread line older runtimes wanted is ignored now).
[application]
id = half-life
name = Half-Life
executable = C:\Games\HalfLife\hl.exe
working_directory = C:\Games\HalfLife
arguments = -game valve -window -w 1920 -h 1080 -gl
prefix = default
runtime = wine-wow64
architecture = pe32
graphics = opengl

[display]
desktop = 1920x1080
show_fps = true

[input]
preset = goldsrc
