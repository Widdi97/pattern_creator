; Etch and overgrow
; Semenoff ss interface
; 09.2024 TEP
; Christian G. Mayer
; christian.mayer@uni-wuerzburg.de
;========= EnO top right semenoff, maple leaf, TCI and adiabatic Honey =======
current = 25000
origin = 0, 0

x = 0
y = 0
stage
; ========================================================
; ======================== left side =========================
; ========================================================

sfile = semenoff_V3
; variable large pillar diameters: 2.0, 2.4 um
; variable pillar overlaps: 0.9, 1.0, 1.1
; variable onsite difference 0.70, 0.80
; full size semenoff 2.0�m with v 0.9, 1.0 and onsite 0.70 and 0.80
; ========= draw semenoff ==========

 ; #1
draw(semenoff_v0.9_d2000_diff0.7_l)
draw(semenoff_v0.9_d2000_diff0.7_edge_l)
draw(semenoff_v0.9_d2000_diff0.7_r)
draw(semenoff_v0.9_d2000_diff0.7_edge_r)
draw(semenoff_v0.9_d2000_diff0.7_marker)

; #2
draw(semenoff_v0.9_d2400_diff0.7_l)
draw(semenoff_v0.9_d2400_diff0.7_edge_l)
draw(semenoff_v0.9_d2400_diff0.7_r)
draw(semenoff_v0.9_d2400_diff0.7_edge_r)
draw(semenoff_v0.9_d2400_diff0.7_marker)

; #3
draw(semenoff_v0.9_d2000_diff0.8_l)
draw(semenoff_v0.9_d2000_diff0.8_edge_l)
draw(semenoff_v0.9_d2000_diff0.8_r)
draw(semenoff_v0.9_d2000_diff0.8_edge_r)
draw(semenoff_v0.9_d2000_diff0.8_marker)


; #5
draw(semenoff_v1.0_d2000_diff0.7_l)
draw(semenoff_v1.0_d2000_diff0.7_edge_l)
draw(semenoff_v1.0_d2000_diff0.7_r)
draw(semenoff_v1.0_d2000_diff0.7_edge_r)
draw(semenoff_v1.0_d2000_diff0.7_marker)

; #6
draw(semenoff_v1.0_d2400_diff0.7_l)
draw(semenoff_v1.0_d2400_diff0.7_edge_l)
draw(semenoff_v1.0_d2400_diff0.7_r)
draw(semenoff_v1.0_d2400_diff0.7_edge_r)
draw(semenoff_v1.0_d2400_diff0.7_marker)

; #7
draw(semenoff_v1.0_d2000_diff0.8_l)
draw(semenoff_v1.0_d2000_diff0.8_edge_l)
draw(semenoff_v1.0_d2000_diff0.8_r)
draw(semenoff_v1.0_d2000_diff0.8_edge_r)
draw(semenoff_v1.0_d2000_diff0.8_marker)

; #9
draw(semenoff_v1.1_d2000_diff0.7_l)
draw(semenoff_v1.1_d2000_diff0.7_edge_l)
draw(semenoff_v1.1_d2000_diff0.7_r)
draw(semenoff_v1.1_d2000_diff0.7_edge_r)
draw(semenoff_v1.1_d2000_diff0.7_marker)

; #10
draw(semenoff_v1.1_d2400_diff0.7_l)
draw(semenoff_v1.1_d2400_diff0.7_edge_l)
draw(semenoff_v1.1_d2400_diff0.7_r)
draw(semenoff_v1.1_d2400_diff0.7_edge_r)
draw(semenoff_v1.1_d2400_diff0.7_marker)

; #11
draw(semenoff_v1.1_d2000_diff0.8_l)
draw(semenoff_v1.1_d2000_diff0.8_edge_l)
draw(semenoff_v1.1_d2000_diff0.8_r)
draw(semenoff_v1.1_d2000_diff0.8_edge_r)
draw(semenoff_v1.1_d2000_diff0.8_marker)


; #13
draw(semenoff_v0.9_d2000_diff0.7_full)

; #14
draw(semenoff_v1.0_d2000_diff0.7_full)

; #15
draw(semenoff_v0.9_d2000_diff0.8_full)



#NEW FOR V3 Maple Leaf no 2.4�m 0.8 pillar difference
sfile = maple_leaf_V3

;#4
draw(Maple_leaf_v_0.8_x_1_y_1)
draw(Maple_leaf_v_0.8_x_1_y_0)
draw(Maple_leaf_v_0.8_x_1_y_-1)
draw(Maple_leaf_v_0.8_x_0_y_1)
draw(Maple_leaf_v_0.8_x_0_y_0)
draw(Maple_leaf_v_0.8_x_0_y_-1)
draw(Maple_leaf_v_0.8_x_-1_y_1)
draw(Maple_leaf_v_0.8_x_-1_y_0)
draw(Maple_leaf_v_0.8_x_-1_y_-1)

