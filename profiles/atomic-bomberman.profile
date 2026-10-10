; Atomic Bomberman (Interplay, 1997) through Wine: DirectDraw at 640x480 in
; 256 colours, drawn by cnc-ddraw's GDI renderer (ddraw.dll in the game's
; folder, hence the override). Install your own CD with
; recipes/atomic-bomberman.yml (it writes this profile too); the game gets its
; own prefix and reads everything from C:\INTRPLAY\BOMBRMAN, no CD needed.
[application]
id = atomic-bomberman
name = Atomic Bomberman
executable = C:\INTRPLAY\BOMBRMAN\BM95.EXE
working_directory = C:\INTRPLAY\BOMBRMAN
dll_overrides = ddraw=n
prefix = atomic-bomberman
runtime = wine-wow64
architecture = pe32
graphics = gdi

[display]
desktop = 640x480
scaling = fit

[input]
preset = atomic-bomberman
player2 = atomic-bomberman-p2
