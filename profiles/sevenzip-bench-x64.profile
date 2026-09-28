; The x64 7za.exe from the same 7-Zip package, running natively on the
; console: the baseline for sevenzip-bench, whose i386 build goes through
; the DBT. Put 7za-x64.exe in the prefix's drive_c/Tools
; (benchmarks/build.sh makes it).
[application]
id = sevenzip-bench-x64
name = 7-Zip benchmark (x64)
executable = C:\Tools\7za-x64.exe
working_directory = C:\Tools
arguments = b -mmt1 -md22
prefix = default
runtime = wine-wow64
architecture = pe64
graphics = gdi
