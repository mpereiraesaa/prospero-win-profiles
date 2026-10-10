; nbench built for x64 by benchmarks/build.sh, running natively on the
; console: the baseline for nbench-x87. Put nb-x64.exe, NNET.DAT and COM.DAT
; in the prefix's drive_c/Tools.
[application]
id = nbench-x64
name = nbench (x64)
executable = C:\Tools\nb-x64.exe
working_directory = C:\Tools
prefix = default
runtime = wine-wow64
architecture = pe64
graphics = gdi
