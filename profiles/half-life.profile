; Half-Life 1: copy your own installed Windows game to C:\Games\HalfLife.
; Starts at the main menu, at the console's native 1920x1080. The DualSense is
; Half-Life's own gamepad (XInput); a USB keyboard and mouse work alongside it.
; opengl_thread runs the game's OpenGL work on its own CPU core, beside the
; game; it needs a prospero-win runtime with the [display] opengl_thread
; setting (an older runtime refuses this profile; delete that line to use one).
[application]
id = half-life
name = Half-Life OpenGL
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
opengl_thread = true

[input]
preset = goldsrc
