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

sfile = chars

for m = 1 to 50
x = 0
for n = 1 to 40
stage

; ========= draw x numbers
idraw(nbr_, n)
; ========= draw y numbers
+y = -35
stage
idraw(nbr_, m)
+y = 35


+x = -650
next n
+y = 530
next m