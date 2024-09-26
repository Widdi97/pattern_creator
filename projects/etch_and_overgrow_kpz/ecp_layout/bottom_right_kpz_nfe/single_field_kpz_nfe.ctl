; Etch and overgrow
; KPZ square and triangular lattices in the nearly free electron limit
; 09.2024 TEP
; Simon Widmann
; simon.widmann@uni-wuerzburg.de

; square and triangular lattice parameters:
; variable perturbations

current = 25000

origin = 0, 0
x = 0
y = 0
stage


; draw characters and arrows
sfile = other_patterns

draw(arrow_right)
draw(arrow_down)
draw(overlap_series)

; ==========draw all lattices
sfile = lattices_nfe

draw(square_perturb_0.6)
draw(square_perturb_0.658)
draw(square_perturb_0.716)
draw(square_perturb_0.774)
draw(square_perturb_0.832)
draw(square_perturb_0.89)
draw(triang_perturb_0.89)
draw(triang_perturb_0.906)
draw(triang_perturb_0.922)
draw(triang_perturb_0.938)
draw(triang_perturb_0.954)
draw(triang_perturb_0.97)

END