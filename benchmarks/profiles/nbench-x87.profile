; nbench (BYTEmark 2.2.3), built for i386 with x87 floating point by
; benchmarks/build.sh. Put nb-x87.exe, NNET.DAT and COM.DAT in the prefix's
; drive_c/Tools. The ten tests take about four minutes on the console; the
; indexes arrive in ps5log as STDOUT lines.
[application]
id = nbench-x87
name = nbench (x87)
executable = C:\Tools\nb-x87.exe
working_directory = C:\Tools
prefix = default
runtime = wine-wow64
architecture = pe32
graphics = gdi
