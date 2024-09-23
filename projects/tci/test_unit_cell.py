# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 13:47:16 2024

@author: chm66em
"""


from generate_pattern import Pattern, circle, Lattice
import numpy as np


d_list = [2000, 2000, 2200, 2500]

v_list  = [0.7, 0.8, 0.9, 1, 1.1]

for d in d_list:
    for v in v_list:
        
        a = 3* d*v
        
        a1_ = a * np.array([1, 0])
        a2_ = a * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])
        
        b1_ = np.array([0, 0])
        b2_ = ( a1_ / 3)
        b3_ =  (a1_ / 3 +  a2_ / 3)
        b4_ = ( 2* a2_ / 3)
        b5_ = (-a1_ / 3 + 2* a2_ / 3)
        b6_ =  (-a1_ / 3 +  a2_ / 3)
        bs = np.array([b1_, b2_, b3_, b4_, b5_, b6_])
        
        bs = bs + np.array([d,d/2 ])
        pat_str = ""
        draw_strs = ""
        pixel_res = 25
        
        width = a+d/2
        
        
        pattern = Pattern(width, width, 100)
        
        for b in bs:
            pattern.add_parametrized_shape(circle, b[0], b[1], d/2)
        pattern.visualize()