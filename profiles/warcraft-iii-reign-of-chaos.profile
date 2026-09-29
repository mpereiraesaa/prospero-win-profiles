; Warcraft III: Reign of Chaos 1.27a through Wine, Direct3D 9 through DXVK.
; Install your own copy with recipes/warcraft-iii-reign-of-chaos.yml (it
; writes this profile too); the game gets its own prefix. War3.exe itself:
; "Warcraft III.exe" only starts it as a second process.
[application]
id = warcraft-iii-reign-of-chaos
name = Warcraft III
executable = C:\Program Files (x86)\Warcraft III\War3.exe
working_directory = C:\Program Files (x86)\Warcraft III
dll_overrides = d3d8,d3d9,d3d10core,d3d11,dxgi=n
prefix = warcraft-iii-reign-of-chaos
runtime = wine-wow64
architecture = pe32
graphics = dxvk

[display]
desktop = 1920x1080
scaling = fit

[input]
preset = mouse
