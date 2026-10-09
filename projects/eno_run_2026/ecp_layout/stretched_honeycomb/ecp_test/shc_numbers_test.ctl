; Etch and overgrow 2026, chip labels: stretched honeycomb region
; numbers_xy.pat copied from the 2024 EnO layout (labels at x 20-52 um, y 13-60 um)
; TEST: 3 x 3 chips (production: 49 x 50), pitch 550 x 540 um; must match the jdf ARRAY

current = 25000

origin = 0, 0
x = 0
y = 0
stage

sfile = numbers_xy

for m = 1 to 3
x = 0
for n = 1 to 3
stage

idraw(nbr_x_, n)
idraw(nbr_y_, m)

+x = 550
next n
+y = 540
next m


END
