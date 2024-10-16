; Etch and overgrow
; KPZ square and triangular lattices
; 09.2024 TEP
; Simon Widmann
; simon.widmann@uni-wuerzburg.de
; variable pillar diameters: 1.8, 2.1um
; variable pillar overlaps: 0.97, 1.05, 1.1

; Fragen:
; - IF statements m�glich? -> Viertelkreis
; - Bedeutung des roten Rechtecks im .pat file
; - Exposure time realistisch?
; - 

current = 25000

origin = 0, 0
x = 0
y = 0
stage

; place fields
for m = 1 to 55
;for m = 1 to 10
x = 0
for n = 1 to 30
;for n = 1 to 6
stage

; draw characters and arrows
sfile = chars

+y = -320
stage
idraw(nbr_, n)

+x = 60
stage
draw(arrow_right)
+x = -60
+y = -35
stage
idraw(nbr_, m)
+x = 60
stage
draw(arrow_up)
+x = -60

+y = 355
stage

sfile = other_patterns
;draw overlap variation

+x = 115
+y = -355
stage
draw(overlap_series)


;+x = 70
;stage
;draw(large_square)
;+x = -185
;+y = 355
;stage

sfile = split_square
+x = 70
stage
draw(split_square)
+x = -185
+y = 355
stage


sfile = other_patterns
; ==========draw 1D ssh chains
sfile = ssh_chains
+x = 250
+y = -340
stage

; ==========short ssh chains
for s = 1 to 5
idraw(ssh_1d_short_bulk_, s)
idraw(ssh_1d_short_top_, s)
idraw(ssh_1d_short_bot_, s)
+x = 15
stage
next s
+x = -75

; ==========long ssh chains
+x = 75
+y = -20
stage
for s = 1 to 5
idraw(ssh_1d_long_bulk_, s)
idraw(ssh_1d_long_top_, s)
idraw(ssh_1d_long_bot_, s)
+x = 15
stage
next s
+x = -75
+x = -75
+y = 20

+x = -250
+y = 340
stage


; ==========draw zigzigzagzag chains
sfile = zigzigzagzag

+x = 395
+y = -383
stage
draw(dred_1um924_1um1_1um0_use)
+x = 15
stage
draw(dred_1um924_1um1_0um975_use)
+x = 15
stage
draw(dred_1um924_1um1_0um95_use)
+x = 15
stage
draw(dred_1um924_1um05_0um975_use)
+x = 15
stage
draw(dred_1um924_1um05_0um95_use)
+x = 15
stage
draw(dred_1um924_1um05_0um925_use)
+x = 15
stage
draw(dred_1um924_1um0_0um925_use)
+x = 15
stage
draw(dred_1um924_1um0_0um9_use)
+x = 15
stage
draw(dred_1um924_1um0_0um875_use)
+x = -120

+x = -395
+y = 383
stage


; ==========draw all lattices
sfile = patterns

; ====== SQ Lattice 1
draw(square_v0.97_d1800_x_1_y_1)
draw(square_v0.97_d1800_x_1_y_0)
draw(square_v0.97_d1800_x_1_y_-1)
draw(square_v0.97_d1800_x_0_y_1)
draw(square_v0.97_d1800_x_0_y_0)
draw(square_v0.97_d1800_x_0_y_-1)
draw(square_v0.97_d1800_x_-1_y_1)
draw(square_v0.97_d1800_x_-1_y_0)
draw(square_v0.97_d1800_x_-1_y_-1)

+x = 140
stage

; ====== SQ Lattice 2
draw(square_v0.97_d2100_x_1_y_1)
draw(square_v0.97_d2100_x_1_y_0)
draw(square_v0.97_d2100_x_1_y_-1)
draw(square_v0.97_d2100_x_0_y_1)
draw(square_v0.97_d2100_x_0_y_0)
draw(square_v0.97_d2100_x_0_y_-1)
draw(square_v0.97_d2100_x_-1_y_1)
draw(square_v0.97_d2100_x_-1_y_0)
draw(square_v0.97_d2100_x_-1_y_-1)

+y = -140
+x = -140
stage

; ====== SQ Lattice 3
draw(square_v1.05_d1800_x_1_y_1)
draw(square_v1.05_d1800_x_1_y_0)
draw(square_v1.05_d1800_x_1_y_-1)
draw(square_v1.05_d1800_x_0_y_1)
draw(square_v1.05_d1800_x_0_y_0)
draw(square_v1.05_d1800_x_0_y_-1)
draw(square_v1.05_d1800_x_-1_y_1)
draw(square_v1.05_d1800_x_-1_y_0)
draw(square_v1.05_d1800_x_-1_y_-1)

+x = 140
stage

; ====== SQ Lattice 4
draw(square_v1.05_d2100_x_1_y_1)
draw(square_v1.05_d2100_x_1_y_0)
draw(square_v1.05_d2100_x_1_y_-1)
draw(square_v1.05_d2100_x_0_y_1)
draw(square_v1.05_d2100_x_0_y_0)
draw(square_v1.05_d2100_x_0_y_-1)
draw(square_v1.05_d2100_x_-1_y_1)
draw(square_v1.05_d2100_x_-1_y_0)
draw(square_v1.05_d2100_x_-1_y_-1)