;#8x	
draw(Maple_leaf_v_0.9_x_1_y_1)
draw(Maple_leaf_v_0.9_x_1_y_0)
draw(Maple_leaf_v_0.9_x_1_y_-1)
draw(Maple_leaf_v_0.9_x_0_y_1)
draw(Maple_leaf_v_0.9_x_0_y_0)
draw(Maple_leaf_v_0.9_x_0_y_-1)
draw(Maple_leaf_v_0.9_x_-1_y_1)
draw(Maple_leaf_v_0.9_x_-1_y_0)
draw(Maple_leaf_v_0.9_x_-1_y_-1)

;#12
draw(Maple_leaf_v_1.0_x_1_y_1)
draw(Maple_leaf_v_1.0_x_1_y_0)
draw(Maple_leaf_v_1.0_x_1_y_-1)
draw(Maple_leaf_v_1.0_x_0_y_1)
draw(Maple_leaf_v_1.0_x_0_y_0)
draw(Maple_leaf_v_1.0_x_0_y_-1)
draw(Maple_leaf_v_1.0_x_-1_y_1)
draw(Maple_leaf_v_1.0_x_-1_y_0)
draw(Maple_leaf_v_1.0_x_-1_y_-1)

;#16
draw(Maple_leaf_v_1.1_x_1_y_1)
draw(Maple_leaf_v_1.1_x_1_y_0)
draw(Maple_leaf_v_1.1_x_1_y_-1)
draw(Maple_leaf_v_1.1_x_0_y_1)
draw(Maple_leaf_v_1.1_x_0_y_0)
draw(Maple_leaf_v_1.1_x_0_y_-1)
draw(Maple_leaf_v_1.1_x_-1_y_1)
draw(Maple_leaf_v_1.1_x_-1_y_0)
draw(Maple_leaf_v_1.1_x_-1_y_-1)



; ========= Calibartion ==========
sfile = other_patterns

draw (arrow_left)
draw (arrow_up)
draw (overlap_series)

; ========= Numbers1 ==========
sfile = numbers_honey_V3
for i = 1 to 16
idraw(nbr_,i)
next i
; ========================================================
; ======================== right side =========================
; ========================================================
x = 455
y = 0
stage


; ========= Numbers2 ==========
sfile = numbers_addiabatic
draw(nbr_17)
draw(nbr_18)
draw(nbr_19)
draw(nbr_20)
draw(nbr_21)
draw(nbr_22)
draw(nbr_23)
draw(nbr_24)
draw(nbr_25)
draw(nbr_26)
draw(nbr_27)
draw(nbr_28)
draw(nbr_29)
draw(nbr_3)
draw(nbr_0)




sfile = honey_adiabaticV2
; ========= Addiabatic change Honeycomb v constant ==========

; start pillar diameter: 1.8 �m
; end pillar diameter: 2.6, 3.0 �m
; variable overlap v: 0.9, 1.0, 1.1, 1,2

;#17
draw(adiabaticHoney_v_1.2_ds1800_dl2600)
draw(adiabaticHoney_v_1.2_ds1800_dl2600_marker)

;#18
draw(adiabaticHoney_v_1.1_ds1800_dl2600)
draw(adiabaticHoney_v_1.1_ds1800_dl2600_marker)

;#19
draw(adiabaticHoney_v_1.0_ds1800_dl2600)
draw(adiabaticHoney_v_1.0_ds1800_dl2600_marker)

;#20
draw(adiabaticHoney_v_0.9_ds1800_dl2600)
draw(adiabaticHoney_v_0.9_ds1800_dl2600_marker)

;#21
draw(adiabaticHoney_v_1.2_ds1800_dl3000)
draw(adiabaticHoney_v_1.2_ds1800_dl3000_marker)

;#22
draw(adiabaticHoney_v_1.1_ds1800_dl3000)
draw(adiabaticHoney_v_1.1_ds1800_dl3000_marker)

;#23
draw(adiabaticHoney_v_1.0_ds1800_dl3000)
draw(adiabaticHoney_v_1.0_ds1800_dl3000_marker)

;#24
draw(adiabaticHoney_v_0.9_ds1800_dl3000)
draw(adiabaticHoney_v_0.9_ds1800_dl3000_marker)

; ========= Addiabatic change Honeycomb a constant ==========

; start pillar diameter: 1.8 �m
; end pillar diameter: 2.6, 3.0 �m
; variable overlap at the small pillar v: 1.1, 1.3, 1.5

;#25
for i = 1 to 4
idraw(ad_lat_1.1_ds1800_dl2600_,i)
next i


;#26
for i = 1 to 4
idraw(ad_lat_1.1_ds1800_dl3000_,i)
next i
;draw(adiabaticHoney_lattice1.1_ds1800_dl3000)


;#27
for i = 1 to 4
idraw(ad_lat_1.3_ds1800_dl2600_,i)
next i


;#28
for i = 1 to 4
idraw(ad_lat_1.3_ds1800_dl3000_,i)
next i

;#29
for i = 1 to 4
idraw(ad_lat_1.5_ds1800_dl2600_,i)
next i

;#30
for i = 1 to 4
idraw(ad_lat_1.5_ds1800_dl3000_,i)
next i

; ========= Addiabatic change Chain v  constant ==========

; start pillar diameter: 1.8, 2.0 �m
; end pillar diameter: 2.6, 3.0 �m
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