; 7-Zip's built-in benchmark on one thread, the yardstick FEX and box64
; publish: it measures prospero-win's i386 translator. Put the i386 7za.exe
; from the official 7-Zip "extra" package in the prefix's drive_c/Tools
; (benchmarks/build.sh fetches it). The report arrives in ps5log as STDOUT
; lines, and the program exits by itself.
[application]
id = sevenzip-bench
name = 7-Zip benchmark
executable = C:\Tools\7za.exe
working_directory = C:\Tools
arguments = b -mmt1 -md22
prefix = default
runtime = wine-wow64
architecture = pe32
graphics = gdi
