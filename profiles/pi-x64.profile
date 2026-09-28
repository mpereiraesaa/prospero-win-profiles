; pi to 4.2M digits built for x64 by benchmarks/build.sh, running natively
; on the console: the baseline for pi-x87. Put pi-x64.exe in the prefix's
; drive_c/Tools; the digits go to C:\Tools\pi.dat.
[application]
id = pi-x64
name = pi 4.2M digits (x64)
executable = C:\Tools\pi-x64.exe
working_directory = C:\Tools
arguments = 1048576
prefix = default
runtime = wine-wow64
architecture = pe64
graphics = gdi
