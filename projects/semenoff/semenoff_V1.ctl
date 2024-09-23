; Etch and overgrow
; Semenoff ss interface
; 09.2024 TEP
; Christian G. Mayer
; christian.mayer@uni-wuerzburg.de
; variable pillar diameters: 2.0, 2.4 um
; variable pillar overlaps: 0.9, 1.0, 1.1
; variable onsite difference 0.70, 0.80

; ========= draw semenoff ==========
current = 25000


origin = 0, 0
x = 0
y = 0
stage

sfile = semenoff_V1


draw(semenoff_v0.9_d2000_diff0.7_l)
draw(semenoff_v0.9_d2000_diff0.7_edge_l)
draw(semenoff_v0.9_d2000_diff0.7_r)
draw(semenoff_v0.9_d2000_diff0.7_edge_r)
draw(semenoff_v0.9_d2000_diff0.7_marker)


draw(semenoff_v0.9_d2400_diff0.7_l)
draw(semenoff_v0.9_d2400_diff0.7_edge_l)
draw(semenoff_v0.9_d2400_diff0.7_r)
draw(semenoff_v0.9_d2400_diff0.7_edge_r)
draw(semenoff_v0.9_d2400_diff0.7_marker)


draw(semenoff_v0.9_d2000_diff0.8_l)
draw(semenoff_v0.9_d2000_diff0.8_edge_l)
draw(semenoff_v0.9_d2000_diff0.8_r)
draw(semenoff_v0.9_d2000_diff0.8_edge_r)
draw(semenoff_v0.9_d2000_diff0.8_marker)


draw(semenoff_v0.9_d2400_diff0.8_l)
draw(semenoff_v0.9_d2400_diff0.8_edge_l)
draw(semenoff_v0.9_d2400_diff0.8_r)
draw(semenoff_v0.9_d2400_diff0.8_edge_r)
draw(semenoff_v0.9_d2400_diff0.8_marker)


draw(semenoff_v1.0_d2000_diff0.7_l)
draw(semenoff_v1.0_d2000_diff0.7_edge_l)
draw(semenoff_v1.0_d2000_diff0.7_r)
draw(semenoff_v1.0_d2000_diff0.7_edge_r)
draw(semenoff_v1.0_d2000_diff0.7_marker)


draw(semenoff_v1.0_d2400_diff0.7_l)
draw(semenoff_v1.0_d2400_diff0.7_edge_l)
draw(semenoff_v1.0_d2400_diff0.7_r)
draw(semenoff_v1.0_d2400_diff0.7_edge_r)
draw(semenoff_v1.0_d2400_diff0.7_marker)


draw(semenoff_v1.0_d2000_diff0.8_l)
draw(semenoff_v1.0_d2000_diff0.8_edge_l)
draw(semenoff_v1.0_d2000_diff0.8_r)
draw(semenoff_v1.0_d2000_diff0.8_edge_r)
draw(semenoff_v1.0_d2000_diff0.8_marker)


draw(semenoff_v1.0_d2400_diff0.8_l)
draw(semenoff_v1.0_d2400_diff0.8_edge_l)
draw(semenoff_v1.0_d2400_diff0.8_r)
draw(semenoff_v1.0_d2400_diff0.8_edge_r)
draw(semenoff_v1.0_d2400_diff0.8_marker)


draw(semenoff_v1.1_d2000_diff0.7_l)
draw(semenoff_v1.1_d2000_diff0.7_edge_l)
draw(semenoff_v1.1_d2000_diff0.7_r)
draw(semenoff_v1.1_d2000_diff0.7_edge_r)
draw(semenoff_v1.1_d2000_diff0.7_marker)


draw(semenoff_v1.1_d2400_diff0.7_l)
draw(semenoff_v1.1_d2400_diff0.7_edge_l)
draw(semenoff_v1.1_d2400_diff0.7_r)
draw(semenoff_v1.1_d2400_diff0.7_edge_r)
draw(semenoff_v1.1_d2400_diff0.7_marker)


draw(semenoff_v1.1_d2000_diff0.8_l)
draw(semenoff_v1.1_d2000_diff0.8_edge_l)
draw(semenoff_v1.1_d2000_diff0.8_r)
draw(semenoff_v1.1_d2000_diff0.8_edge_r)
draw(semenoff_v1.1_d2000_diff0.8_marker)


draw(semenoff_v1.1_d2400_diff0.8_l)
draw(semenoff_v1.1_d2400_diff0.8_edge_l)
draw(semenoff_v1.1_d2400_diff0.8_r)
draw(semenoff_v1.1_d2400_diff0.8_edge_r)
draw(semenoff_v1.1_d2400_diff0.8_marker)


draw(semenoff_v0.9_d2000_diff0.7_full)
draw(semenoff_v1.0_d2000_diff0.7_full)
draw(semenoff_v0.9_d2000_diff0.8_full)
draw(semenoff_v1.0_d2000_diff0.8_full)


x = 220
y = 0
stage

sfile = other_patterns

draw(arrow_right)
draw(arrow_up)
draw(overlap_series)