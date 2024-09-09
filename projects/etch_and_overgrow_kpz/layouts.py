from generate_pattern import Pattern, circle, ellipse
from shape_intersections import find_intersections
from math import pi
import numpy as np
import matplotlib.pyplot as plt

pat_str = ""
pixel_res = 150

#%% square lattice

def generate_square_bulk_unit_cell(d_pillar, v, max_px_size=30):
    
    a_latt = v * d_pillar
    
    steps = int(a_latt // max_px_size) + 1
    px_size = a_latt / steps
    
    pat_name = f"square_bulk_uc_d{d_pillar}_v{v}_ax{a_latt}_ay{a_latt}"
    pattern = Pattern(a_latt, a_latt, px_size, pattern_name=pat_name, increment=2, dwell_time=200)
    
    # define lattice vectors
    a1 = np.array([1, 0]) * a_latt
    a2 = np.array([0, 1]) * a_latt
    
    offset = a1 / 2 + a2 / 2 - px_size / 2
    
    #plot unit cell
    for ii in range(-1, 2):
        for jj in range(-1, 2):
            vec = offset + ii * a1 + jj * a2
            pattern.add_parametrized_shape(circle, *vec, d_pillar / 2)
    pattern.visualize()
    return pattern

overlaps_sq = [0.95, 1.0, 1.07]
d_pillars_sq = [1800, 2100, 2500]


for v in overlaps_sq:
    for d_pillar in d_pillars_sq:
        pat = generate_square_bulk_unit_cell(d_pillar, v, pixel_res)
        pat_str += pat.export_pattern(complete=True) + "\n"*3

#%% triangular lattice

def rotmat(phi):
    c = np.cos(phi)
    s = np.sin(phi)
    return np.array([[c,-s],[s, c]])


def generate_triangular_bulk_unit_cell(d_pillar, v, max_px_size=30):
    
    a_latt = v * d_pillar
    
    steps = int(a_latt // max_px_size) + 1
    px_size = a_latt / steps
    
    # define lattice vectors
    a1 = np.array([1, 0]) * a_latt
    a2 = np.dot(rotmat(60/180*np.pi), a1)
    y_vec = 2 * a2 - a1
    y_size = np.dot(y_vec, y_vec)**0.5
    
    pat_name = f"triangular_bulk_d{d_pillar}_v{v}"
    pattern = Pattern(a_latt, y_size, px_size, pattern_name=pat_name, increment=2, dwell_time=200)
    pat_name += f"_ax{round(pat.x_ax[-1] + pat.step_size)}_ay{{round(pat.y_ax[-1] + pat.step_size)}}"
    pattern.pattern_name = pat_name
    
    offset = a1 / 2 + a2 / 2 - px_size / 2
    
    #plot unit cell
    for ii in range(-1, 2):
        for jj in range(-1, 3):
            vec = offset + ii * a1 + jj * a2
            pattern.add_parametrized_shape(circle, *vec, d_pillar / 2)
    pattern.visualize()
    return pattern
# generate_triangular_bulk_unit_cell(2000, 1, 100)
overlaps_tri = [0.95, 1.0, 1.07]
d_pillars_tri = [1800, 2100, 2500]

for v in overlaps_tri:
    for d_pillar in d_pillars_tri:
        pat = generate_triangular_bulk_unit_cell(d_pillar, v, pixel_res)
        pat_str += pat.export_pattern(complete=True) + "\n"*3

print(pat_str)
file = open("pat_string.txt", "w")
file.write(pat_str)