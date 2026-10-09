; C5829 QD wafer
; Ring-WG Coupling
; 08.2025 TEP
; Simon Widmann
; simon.widmann@uni-wuerzburg.de
; DBR rings
;20um rings with variable ring-wg distance: 100, 200, 300, 400, 500 and 600nm


; ========= draw rings ==========
sfile = ring_wg_dist_patterns
current = 25000


origin = 0, 0
x = 0
y = 0
stage



for m = 1 to 30
x = 0
for n = 1 to 15
stage

; === draw x 
sfile = numbers_x
idraw(nbr_, n)

sfile = numbers_y
idraw(nbr_, m)


; === draw rings
sfile = ring_wg_dist_patterns
for i = 1 to 6
idraw(wg_ring_,  i)
next i


+x = 500
next n
+y = 300
next m
