# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:59:14 2024

@author: sib16nk
"""

from generate_pattern import Pattern, circle, ellipse
from math import pi, cos, sin
import numpy as np
import time

diameter = 2.0
overlapp1 = 0.9
overlapp2 = 0.7
resolution_ratio = 40
flat_top = False

def hex_corners(center, distance, i, flat_top = True):
    if flat_top:
        angle_deg = 60 * i
    else:
        angle_deg = 60 * i - 30
    angle_rad = pi / 180 * angle_deg
    return([center[0] + distance * np.cos(angle_rad), center[1] + distance * np.sin(angle_rad)])


if flat_top:
    width = 2*diameter*overlapp1 + diameter
    height = np.sqrt(3)*diameter*overlapp1 + diameter
else:
    height = 2*diameter*overlapp1 + diameter
    width = np.sqrt(3)*diameter*overlapp1 + diameter
    
center = [width/2,height/2]
cc_dist1 = diameter * overlapp1
cc_dist2 = diameter * (overlapp1 + overlapp2)
        
resolution = round(diameter * resolution_ratio) 
off = resolution/2
start_time = time.time()

# intitialize pattern object
pattern = Pattern(width*1e3+off, height*1e3+off, resolution)

# add all circles
for i in range(3):
    corners = hex_corners(center,cc_dist1,i+4,flat_top)
    pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
for i in range(1):
    corners = hex_corners(center,cc_dist2,i,flat_top)
    pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")

# generate .pat string
pattern_string = pattern.export_pattern(complete=True, export=False)
nlines = pattern_string.count('\n') - 3

# print .pat string
print(pattern_string)

# plot
pattern.visualize()

end_time=time.time()
duration = end_time - start_time
print('\n' + f"this pattern took {duration:.4f} seconds and is {nlines} rectangles long" + '\n')

#%%
