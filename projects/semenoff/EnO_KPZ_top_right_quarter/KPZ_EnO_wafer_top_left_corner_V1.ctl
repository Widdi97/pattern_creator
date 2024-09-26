; Etch and overgrow
; Semenoff ss interface
; 09.2024 TEP
; Christian G. Mayer
; christian.mayer@uni-wuerzburg.de
;========= EnO top right semenoff, TCI and adiabatic Honey =======
current = 25000
origin = 0, 0

; variable large pillar diameters: 2.0, 2.4 um
; variable pillar overlaps: 0.9, 1.0, 1.1
; variable onsite difference 0.70, 0.80
; full size semenoff 2.0µm with v 0.9, 1.0 and onsite 0.70 and 0.80
; ========= draw semenoff ==========
x = 0
y = 0
stage 
sfile = semenoff_V2
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

; ========= Calibartion ==========
sfile = other_patterns

draw (arrow_left)
draw (arrow_up)
draw (overlap_series)


x = 455
y = 0
stage
sfile = honey_adiabatic


; ========= Addiabatic change Honeycomb v constant ==========

; start pillar diameter: 1.8 µm
; end pillar diameter: 2.6, 3.0 µm
; variable overlap v: 0.9, 1.0, 1.1, 1,2

draw(adiabaticHoney_v_1.2_ds1800_dl2600)
draw(adiabaticHoney_v_1.2_ds1800_dl2600_marker)

draw(adiabaticHoney_v_1.2_ds1800_dl3000)
draw(adiabaticHoney_v_1.2_ds1800_dl3000_marker)

draw(adiabaticHoney_v_1.1_ds1800_dl2600)
draw(adiabaticHoney_v_1.1_ds1800_dl2600_marker)

draw(adiabaticHoney_v_1.1_ds1800_dl3000)
draw(adiabaticHoney_v_1.1_ds1800_dl3000_marker)

draw(adiabaticHoney_v_1.0_ds1800_dl2600)
draw(adiabaticHoney_v_1.0_ds1800_dl2600_marker)

draw(adiabaticHoney_v_1.0_ds1800_dl3000)
draw(adiabaticHoney_v_1.0_ds1800_dl3000_marker)

draw(adiabaticHoney_v_0.9_ds1800_dl2600)
draw(adiabaticHoney_v_0.9_ds1800_dl2600_marker)

draw(adiabaticHoney_v_0.9_ds1800_dl3000)
draw(adiabaticHoney_v_0.9_ds1800_dl3000_marker)

; ========= Addiabatic change Honeycomb a constant ==========

; start pillar diameter: 1.8 µm
; end pillar diameter: 2.6, 3.0 µm
; variable overlap at the small pillar v: 1.1, 1.3, 1.5

draw(adiabaticHoney_lattice1.1_ds1800_dl2600)
draw(adiabaticHoney_lattice1.1_ds1800_dl3000)
draw(adiabaticHoney_lattice1.3_ds1800_dl2600)
draw(adiabaticHoney_lattice1.3_ds1800_dl3000)
draw(adiabaticHoney_lattice1.5_ds1800_dl2600)
draw(adiabaticHoney_lattice1.5_ds1800_dl3000)

; ========= Addiabatic change Chain v  constant ==========

; start pillar diameter: 1.8, 2.0 µm
; end pillar diameter: 2.6, 3.0 µm
; variable overlap v: 0.9, 1.0, 1.1, 1,2

draw(adiabaticChain1.2_ds1800_dl2600)
draw(adiabaticChain1.2_ds1800_dl3000)
draw(adiabaticChain1.1_ds1800_dl2600)
draw(adiabaticChain1.1_ds1800_dl3000)
draw(adiabaticChain1.0_ds1800_dl2600)
draw(adiabaticChain1.0_ds1800_dl3000)
draw(adiabaticChain0.9_ds1800_dl2600)
draw(adiabaticChain0.9_ds1800_dl3000)
draw(adiabaticChain1.2_ds2000_dl2600)
draw(adiabaticChain1.2_ds2000_dl3000)
draw(adiabaticChain1.1_ds2000_dl2600)
draw(adiabaticChain1.1_ds2000_dl3000)
draw(adiabaticChain1.0_ds2000_dl2600)
draw(adiabaticChain1.0_ds2000_dl3000)
draw(adiabaticChain0.9_ds2000_dl2600)
draw(adiabaticChain0.9_ds2000_dl3000)



sfile = old_pattern
; =====================
; TCI V4 A1 TCI Hexagons Triangles
; =====================

draw (TCI_honey_D4000_07_30, 16, 85.00)

; =====================
; TCI V3 G5 Science Paper layou
; =====================

draw (TCI_HEXA_D2500_098_08_092_074_086_30, 16, 60.00)

end