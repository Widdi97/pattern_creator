; Etch and overgrow 2026, TEST grid 3 x 2 of shc_field with field numbers 
; pitch 550 x 540 um (same as the jdf ARRAY); keep nx, ny small (ECP gets slow)

current = 25000

origin = 0, 0
x = 0
y = 0
stage

for m = 1 to 2
x = 0
for n = 1 to 3
stage

sfile = shc_field
draw(shc_field_f0_kek_v1p100_s000_x_0_y_0)
draw(shc_field_f0_kek_v1p100_s000_x_0_y_1)
draw(shc_field_f0_kek_v1p100_s000_x_0_y_-1)
draw(shc_field_f0_kek_v1p133_s000_x_0_y_0)
draw(shc_field_f0_kek_v1p133_s000_x_0_y_1)
draw(shc_field_f0_kek_v1p133_s000_x_0_y_-1)
draw(shc_field_f0_kek_v1p167_s000_x_0_y_0)
draw(shc_field_f0_kek_v1p167_s000_x_0_y_1)
draw(shc_field_f0_kek_v1p167_s000_x_0_y_-1)
draw(shc_field_f0_kek_v1p200_s000_x_0_y_0)
draw(shc_field_f0_kek_v1p200_s000_x_0_y_1)
draw(shc_field_f0_kek_v1p200_s000_x_0_y_-1)
draw(shc_field_f0_kek_v1p100_s080_x_0_y_0)
draw(shc_field_f0_kek_v1p100_s080_x_0_y_1)
draw(shc_field_f0_kek_v1p100_s080_x_0_y_-1)
draw(shc_field_f0_kek_v1p133_s080_x_0_y_0)
draw(shc_field_f0_kek_v1p133_s080_x_0_y_1)
draw(shc_field_f0_kek_v1p133_s080_x_0_y_-1)
draw(shc_field_f0_kek_v1p167_s080_x_0_y_0)
draw(shc_field_f0_kek_v1p167_s080_x_0_y_1)
draw(shc_field_f0_kek_v1p167_s080_x_0_y_-1)
draw(shc_field_f0_kek_v1p200_s080_x_0_y_0)
draw(shc_field_f0_kek_v1p200_s080_x_0_y_1)
draw(shc_field_f0_kek_v1p200_s080_x_0_y_-1)
draw(shc_field_f0_kek_v1p100_s110_x_0_y_0)
draw(shc_field_f0_kek_v1p100_s110_x_1_y_0)
draw(shc_field_f0_kek_v1p100_s110_x_0_y_1)
draw(shc_field_f0_kek_v1p100_s110_x_0_y_-1)
draw(shc_field_f0_kek_v1p100_s110_x_-1_y_0)
draw(shc_field_f0_kek_v1p133_s110_x_0_y_0)
draw(shc_field_f0_kek_v1p133_s110_x_0_y_1)
draw(shc_field_f0_kek_v1p133_s110_x_0_y_-1)
draw(shc_field_f0_kek_v1p167_s110_x_0_y_0)
draw(shc_field_f0_kek_v1p167_s110_x_0_y_1)
draw(shc_field_f0_kek_v1p167_s110_x_0_y_-1)
draw(shc_field_f0_kek_v1p200_s110_x_0_y_0)
draw(shc_field_f0_kek_v1p200_s110_x_0_y_1)
draw(shc_field_f0_kek_v1p200_s110_x_0_y_-1)
draw(shc_field_f0_kek_v1p100_s140_x_0_y_0)
draw(shc_field_f0_kek_v1p100_s140_x_1_y_0)
draw(shc_field_f0_kek_v1p100_s140_x_0_y_1)
draw(shc_field_f0_kek_v1p100_s140_x_0_y_-1)
draw(shc_field_f0_kek_v1p100_s140_x_-1_y_0)
draw(shc_field_f0_kek_v1p133_s140_x_0_y_0)
draw(shc_field_f0_kek_v1p133_s140_x_1_y_0)
draw(shc_field_f0_kek_v1p133_s140_x_0_y_1)
draw(shc_field_f0_kek_v1p133_s140_x_0_y_-1)
draw(shc_field_f0_kek_v1p133_s140_x_-1_y_0)
draw(shc_field_f0_kek_v1p167_s140_x_0_y_0)
draw(shc_field_f0_kek_v1p167_s140_x_0_y_1)
draw(shc_field_f0_kek_v1p167_s140_x_0_y_-1)
draw(shc_field_f0_kek_v1p200_s140_x_0_y_0)
draw(shc_field_f0_kek_v1p200_s140_x_0_y_1)
draw(shc_field_f0_kek_v1p200_s140_x_0_y_-1)
draw(shc_field_f0_ref_overlap_series_2024)
draw(shc_field_f0_ref_arrows_right)
draw(shc_field_f0_ref_arrows_up)
draw(shc_field_f0_labels)

sfile = numbers_xy
idraw(nbr_x_, n)
idraw(nbr_y_, m)

+x = 550
next n
+y = 540
next m

END