+y = -140
+x = -140
stage


; ====== SQ Lattice 5
draw(square_v1.1_d1800_x_1_y_1)
draw(square_v1.1_d1800_x_1_y_0)
draw(square_v1.1_d1800_x_1_y_-1)
draw(square_v1.1_d1800_x_0_y_1)
draw(square_v1.1_d1800_x_0_y_0)
draw(square_v1.1_d1800_x_0_y_-1)
draw(square_v1.1_d1800_x_-1_y_1)
draw(square_v1.1_d1800_x_-1_y_0)
draw(square_v1.1_d1800_x_-1_y_-1)

+x = 140
stage

; ====== SQ Lattice 6
draw(square_v1.1_d2100_x_1_y_1)
draw(square_v1.1_d2100_x_1_y_0)
draw(square_v1.1_d2100_x_1_y_-1)
draw(square_v1.1_d2100_x_0_y_1)
draw(square_v1.1_d2100_x_0_y_0)
draw(square_v1.1_d2100_x_0_y_-1)
draw(square_v1.1_d2100_x_-1_y_1)
draw(square_v1.1_d2100_x_-1_y_0)
draw(square_v1.1_d2100_x_-1_y_-1)

+y = 280
+x = 200
stage

; ====== TRI Lattice 1
draw(triangular_v0.97_d1800_x_1_y_1)
draw(triangular_v0.97_d1800_x_1_y_0)
draw(triangular_v0.97_d1800_x_1_y_-1)
draw(triangular_v0.97_d1800_x_0_y_1)
draw(triangular_v0.97_d1800_x_0_y_0)
draw(triangular_v0.97_d1800_x_0_y_-1)
draw(triangular_v0.97_d1800_x_-1_y_1)
draw(triangular_v0.97_d1800_x_-1_y_0)
draw(triangular_v0.97_d1800_x_-1_y_-1)

+x = 140
stage

; ====== TRI Lattice 2
draw(triangular_v0.97_d2100_x_1_y_1)
draw(triangular_v0.97_d2100_x_1_y_0)
draw(triangular_v0.97_d2100_x_1_y_-1)
draw(triangular_v0.97_d2100_x_0_y_1)
draw(triangular_v0.97_d2100_x_0_y_0)
draw(triangular_v0.97_d2100_x_0_y_-1)
draw(triangular_v0.97_d2100_x_-1_y_1)
draw(triangular_v0.97_d2100_x_-1_y_0)
draw(triangular_v0.97_d2100_x_-1_y_-1)

+y = -140
+x = -140
stage

; ====== TRI Lattice 3
draw(triangular_v1.05_d1800_x_1_y_1)
draw(triangular_v1.05_d1800_x_1_y_0)
draw(triangular_v1.05_d1800_x_1_y_-1)
draw(triangular_v1.05_d1800_x_0_y_1)
draw(triangular_v1.05_d1800_x_0_y_0)
draw(triangular_v1.05_d1800_x_0_y_-1)
draw(triangular_v1.05_d1800_x_-1_y_1)
draw(triangular_v1.05_d1800_x_-1_y_0)
draw(triangular_v1.05_d1800_x_-1_y_-1)

+x = 140
stage

; ====== TRI Lattice 4
draw(triangular_v1.05_d2100_x_1_y_1)
draw(triangular_v1.05_d2100_x_1_y_0)
draw(triangular_v1.05_d2100_x_1_y_-1)
draw(triangular_v1.05_d2100_x_0_y_1)
draw(triangular_v1.05_d2100_x_0_y_0)
draw(triangular_v1.05_d2100_x_0_y_-1)
draw(triangular_v1.05_d2100_x_-1_y_1)
draw(triangular_v1.05_d2100_x_-1_y_0)
draw(triangular_v1.05_d2100_x_-1_y_-1)

+y = -140
+x = -140
stage


; ====== TRI Lattice 5
draw(triangular_v1.1_d1800_x_1_y_1)
draw(triangular_v1.1_d1800_x_1_y_0)
draw(triangular_v1.1_d1800_x_1_y_-1)
draw(triangular_v1.1_d1800_x_0_y_1)
draw(triangular_v1.1_d1800_x_0_y_0)
draw(triangular_v1.1_d1800_x_0_y_-1)
draw(triangular_v1.1_d1800_x_-1_y_1)
draw(triangular_v1.1_d1800_x_-1_y_0)
draw(triangular_v1.1_d1800_x_-1_y_-1)

+x = 140
stage

; ====== TRI Lattice 6
draw(triangular_v1.1_d2100_x_1_y_1)
draw(triangular_v1.1_d2100_x_1_y_0)
draw(triangular_v1.1_d2100_x_1_y_-1)
draw(triangular_v1.1_d2100_x_0_y_1)
draw(triangular_v1.1_d2100_x_0_y_0)
draw(triangular_v1.1_d2100_x_0_y_-1)
draw(triangular_v1.1_d2100_x_-1_y_1)
draw(triangular_v1.1_d2100_x_-1_y_0)
draw(triangular_v1.1_d2100_x_-1_y_-1)

+y = 280
+x = 400
next n
+y = 500
next m