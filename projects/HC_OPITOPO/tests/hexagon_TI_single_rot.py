# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:59:14 2024

@author: sib16nk
"""

from generate_pattern import Pattern, circle, ellipse
from math import pi, cos, sin
import numpy as np
import time
import itertools 

diameter = 2.0
overlapp1_list = [0.9]
overlapp2_list = [0.8]
resolution_ratio = 10
file_name = f"hexagon_TI_d{diameter}_SB.pat"

def hex_corners(center, distance, i):
    angle_deg = 60 * i# - 30
    angle_rad = pi / 180 * angle_deg
    return([center[0] + distance * np.cos(angle_rad), center[1] + distance * np.sin(angle_rad)])

with open(file_name, 'w') as file:
    # dia_string = f"{diameter}".replace(".","p")
    # file.write("D hex_TI_"+ dia_string + '\n' + "I 1" + '\n' + "C 100" + '\n')
    resolution = round(diameter * resolution_ratio)
    off = resolution/2
    for (overlapp1, overlapp2) in zip(overlapp1_list, overlapp2_list):
        start_time = time.time()
        pn1 = f"hexti_d{diameter}_va{overlapp1}_vb{overlapp2}_1,{round((2*diameter*overlapp1 + diameter*overlapp2)*1000)},{round(2*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)},5,5"
        pattern_name1 = pn1.replace(".","p")
        print(pn1)
        pn2 = f"hexti_d{diameter}_va{overlapp1}_vb{overlapp2}_2,{round((2*diameter*overlapp1 + diameter*overlapp2)*1000)},{round(2*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)},5,5"
        pattern_name2 = pn2.replace(".","p")
        print(pn2)
        
        width = 2*diameter*overlapp1 + diameter
        height = np.sqrt(3)*diameter*overlapp1 + diameter
            
        center = [width/2,height/2]
        cc_dist1 = diameter * overlapp1
        cc_dist2 = diameter * (overlapp1 + overlapp2)
                
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name1)
        
        # add all circles
        for i in range(6):
            corners = hex_corners(center,cc_dist1,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        for i in range(3):
            corners = hex_corners(center,cc_dist2,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False)
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name2)
        
        # add all circles
        for i in range(6):
            corners = hex_corners(center,cc_dist1,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        for i in range(3):
            corners = hex_corners(center,cc_dist2,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = round(diameter*(overlapp1+0.5*overlapp2)*1000), offsety = round((np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000))
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        end_time=time.time()
        duration = end_time - start_time
        
        # print .pat string
        print(pattern_string)
        
        # plot
        pattern.visualize()
        
        end_time=time.time()
        duration = end_time - start_time
        print('\n' + f"this pattern took {duration:.4f} seconds and is {nlines} rectangles long" + '\n')

#%%
