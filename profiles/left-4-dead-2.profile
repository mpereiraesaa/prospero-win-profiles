; Left 4 Dead 2 Steam install
; The prefix registers .vpk files to open with bin/addoninstaller.exe via /register.
[application]
id = left-4-dead-2
name = Left 4 Dead 2
executable = C:\Games\Left4Dead2\left4dead2.exe
working_directory = C:\Games\Left4Dead2
arguments = -game left4dead2 -novid -fullscreen -w 1920 -h 1080
dll_overrides = d3d8,d3d9,d3d10core,d3d11,dxgi=n
prefix = left-4-dead-2
runtime = wine-wow64
architecture = pe32
graphics = dxvk

[display]
desktop = 1920x1080

[input]
preset = left-4-dead-2
mode = keyboard


[debug]
env = ORBIS_ARENA_MIB=1280
