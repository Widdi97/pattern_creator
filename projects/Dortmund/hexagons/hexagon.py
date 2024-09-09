# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:59:14 2024

@author: sib16nk
"""

from generate_pattern import Pattern, circle, ellipse
from math import pi, cos, sin
import numpy as np
import time

diameter_list = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]
overlapp_list = [0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
resolution_ratio = 15
flat_top = False

def hex_corners(center, distance, i, flat_top = True):
    if flat_top:
        angle_deg = 60 * i
    else:
        angle_deg = 60 * i - 30
    angle_rad = pi / 180 * angle_deg
    return([center[0] + distance * np.cos(angle_rad), center[1] + distance * np.sin(angle_rad)])


if flat_top:
    file_name = "hexagons_flat.pat"
else:
   file_name = "hexagons_peak.pat" 


with open(file_name, 'w') as file:
    for diameter in diameter_list:
        resolution = round(diameter * resolution_ratio) 
        off = resolution/2
        for overlapp in overlapp_list:
            start_time = time.time()
            if flat_top:
                pn = f"hexf_d{diameter}_v{overlapp}_res{resolution}"
            else:
                pn = f"hexp_d{diameter}_v{overlapp}_res{resolution}"
            pattern_name = pn.replace(".","p")
            print(pn)
            if flat_top:
                width = 2*diameter*overlapp + diameter
                height = np.sqrt(3)*diameter*overlapp + diameter
            else:
                height = 2*diameter*overlapp + diameter
                width = np.sqrt(3)*diameter*overlapp + diameter
            center = [width/2,height/2]
            cc_dist = diameter * overlapp
            
            # intitialize pattern object
            pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name)
            
            # add all circles
            for i in range(6):
                corners = hex_corners(center,cc_dist,i,flat_top)
                pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
            
            # generate .pat string and export
            pattern_string = pattern.export_pattern(complete=True, export=False) 
            file.write(pattern_string + '\n'+ '\n')
            nlines = pattern_string.count('\n') - 3
            end_time=time.time()
            duration = end_time - start_time
            print(f"this pattern took {duration:.4f} seconds and is {nlines} rectangles long" + '\n')

#%%
