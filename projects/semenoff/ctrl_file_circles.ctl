; Etch and overgrow
; Semenoff ss interface
; 09.2024 TEP
; Christian G. Mayer
; christian.mayer@uni-wuerzburg.de
; variable pillar diameters: 2.0, 2.5 um
; variable pillar overlaps: 0.95, 1.05, 1.05
; variable onsite difference 0.8, 0.9

; ========= draw semenoff ==========
sfile = pattern_circles
current = 25000


origin = 0, 0
x = 0
y = 0
stage


draw(semenoff_v0.9_d2200_diff0.85_l)
draw(semenoff_v0.9_d2200_diff0.85_edge_l)
draw(semenoff_v0.9_d2200_diff0.85_r)
draw(semenoff_v0.9_d2200_diff0.85_edge_r)
draw(semenoff_v0.9_d2200_diff0.85_marker)
