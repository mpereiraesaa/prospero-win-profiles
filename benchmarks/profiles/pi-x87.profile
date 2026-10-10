; pi to 4.2M digits with Takuya Ooura's pi_fftca (Gauss-Legendre with FFT
; multiplication, Super PI's method), built for i386 with x87 floating point
; by benchmarks/build.sh. Put pi-x87.exe in the prefix's drive_c/Tools. The
; argument is the FFT length; the digits go to C:\Tools\pi.dat.
[application]
id = pi-x87
name = pi 4.2M digits (x87)
executable = C:\Tools\pi-x87.exe
working_directory = C:\Tools
arguments = 1048576
prefix = default
runtime = wine-wow64
architecture = pe32
graphics = gdi
