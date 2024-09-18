# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 10:10:52 2024

@author: chm66em
"""

from generate_pattern import Pattern, circle, Lattice

import numpy as np
import matplotlib.pyplot as plt


d = 2000

v = 0.95
pixel_res = 75
x_size = 5
y_size = 18
offset = 7000
increment = 2
dwell_time = 200 


#%%
# a = d * v 

# Armchair at y
# a =  d * v 
# a_lattice = (3*a/2)  / np.cos(30 / 180 * np.pi)
# a1_ = a_lattice * np.array([1, 0])
# a2_ = a_lattice * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])
# b1_ = np.array([0,0]) 
# b2_ = 2*a1_/3 - a2_/3

# Zig-Zag at y
a = d * v 
a_lattice1 = 3 * a 
a_lattice2 = (3*a/2)  / np.cos(30 / 180 * np.pi)
a1_ = a_lattice1  * np.array([1, 0])
a2_ = a_lattice2 * np.array([np.cos(30 / 180 * np.pi), np.sin(30 / 180 * np.pi)])
b1_ = np.array([0,0]) 
b2_ = a1_/3

bs =np.array([b1_,b2_])
x_size_ = 10000
y_size_ = 10000
# lattice = Lattice(a1_ , a2_, x_size_, y_size_,pixel_res, [[circle, 0, 0, d1/2],[circle, 0, 0, d2/2]], bs)

#%%
# fac = 1
# plt.quiver(0,0, a1_[0], a1_[1], color=["r"], angles="xy", scale_units="xy", scale=1)

# plt.quiver(0,0, fac*a2_[0], fac*a2_[1], color=["b"], angles="xy", scale_units="xy", scale=1)

# plt.xlim(-50, 8000)
# plt.ylim(-50, 8000)

# plt.show()

#%%


d1 = d *0.8
d2 = d 



pattern_name = "Semenoff_left"
pat_str = ""
pat_str += "\n" + "D " + pattern_name + ", " + str(int(a_lattice1)) + ", " +  str(int(a_lattice2)) +", " + str(int(x_size)) + ", " +  str(int(y_size))+ "\n"
pat_str += "I " + str(int(increment)) + "\n"
pat_str += "C " + str(int(dwell_time)) + "\n"

pat_str += "Circle "+str(int(offset+a1_[0]))+", "+str(int(offset+a1_[1]))+", "+str(int(d1/2)) + "\n"
pat_str += "Circle "+str(int(offset+a1_[0]+b2_[0]))+", "+str(int(offset+a1_[1]+b2_[1]))+", "+str(int(d2/2)) + "\n"

pat_str += "Circle "+str(int(offset+a2_[0]))+", "+str(int(offset+ a2_[1]))+", "+str(int(d1/2)) + "\n"
pat_str += "Circle "+str(int(offset+a2_[0]+b2_[0]))+", "+str(int(offset+ a2_[1]+b2_[1]))+", "+str(int(d2/2)) + "\n"
pat_str +=  "END" + "\n"


# file = open("test_left.txt", "w")
# file.write(pat_str)
# file.close()

#%%

pattern_name = "Semenoff_edge_left"
# pat_str = ""
pat_str += "\n" + "D " + pattern_name + ", " + str(int(a_lattice1)) + ", " +  str(int(a_lattice2)) +", " + "1" + ", " +  str(int(y_size))+ "\n"
pat_str += "I " + str(int(increment)) + "\n"
pat_str += "C " + str(int(dwell_time)) + "\n"

pat_str += "Circle "+str(int(offset+a1_[0]*x_size + a2_[0]))+", "+str(int(offset+a1_[1]*x_size+ a2_[1]))+", "+str(int(d1/2)) + "\n"
pat_str += "Circle "+str(int(offset+a1_[0]*x_size+b2_[0] + a2_[0]))+", "+str(int(offset+a1_[1]*x_size+b2_[1]+ a2_[1]))+", "+str(int(d2/2)) + "\n"
pat_str += "Circle "+str(int(offset+a1_[0]*(x_size+1)))+", "+str(int(offset+a1_[1]*(x_size+1)))+", "+str(int(d1/2)) + "\n"
pat_str +=  "END" + "\n"


# file = open("edge_left.txt", "w")
# file.write(pat_str)
# file.close()


#%%
d1 = d 
d2 = d *0.8
offset_x = (x_size+1) *a_lattice1


pattern_name = "Semenoff_right"
# pat_str = ""
pat_str += "\n" + "D " + pattern_name + ", " + str(int(a_lattice1)) + ", " +  str(int(a_lattice2)) +", " + str(int(x_size)) + ", " +  str(int(y_size))+ "\n"
pat_str += "I " + str(int(increment)) + "\n"
pat_str += "C " + str(int(dwell_time)) + "\n"*2

pat_str += "Circle "+str(int(offset_x + offset+a1_[0]))+", "+str(int(offset+a1_[1]))+", "+str(int(d1/2)) + "\n"
pat_str += "Circle "+str(int(offset_x + offset+a1_[0]+b2_[0]))+", "+str(int(offset+a1_[1]+b2_[1]))+", "+str(int(d2/2)) + "\n"

pat_str += "Circle "+str(int(offset_x + offset+a2_[0]))+", "+str(int(offset+ a2_[1]))+", "+str(int(d1/2)) + "\n"
pat_str += "Circle "+str(int(offset_x + offset+a2_[0]+b2_[0]))+", "+str(int(offset+ a2_[1]+b2_[1]))+", "+str(int(d2/2)) + "\n"
pat_str += "END" + "\n"


# file = open("test_right.txt", "w")
# file.write(pat_str)
# file.close()

#%%

pattern_name = "Semenoff_edge_right"
# pat_str = ""
pat_str += "\n" + "D " + pattern_name + ", " + str(int(a_lattice1)) + ", " +  str(int(a_lattice2)) +", " + "1" + ", " +  str(int(y_size))+ "\n"
pat_str += "I " + str(int(increment)) + "\n"
pat_str += "C " + str(int(dwell_time)) + "\n"

pat_str += "Circle "+str(int(offset_x + offset+b2_[0] ))+", "+str(int(offset+b2_[1]))+", "+str(int(d2/2)) + "\n"


pat_str += "END" + "\n"


#%% Pillar to find edge

pattern_name = "marker"
# pat_str = ""
pat_str += "\n" + "D " + pattern_name + "\n"
pat_str += "I " + str(int(increment)) + "\n"
pat_str += "C " + str(int(dwell_time)) + "\n"

pat_str += "Circle "+str(int(offset+a1_[0]*(x_size+1)+a/2))+", "+str(int(offset + a_lattice2 - 4000))+", "+str(1250) + "\n"

pat_str += "Circle "+str(int(offset+a1_[0]*(x_size+1)+a/2))+", "+str(int(offset + (y_size+1) *a_lattice2 + 4000 - a_lattice2/2))+", "+str(1250) + "\n"


pat_str += "END" + "\n"

file = open("pillar_test.txt", "w")
file.write(pat_str)
file.close()

#%%
# fig, ax = plt.subplots()
# #plot rectangles
# for idx, rec_coords in enumerate(rects):
#     rect = patches.Rectangle([rec_coords[0], rec_coords[1]], rec_coords[2] - rec_coords[0], rec_coords[3] - rec_coords[1], linewidth=1, 
#                               edgecolor=colors(idx), facecolor="None", alpha=0.5, hatch="xxx")
#     ax.add_patch(rect)

# #plot shapes
# for parametrization, args in self.shapes:
#     plt.plot(*parametrization(np.linspace(0, 1, 100), *args), color="k")

# plt.xlabel("x")
# plt.ylabel("y")
# plt.axis('equal')
# fig.tight_layout()
# plt.savefig("plot.png", dpi=1000)
# plt.show()