; Etch and overgrow
; OptiTopo
; 09.2024 TEP
; Simon Betzold
; simon.betzold@uni-wuerzburg.de
; pillar diameters: 1.7, 2.0um
; variable pillar overlaps: 0.85 - 1.20

; =====================

current = 25000

origin = 0, 0
x = 0
y = 0
stage

; =====================
;place fields
; =====================

;for m = 1 to 30
;x = 0
;for n = 1 to 30
;stage

; =====================
;draw characters and arrows
; =====================

sfile = other_patterns_SB

; =====================

draw(arrow_left)
draw(arrow_down)


; =====================
; Overlap series (Moleküle Array)
; =====================

draw(overlap_series)

; =====================
;Einzelne Hexagons 1.7um - 2um
; =====================

sfile = hexagons_res25_peak

; =====================

draw (hexagon_peak_1p7, 16, 80.00)
draw (hexagon_peak_2p0, 16, 80.00)
draw (hexagon_peak_2p5, 16, 80.00)


; =====================
;Honeycomb TOPO d1.7
; =====================

sfile = HC_TOPO_EnO_d1.7_res_25_4x4_SB

; =====================

;1
draw (VA1p2_VB1p2_1, 16, 60.00)
draw (VA1p2_VB1p2_2, 16, 60.00)
draw (VA1p2_VB1p2_3, 16, 70.00)
draw (VA1p2_VB1p2_4, 16, 70.00)
draw (VA1p2_VB1p2_5, 16, 70.00)

;2
draw (VA1p0_VB1p0_1, 16, 60.00)
draw (VA1p0_VB1p0_2, 16, 60.00)
draw (VA1p0_VB1p0_3, 16, 70.00)
draw (VA1p0_VB1p0_4, 16, 70.00)
draw (VA1p0_VB1p0_5, 16, 70.00)

;3
draw (VA0p9_VB0p9_1, 16, 60.00)
draw (VA0p9_VB0p9_2, 16, 60.00)
draw (VA0p9_VB0p9_3, 16, 70.00)
draw (VA0p9_VB0p9_4, 16, 70.00)
draw (VA0p9_VB0p9_5, 16, 70.00)

;4
draw (VA0p8_VB0p8_1, 16, 60.00)
draw (VA0p8_VB0p8_2, 16, 60.00)
draw (VA0p8_VB0p8_3, 16, 70.00)
draw (VA0p8_VB0p8_4, 16, 70.00)
draw (VA0p8_VB0p8_5, 16, 70.00)

;5
draw (VA1p2_VB1p0_1, 16, 60.00)
draw (VA1p2_VB1p0_2, 16, 60.00)
draw (VA1p2_VB1p0_3, 16, 70.00)
draw (VA1p2_VB1p0_4, 16, 70.00)
draw (VA1p2_VB1p0_5, 16, 70.00)

;6
draw (VA1p1_VB0p95_1, 16, 60.00)
draw (VA1p1_VB0p95_2, 16, 60.00)
draw (VA1p1_VB0p95_3, 16, 70.00)
draw (VA1p1_VB0p95_4, 16, 70.00)
draw (VA1p1_VB0p95_5, 16, 70.00)

;7
draw (VA1p0_VB0p9_1, 16, 60.00)
draw (VA1p0_VB0p9_2, 16, 60.00)
draw (VA1p0_VB0p9_3, 16, 70.00)
draw (VA1p0_VB0p9_4, 16, 70.00)
draw (VA1p0_VB0p9_5, 16, 70.00)

;8
draw (VA0p9_VB0p85_1, 16, 60.00)
draw (VA0p9_VB0p85_2, 16, 60.00)
draw (VA0p9_VB0p85_3, 16, 70.00)
draw (VA0p9_VB0p85_4, 16, 70.00)
draw (VA0p9_VB0p85_5, 16, 70.00)

;9
draw (VA1p2_VB0p95_1, 16, 60.00)
draw (VA1p2_VB0p95_2, 16, 60.00)
draw (VA1p2_VB0p95_3, 16, 70.00)
draw (VA1p2_VB0p95_4, 16, 70.00)
draw (VA1p2_VB0p95_5, 16, 70.00)

