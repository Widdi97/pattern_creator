; M3570 QD wafer
; Individual rings
; 07.2024 TEP
; Simon Widmann
; simon.widmann@uni-wuerzburg.de
; DBR rings
; variable ring outer diameter: 10, 20, 30, 40, 50, 60, 70, 80 um
; variable ring waaveguide width: 650, 800, 950 nm

; ========= draw rings ==========
sfile = rings
current = 25000


origin = 0, 0
x = 0
y = 0
stage



for m = 1 to 35
x = 0
for n = 1 to 5
stage

; === draw char
sfile = chars
-x = 40
stage
; place same x and y index three times

for i = 1 to 3
idraw(nbr_, m)
+y = 30
stage
idraw(nbr_, n)
-y = 30
+x = 330
stage
next i

-x = 990
+x = 40
stage

; === draw ring
sfile = rings

draw(rings_W650nm)
+x = 330
stage
draw(rings_W800nm)
+x = 330
stage
draw(rings_W950nm)
+x = 330
stage

;+x = 990
next n
+y = 210
next m
