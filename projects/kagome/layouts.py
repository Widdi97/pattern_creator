from generate_pattern import Lattice, circle, ellipse
from shape_intersections import find_intersections
from math import pi
import numpy as np
import matplotlib.pyplot as plt

pat_str = ""
draw_strs = ""
pixel_res = 75

#%% square lattice


overlaps_sq = [1.02, 1.07]
d_pillars_sq = [1800, 2100]


for v in overlaps_sq:
    for d_pillar in d_pillars_sq:
        name = f"kagome_v{v}_d{d_pillar}"
        draw_lattice_str = ""
        
        
        
        a = 2 * v * d_pillar
        a1_ = a * np.array([1, 0])
        a2_ = a * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])
        
        b1_ = np.array([0, 0])
        b2_ = a1_ / 2
        b3_ = a2_ / 2
        bs = np.array([b1_, b2_, b3_])
        
        x_size_ = 100000
        y_size_ = 100000
        lattice = Lattice(a1_, a2_, x_size_, y_size_, pixel_res, [[circle, 0, 0, d_pillar / 2] for b in bs], bs, pattern_name=name)
        
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