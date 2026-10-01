; Half-Life 1: copy your own installed Windows game to C:\Games\HalfLife.
; Starts at the main menu, at the console's native 1920x1080. The DualSense is
; Half-Life's own gamepad (XInput); a USB keyboard and mouse work alongside it.
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

[input]
mode = xinput