;10
draw (VA1p1_VB0p9_1, 16, 60.00)
draw (VA1p1_VB0p9_2, 16, 60.00)
draw (VA1p1_VB0p9_3, 16, 70.00)
draw (VA1p1_VB0p9_4, 16, 70.00)
draw (VA1p1_VB0p9_5, 16, 70.00)

;11
draw (VA1p0_VB0p85_1, 16, 60.00)
draw (VA1p0_VB0p85_2, 16, 60.00)
draw (VA1p0_VB0p85_3, 16, 70.00)
draw (VA1p0_VB0p85_4, 16, 70.00)
draw (VA1p0_VB0p85_5, 16, 70.00)

;12
draw (VA0p9_VB0p8_1, 16, 60.00)
draw (VA0p9_VB0p8_2, 16, 60.00)
draw (VA0p9_VB0p8_3, 16, 70.00)
draw (VA0p9_VB0p8_4, 16, 70.00)
draw (VA0p9_VB0p8_5, 16, 70.00)

;13
draw (VA1p2_VB0p9_1, 16, 60.00)
draw (VA1p2_VB0p9_2, 16, 60.00)
draw (VA1p2_VB0p9_3, 16, 70.00)
draw (VA1p2_VB0p9_4, 16, 70.00)
draw (VA1p2_VB0p9_5, 16, 70.00)

;14
draw (VA1p1_VB0p85_1, 16, 60.00)
draw (VA1p1_VB0p85_2, 16, 60.00)
draw (VA1p1_VB0p85_3, 16, 70.00)
draw (VA1p1_VB0p85_4, 16, 70.00)
draw (VA1p1_VB0p85_5, 16, 70.00)

;15
draw (VA1p0_VB0p8_1, 16, 60.00)
draw (VA1p0_VB0p8_2, 16, 60.00)
draw (VA1p0_VB0p8_3, 16, 70.00)
draw (VA1p0_VB0p8_4, 16, 70.00)
draw (VA1p0_VB0p8_5, 16, 70.00)

;16
draw (VA0p9_VB0p75_1, 16, 60.00)
draw (VA0p9_VB0p75_2, 16, 60.00)
draw (VA0p9_VB0p75_3, 16, 70.00)
draw (VA0p9_VB0p75_4, 16, 70.00)
draw (VA0p9_VB0p75_5, 16, 70.00)

; =====================
;Label
; =====================

sfile = numbers_honey_1

; =====================

for (a,16,1)
idraw(nbr_, a)
next a

+x = 500
stage

; =====================
;draw characters and arrows
; =====================

sfile = other_patterns_SB

; =====================

draw(arrow_left)
draw(arrow_down)


; =====================
; Overlap series (Moleküle Array)
; =====================

draw(overlap_series)

; =====================
;Einzelne Hexagons 1.7um - 2um
; =====================

sfile = hexagons_res25_flat

; =====================

draw (hexagon_flat_1p7, 16, 80.00)
draw (hexagon_flat_2p0, 16, 80.00)
draw (hexagon_flat_2p5, 16, 80.00)


; =====================
;Honeycomb TOPO d2.0
; =====================

sfile = HC_TOPO_EnO_d2.0_res_25_4x4_SB

; =====================

;17
draw (VA1p2_VB1p2_1, 16, 60.00)
draw (VA1p2_VB1p2_2, 16, 60.00)
draw (VA1p2_VB1p2_3, 16, 70.00)
draw (VA1p2_VB1p2_4, 16, 70.00)
draw (VA1p2_VB1p2_5, 16, 70.00)

;18
draw (VA1p0_VB1p0_1, 16, 60.00)
draw (VA1p0_VB1p0_2, 16, 60.00)
draw (VA1p0_VB1p0_3, 16, 70.00)
draw (VA1p0_VB1p0_4, 16, 70.00)
draw (VA1p0_VB1p0_5, 16, 70.00)

;19
draw (VA0p9_VB0p9_1, 16, 60.00)
draw (VA0p9_VB0p9_2, 16, 60.00)
draw (VA0p9_VB0p9_3, 16, 70.00)
draw (VA0p9_VB0p9_4, 16, 70.00)
draw (VA0p9_VB0p9_5, 16, 70.00)

;20
draw (VA0p8_VB0p8_1, 16, 60.00)
draw (VA0p8_VB0p8_2, 16, 60.00)
draw (VA0p8_VB0p8_3, 16, 70.00)
draw (VA0p8_VB0p8_4, 16, 70.00)
draw (VA0p8_VB0p8_5, 16, 70.00)

