from generate_pattern import Pattern, Lattice, circle, ellipse
from shape_intersections import find_intersections
from math import pi
import numpy as np
import matplotlib.pyplot as plt

pat_str = ""
draw_strs = ""
pixel_res = 25
a_ecp = 130000
latt_size = 100000

perturb_size_sq = np.linspace(0.6, 0.89, 6)
a = 2500

ov = np.array([4500, 50000+75000])

def xy_shift(latt_idx):
    return a_ecp * np.array([latt_idx%2, 2 - latt_idx//2])

#%% square lattice

all_str = ""

def square_lattice_func(x, y, a, p):
    x = x + pixel_res / 2
    y = y + pixel_res / 2
    return ((np.cos(2 * np.pi * x / a) + np.cos(2 * np.pi * y / a)) / 4 + 0.5 - p) <= 0

for idx, p in enumerate(perturb_size_sq):
    pattern = Pattern(a, a, pixel_res)
    X, Y = pattern.XY_meshgrid
    test = square_lattice_func(X, Y, a, p)
    
    pattern.pattern = pattern.pattern | test
    plt.pcolormesh(pattern.x_ax, pattern.y_ax, pattern.pattern)
    plt.axis("equal")
    plt.title(p)
    plt.show()
    
    pattern.rectangulize()
    pattern.pat_file_string_updated = False
    pattern.visualize()
    pattern.verify_rectangulization()
    
    # plt.matshow(test)
    # plt.show()
    pat_str = f"D square_perturb_{round(p,4)}, {int(a)}, {int(a)}, {int(latt_size / a)}, {int(latt_size / a)}\n"
    pat_str += "I 16\nC 100\n"
    
    offset = ov + xy_shift(idx)
    pat_str += pattern.export_pattern(offsetx=offset[0], offsety=offset[1]) + "END" + "\n"*3
    all_str += pat_str

#%% triangular lattice

perturb_size_tri = np.linspace(0.89, 0.97, 6)

def triang_lattice_func(x, y, a, p):
    ar = a * 2 * np.cos(np.pi / 6) / (4 * np.pi)
    phi = 30 / 180 * np.pi
    r1 = x * np.cos(phi) + y * np.sin(phi)
    r2 = x * np.cos(np.pi / 3 + phi) + y * np.sin(np.pi / 3 + phi)
    r3 = x * np.cos(2 * np.pi / 3 + phi) + y * np.sin(2 * np.pi / 3 + phi)
    
    return (((np.cos(r1 / ar) + np.cos(r2 / ar) + np.cos(r3 / ar)) + 1.5) / 4.5 - (1 - p)) >= 0

for idx, p in enumerate(perturb_size_tri):
    ay = a * np.sin(np.pi/3) * 2
    pattern = Pattern(a, ay, pixel_res)
    X, Y = pattern.XY_meshgrid
    test = triang_lattice_func(X, Y, a, p)
    
    pattern.pattern = pattern.pattern | test
    plt.pcolormesh(pattern.x_ax, pattern.y_ax, pattern.pattern)
    plt.axis("equal")
    plt.title(p)
    plt.show()
    
    pattern.rectangulize()
    pattern.pat_file_string_updated = False
    pattern.visualize()
    pattern.verify_rectangulization()
    
    plt.matshow(test)
    plt.show()
    pat_str = f"D triang_perturb_{round(p,4)}, {int(a)}, {int(pattern.y_ax[-1]+pixel_res)}, {int(latt_size / a)}, {int(latt_size / ay)}\n"
    pat_str += "I 16\nC 100\n"
    
    offset = ov + xy_shift(idx)
    pat_str += pattern.export_pattern(offsetx=offset[0], offsety=offset[1]) + "END" + "\n"*3
    all_str += pat_str



#%% export pattern file

file = open("lattices_nfe.pat", "w")
file.write(all_str)
file.close()

#%% 