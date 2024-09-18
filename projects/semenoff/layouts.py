# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 14:48:18 2024

@author: chm66em
"""

from generate_pattern import Lattice, circle, ellipse
from shape_intersections import find_intersections
import numpy as np
import matplotlib.pyplot as plt

pat_str = ""
draw_strs = ""
pixel_res = 75

#%% rect semenoff not working


# overlaps_sq = [1]
# d_pillars_sq = [2400]
# onsite_diff = [0.8]

# # overlaps_sq = [0.95, 1.00, 1.05]
# # d_pillars_sq = [1800, 2000, 2400]
# # onsite_diff = [0.8, 0.9]

# for v in overlaps_sq:
#     for d_pillar in d_pillars_sq:
#         for d_onsite in onsite_diff: 
#             name = f"semenoff_v{v}_d{d_pillar}_diff{d_onsite}_mirror"
#             draw_lattice_str = ""
            
#             d1 = d_pillar  
#             d2 = d_pillar  * d_onsite
                        
#             a = d_pillar * v 
#             a_lattice1 = 3 * a 
#             a_lattice2 = (3*a/2)  / np.cos(30 / 180 * np.pi)
#             a1_ = a_lattice1  * np.array([1, 0])
#             a2_ = a_lattice2 * np.array([np.cos(30 / 180 * np.pi), np.sin(30 / 180 * np.pi)])
#             b1_ = np.array([0,0]) 
#             b2_ = a1_/3
            
#             bs =np.array([b1_,b2_])
#             x_size_ = 100000 / 2 
#             y_size_ = 100000
#             lattice = Lattice(a1_ , a2_, x_size_, y_size_,pixel_res, [[circle, 0, 0, d1/2],[circle, 0, 0, d2/2]], bs, pattern_name=name)
            
#             pat_str += lattice.pat_str + "\n"*3
#             draw_strs += lattice.draw_latt_str + "\n"*5


#%% semenoff circle no overlap

# overlaps_sq = [1]
# d_pillars_sq = [2400]
# onsite_diff = [0.8]

overlaps_sq = [0.9, 1.00, 1.05] # Overlap larger pillar
d_pillars_sq = [2000, 2200] # Diameter
onsite_diff = [0.75, 0.85] #Percentage smaller to larger

unit_cells_x = 5
unit_cells_y = 18
offset = 3000
increment = 2
dwell_time = 200

pat_str = ""
cntrl_str = ""

for v in overlaps_sq:
    for d_pillar in d_pillars_sq:
        for d_onsite in onsite_diff: 
            
            name = f"semenoff_v{v}_d{d_pillar}_diff{d_onsite}_l"
            
            d1 = d_pillar
            d2 = d_pillar  * d_onsite
                        
            a = d_pillar * v 
            a_lattice1 = 3 * a 
            a_lattice2 = (3*a/2)  / np.cos(30 / 180 * np.pi)
            a1_ = a_lattice1  * np.array([1, 0])
            a2_ = a_lattice2 * np.array([np.cos(30 / 180 * np.pi), np.sin(30 / 180 * np.pi)])
            b1_ = np.array([0,0]) 
            b2_ = a1_/3
            
            
            d1 = d_pillar *d_onsite
            d2 = d_pillar 
            
            name = f"semenoff_v{v}_d{d_pillar}_diff{d_onsite}_l"

            pat_str += "\n" + "D " + name + ", " + str(int(a_lattice1)) + ", " +  str(int(a_lattice2)) +", " + str(int(unit_cells_x)) + ", " +  str(int(unit_cells_y))+ "\n"
            pat_str += "I " + str(int(increment)) + "\n"
            pat_str += "C " + str(int(dwell_time)) + "\n"
            
            pat_str += "Circle "+str(int(offset+a1_[0]))+", "+str(int(offset+a1_[1]))+", "+str(int(d1/2)) + "\n"
            pat_str += "Circle "+str(int(offset+a1_[0]+b2_[0]))+", "+str(int(offset+a1_[1]+b2_[1]))+", "+str(int(d2/2)) + "\n"
            
            pat_str += "Circle "+str(int(offset+a2_[0]))+", "+str(int(offset+ a2_[1]))+", "+str(int(d1/2)) + "\n"
            pat_str += "Circle "+str(int(offset+a2_[0]+b2_[0]))+", "+str(int(offset+ a2_[1]+b2_[1]))+", "+str(int(d2/2)) + "\n"
            pat_str +=  "END" + "\n"
            
            cntrl_str += f"draw({name})\n"
            
        
        
            name = f"semenoff_v{v}_d{d_pillar}_diff{d_onsite}_edge_l"

            pat_str += "\n" + "D " + name + ", " + str(int(a_lattice1)) + ", " +  str(int(a_lattice2)) +", " + "1" + ", " +  str(int(unit_cells_y))+ "\n"
            pat_str += "I " + str(int(increment)) + "\n"
            pat_str += "C " + str(int(dwell_time)) + "\n"
            
            pat_str += "Circle "+str(int(offset+a1_[0]*unit_cells_x + a2_[0]))+", "+str(int(offset+a1_[1]*unit_cells_x+ a2_[1]))+", "+str(int(d1/2)) + "\n"
            pat_str += "Circle "+str(int(offset+a1_[0]*unit_cells_x+b2_[0] + a2_[0]))+", "+str(int(offset+a1_[1]*unit_cells_x+b2_[1]+ a2_[1]))+", "+str(int(d2/2)) + "\n"
            pat_str += "Circle "+str(int(offset+a1_[0]*(unit_cells_x+1)))+", "+str(int(offset+a1_[1]*(unit_cells_x+1)))+", "+str(int(d1/2)) + "\n"
            pat_str +=  "END" + "\n"
            
            cntrl_str += f"draw({name})\n"
            
            
            
            d1 = d_pillar
            d2 = d_pillar * d_onsite
            offset_x = (unit_cells_x+1) *a_lattice1
            
            
            name = f"semenoff_v{v}_d{d_pillar}_diff{d_onsite}_r"
            
            pat_str += "\n" + "D " + name + ", " + str(int(a_lattice1)) + ", " +  str(int(a_lattice2)) +", " + str(int(unit_cells_x)) + ", " +  str(int(unit_cells_y))+ "\n"
            pat_str += "I " + str(int(increment)) + "\n"
            pat_str += "C " + str(int(dwell_time)) + "\n"*2
            
            pat_str += "Circle "+str(int(offset_x + offset+a1_[0])) + ", " + str(int(offset + a1_[1])) + ", " + str(int(d1/2)) + "\n"
            pat_str += "Circle "+str(int(offset_x + offset+a1_[0] + b2_[0])) + ", "+str(int(offset + a1_[1] + b2_[1]))+", "+str(int(d2/2)) + "\n"
            
            pat_str += "Circle "+str(int(offset_x + offset+a2_[0]))+", "+str(int(offset+ a2_[1]))+", "+str(int(d1/2)) + "\n"
            pat_str += "Circle "+str(int(offset_x + offset+a2_[0]+b2_[0]))+", "+str(int(offset+ a2_[1]+b2_[1]))+", "+str(int(d2/2)) + "\n"
            pat_str += "END" + "\n"
            
            cntrl_str += f"draw({name})\n"
            
            
            
            name = f"semenoff_v{v}_d{d_pillar}_diff{d_onsite}_edge_r"
            
            pat_str += "\n" + "D " + name + ", " + str(int(a_lattice1)) + ", " +  str(int(a_lattice2)) +", " + "1" + ", " +  str(int(unit_cells_y))+ "\n"
            pat_str += "I " + str(int(increment)) + "\n"
            pat_str += "C " + str(int(dwell_time)) + "\n"
            
            pat_str += "Circle "+str(int(offset_x + offset + b2_[0] ))+", "+str(int(offset + b2_[1]))+", "+str(int(d2/2)) + "\n"
            pat_str += "END" + "\n"
            
            cntrl_str += f"draw({name})\n"
            
            
            
            name = f"semenoff_v{v}_d{d_pillar}_diff{d_onsite}_marker"
            
            pat_str += "\n" + "D " + name + "\n"
            pat_str += "I " + str(int(increment)) + "\n"
            pat_str += "C " + str(int(dwell_time)) + "\n"
            
            pat_str += "Circle "+str(int(offset + a1_[0] * (unit_cells_x+1) + a/2)) + ", " + str(int(offset + a_lattice2 - 4000))+", "+str(1250) + "\n"
            pat_str += "Circle "+str(int(offset + a1_[0] * (unit_cells_x+1) + a/2)) + ", " + str(int(offset + (unit_cells_y+1) * a_lattice2 + 4000 - a_lattice2/2)) + ", " + str(1250) + "\n"
            pat_str += "END" + "\n"
            
            cntrl_str += f"draw({name})\n" + "\n"*2


#%% export pattern file

# file = open("semenoff_pat.txt", "w")
# file.write(pat_str)
# file.close()

# file = open("semenoff_draw.txt", "w")
# file.write(cntrl_str)
# file.close()
