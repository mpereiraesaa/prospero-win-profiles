; OpenArena 0.8.8 (official Windows build): copy your game to
; C:\Games\OpenArena. Starts aggressor with two bots as a repeatable demo.
[application]
id = openarena-088
name = OpenArena 0.8.8 OpenGL
executable = C:\Games\OpenArena\openarena.exe
working_directory = C:\Games\OpenArena
arguments = +set s_initsound 1 +set r_fullscreen 0 +set r_mode 4 +map aggressor +addbot Sarge 2 +addbot Kyonshi 2
prefix = default
runtime = wine-wow64
architecture = pe32
graphics = opengl

[display]
desktop = 800x600
show_fps = true
