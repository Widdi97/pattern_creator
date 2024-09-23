# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 16:07:35 2024

@author: chm66em
"""

from generate_pattern import Pattern, circle, Lattice
import numpy as np

pat_str = ""
draw_strs = ""
pixel_res = 75

d = 2.5
a =3*d 

vc_i = 0.9
vc_e = 0.95

a1_ = a * np.array([1, 0])
a2_ = a * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])


b1_ = -a2_/3 
b2_ = a1_ /3 + -a2_/3
b3_ = a1_/3
b4_ = a2_/3
b5_ = -a1_/3 + a2_/3
b6_ = -a1_/3

bs =vc_i* np.array([b1_, b2_, b3_, b4_, b5_, b6_])*-1
x_size_ = 10 * a
y_size_ = 8 * a
lattice = Lattice(a1_ * vc_e, a2_* vc_e, x_size_, y_size_, 0.08 * a, [[circle, 0, 0, a/(3*2)] for b in bs], bs, pattern_name = "test")


pat_str += lattice.pat_str + "\n"*3
draw_strs += lattice.draw_latt_str + "\n"*5


file = open("pat_string.txt", "w")
file.write(pat_str)
file.close()

file = open("draw_strs.txt", "w")
file.write(draw_strs)
file.close()

#%% Not perfectly working 


# from generate_pattern import Pattern, circle, Lattice
# import numpy as np


# # # weird lattice
# # a = 2000
# # a1_ = a * np.array([1, 0])
# # a2_ = a * np.array([1/4, 1])
# # x_size_ = 20 * a
# # y_size_ = 16 * a
# # lattice = Lattice(a1_, a2_, x_size_, y_size_, 0.08 * a, [[circle, 0, 0, 0.4 * a]])
# # print(lattice.pat_str)

# vc_i = 0.8
# vc_e = 0.98
# vs_i = 0.92
# vs_e = 0.74

# # kagome 
# a = 3*2000
# a1_ = a * np.array([1, 0])
# a2_ = a * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])

# b1_ = np.array([0, 0])
# b2_ = vc_i*( a1_ / 3)
# b3_ = vc_i* (a1_ / 3 +  a2_ / 3)
# b4_ =vc_i* ( 2* a2_ / 3)
# b5_ = vc_i* (-a1_ / 3 + 2* a2_ / 3)
# b6_ =vc_i*  (-a1_ / 3 +  a2_ / 3)
# bs = np.array([b1_, b2_, b3_, b4_, b5_, b6_])
# x_size_ = 10 * a
# y_size_ = 8 * a
# lattice = Lattice(a1_, a2_, x_size_, y_size_, 0.08 * a, [[circle, 0, 0, 0.1 * a] for b in bs], bs)


# plt.plot(for b in bs)