;21
draw (VA1p2_VB1p0_1, 16, 60.00)
draw (VA1p2_VB1p0_2, 16, 60.00)
draw (VA1p2_VB1p0_3, 16, 70.00)
draw (VA1p2_VB1p0_4, 16, 70.00)
draw (VA1p2_VB1p0_5, 16, 70.00)

;22
draw (VA1p1_VB0p95_1, 16, 60.00)
draw (VA1p1_VB0p95_2, 16, 60.00)
draw (VA1p1_VB0p95_3, 16, 70.00)
draw (VA1p1_VB0p95_4, 16, 70.00)
draw (VA1p1_VB0p95_5, 16, 70.00)

;23
draw (VA1p0_VB0p9_1, 16, 60.00)
draw (VA1p0_VB0p9_2, 16, 60.00)
draw (VA1p0_VB0p9_3, 16, 70.00)
draw (VA1p0_VB0p9_4, 16, 70.00)
draw (VA1p0_VB0p9_5, 16, 70.00)

;24
draw (VA0p9_VB0p85_1, 16, 60.00)
draw (VA0p9_VB0p85_2, 16, 60.00)
draw (VA0p9_VB0p85_3, 16, 70.00)
draw (VA0p9_VB0p85_4, 16, 70.00)
draw (VA0p9_VB0p85_5, 16, 70.00)

;25
draw (VA1p2_VB0p95_1, 16, 60.00)
draw (VA1p2_VB0p95_2, 16, 60.00)
draw (VA1p2_VB0p95_3, 16, 70.00)
draw (VA1p2_VB0p95_4, 16, 70.00)
draw (VA1p2_VB0p95_5, 16, 70.00)

;26
draw (VA1p1_VB0p9_1, 16, 60.00)
draw (VA1p1_VB0p9_2, 16, 60.00)
draw (VA1p1_VB0p9_3, 16, 70.00)
draw (VA1p1_VB0p9_4, 16, 70.00)
draw (VA1p1_VB0p9_5, 16, 70.00)

;27
draw (VA1p0_VB0p85_1, 16, 60.00)
draw (VA1p0_VB0p85_2, 16, 60.00)
draw (VA1p0_VB0p85_3, 16, 70.00)
draw (VA1p0_VB0p85_4, 16, 70.00)
draw (VA1p0_VB0p85_5, 16, 70.00)

;28
draw (VA0p9_VB0p8_1, 16, 60.00)
draw (VA0p9_VB0p8_2, 16, 60.00)
draw (VA0p9_VB0p8_3, 16, 70.00)
draw (VA0p9_VB0p8_4, 16, 70.00)
draw (VA0p9_VB0p8_5, 16, 70.00)

;29
draw (VA1p2_VB0p9_1, 16, 60.00)
draw (VA1p2_VB0p9_2, 16, 60.00)
draw (VA1p2_VB0p9_3, 16, 70.00)
draw (VA1p2_VB0p9_4, 16, 70.00)
draw (VA1p2_VB0p9_5, 16, 70.00)

;30
draw (VA1p1_VB0p85_1, 16, 60.00)
draw (VA1p1_VB0p85_2, 16, 60.00)
draw (VA1p1_VB0p85_3, 16, 70.00)
draw (VA1p1_VB0p85_4, 16, 70.00)
draw (VA1p1_VB0p85_5, 16, 70.00)

;31
draw (VA1p0_VB0p8_1, 16, 60.00)
draw (VA1p0_VB0p8_2, 16, 60.00)
draw (VA1p0_VB0p8_3, 16, 70.00)
draw (VA1p0_VB0p8_4, 16, 70.00)
draw (VA1p0_VB0p8_5, 16, 70.00)

;32
draw (VA0p9_VB0p75_1, 16, 60.00)
draw (VA0p9_VB0p75_2, 16, 60.00)
draw (VA0p9_VB0p75_3, 16, 70.00)
draw (VA0p9_VB0p75_4, 16, 70.00)
draw (VA0p9_VB0p75_5, 16, 70.00)


; =====================
;Label
; =====================

sfile = numbers_honey_17

; =====================

for (a,16,1)
idraw(nbr_, a)
next a


; =====================

;+x = 600
;next n

;+y = 600
;next m

; =====================

END