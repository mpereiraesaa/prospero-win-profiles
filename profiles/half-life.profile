; Half-Life 1: copy your own installed Windows game to C:\Games\HalfLife.
; Starts c1a0 as the hardware-validated OpenGL scene.
[application]
id = half-life
name = Half-Life OpenGL
executable = C:\Games\HalfLife\hl.exe
working_directory = C:\Games\HalfLife
arguments = -game valve -window -w 1280 -h 720 -gl +map c1a0
prefix = default
runtime = wine-wow64
architecture = pe32
graphics = opengl

[display]
desktop = 1280x720
show_fps = true
