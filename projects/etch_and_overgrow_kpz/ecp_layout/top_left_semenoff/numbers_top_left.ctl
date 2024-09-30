; Etch and overgrow
; KPZ layout only field labels
; 09.2024 TEP
; Simon Widmann
; simon.widmann@uni-wuerzburg.de

current = 25000

origin = 0, 0
x = 0
y = 0
stage

sfile = numbers_xy

for m = 1 to 46
x = 0
for n = 1 to 25
stage

; ========= draw numbers
idraw(nbr_x_, n)
idraw(nbr_y_, m)


+x = -1100
next n
+y = 600
next m