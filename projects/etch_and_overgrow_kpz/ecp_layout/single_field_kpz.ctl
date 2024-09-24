; Etch and overgrow
; KPZ square and triangular lattices
; 09.2024 TEP
; Simon Widmann
; simon.widmann@uni-wuerzburg.de

; square and triangular lattice parameters:
; variable pillar diameters: 1.8, 2.1um
; variable pillar overlaps: 0.97, 1.05, 1.1

current = 25000

origin = 0, 0
x = 0
y = 0
stage


; draw characters and arrows
sfile = other_patterns

draw(arrow_right)
draw(arrow_up)
draw(overlap_series)

; ==========draw 1D ssh chains
sfile = ssh_chains_grouped


draw(ssh_1d_short_bulk)
draw(ssh_1d_short_ends)
draw(ssh_1d_long_bulk)
draw(ssh_1d_long_ends)


; ==========draw zigzigzagzag chains
sfile = zigzigzagzag_shifted

draw(1.0_0.875)
draw(1.0_0.9)
draw(1.0_0.925)
draw(1.05_0.925)
draw(1.05_0.95)
draw(1.05_0.975)
draw(1.1_0.95)
draw(1.1_0.975)
draw(1.1_1.0)

; ==========draw all lattices
sfile = kpz_lattices


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

END