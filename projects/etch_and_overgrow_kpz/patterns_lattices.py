from generate_pattern import Lattice, circle, ellipse
from shape_intersections import find_intersections
from math import pi
import numpy as np
import matplotlib.pyplot as plt

pat_str = ""
draw_strs = ""
pixel_res = 25
a_ecp = 130000

#%% square lattice


overlaps_sq = [0.97, 1.05, 1.1]
d_pillars_sq = [1800, 2100]


for vidx, v in enumerate(overlaps_sq):
    for didx, d_pillar in enumerate(d_pillars_sq):
        name = f"square_v{v}_d{d_pillar}"
        draw_lattice_str = ""
        
        a = v * d_pillar
        a1_ = a * np.array([1, 0])
        a2_ = a * np.array([0, 1])
        x_size_ = 100000
        y_size_ = 100000
        lattice = Lattice(a1_, a2_, x_size_, y_size_, pixel_res, [[circle, 0, 0, d_pillar / 2]],
                          pattern_name=name, global_offsetx=a_ecp * didx, global_offsety= (2 - vidx) * a_ecp)
        
        pat_str += lattice.pat_str + "\n"*3
        draw_strs += lattice.draw_latt_str + "\n"*5

#%% triangular lattice

overlaps_tri = [0.97, 1.05, 1.1]
d_pillars_tri = [1800, 2100]


for vidx, v in enumerate(overlaps_tri):
    for didx, d_pillar in enumerate(d_pillars_tri):
        
        name = f"triangular_v{v}_d{d_pillar}"
        draw_lattice_str = ""
        a_latt = v * d_pillar
        
        # define lattice vectors
        a1_ = a_latt * np.array([1, 0])
        a2_ = a_latt * np.array([np.cos(60/180 * np.pi), np.sin(60/180 * np.pi)])
        
        x_size_ = 100000
        y_size_ = 100000
        
        
        
        lattice = Lattice(a1_, a2_, x_size_, y_size_, pixel_res, [[circle, 0, 0, d_pillar / 2]],
                          pattern_name=name, global_offsetx=a_ecp * didx, global_offsety= (2 - vidx) * a_ecp)
        
        pat_str += lattice.pat_str + "\n"*3
        draw_strs += lattice.draw_latt_str + "\n"*5
        


#%% export pattern file

file = open("pat_string.txt", "w")
file.write(pat_str)
file.close()

file = open("draw_strs.txt", "w")
file.write(draw_strs)
file.close()

#%% 