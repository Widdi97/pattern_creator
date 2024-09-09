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

diameter = 2.5
overlapp1_list = [0.9]
overlapp2_list = [0.8]
resolution_ratio = 40
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
        pn1 = f"honeytopo_d{diameter}_va{overlapp1}_vb{overlapp2}_1,{round((2*diameter*overlapp1 + diameter*overlapp2)*1000)},{round(12*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)},7,2"
        pattern_name1 = pn1.replace(".","p")
        print(pn1)
        pn2 = f"honeytopo_d{diameter}_va{overlapp1}_vb{overlapp2}_2,{round((2*diameter*overlapp1 + diameter*overlapp2)*1000)},{round(10*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)},8,2"
        pattern_name2 = pn2.replace(".","p")
        print(pn2)
        pn3 = f"honeytopo_d{diameter}_va{overlapp1}_vb{overlapp2}_3,{round((2*diameter*overlapp1 + diameter*overlapp2)*1000)},{round(8*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)},9,2"
        pattern_name3 = pn3.replace(".","p")
        print(pn3)
        pn4 = f"honeytopo_d{diameter}_va{overlapp1}_vb{overlapp2}_4,{round((2*diameter*overlapp1 + diameter*overlapp2)*1000)},{round(6*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)},10,2"
        pattern_name4 = pn4.replace(".","p")
        print(pn4)
        pn5 = f"honeytopo_d{diameter}_va{overlapp1}_vb{overlapp2}_5,{round((2*diameter*overlapp1 + diameter*overlapp2)*1000)},{round(4*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)},11,2"
        pattern_name5 = pn5.replace(".","p")
        print(pn5)
        pn6 = f"honeytopo_d{diameter}_va{overlapp1}_vb{overlapp2}_6,{round((2*diameter*overlapp1 + diameter*overlapp2)*1000)},{round(2*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)},12,2"
        pattern_name6 = pn6.replace(".","p")
        print(pn6)
        pn7 = f"honeytopo_d{diameter}_va{overlapp1}_vb{overlapp2}_7,{round((2*diameter*overlapp1 + diameter*overlapp2)*1000)},{round(0*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)},13,1"
        pattern_name7 = pn7.replace(".","p")
        print(pn7)
        
        offsetx0 = round(diameter*(overlapp1+0.5*overlapp2)*1000)
        offsety0 = round((np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)
        
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
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = 6*offsetx0, offsety = 0 - round(0*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000))
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
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = 5*offsetx0, offsety = 1*offsety0 + round(2*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000))
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name3)
        
        # add all circles
        for i in range(6):
            corners = hex_corners(center,cc_dist1,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        for i in range(3):
            corners = hex_corners(center,cc_dist2,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = 4*offsetx0, offsety = 2*offsety0 + round(4*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000))
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name4)
        
        # add all circles
        for i in range(6):
            corners = hex_corners(center,cc_dist1,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        for i in range(3):
            corners = hex_corners(center,cc_dist2,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = 3*offsetx0, offsety = 3*offsety0 + round(6*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000))
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name5)
        
        # add all circles
        for i in range(6):
            corners = hex_corners(center,cc_dist1,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        for i in range(3):
            corners = hex_corners(center,cc_dist2,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = 2*offsetx0, offsety = 4*offsety0 + round(8*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000))
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name6)
        
        # add all circles
        for i in range(6):
            corners = hex_corners(center,cc_dist1,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        for i in range(3):
            corners = hex_corners(center,cc_dist2,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = 1*offsetx0, offsety = 5*offsety0 + round(10*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000))
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name7)
        
        # add all circles
        for i in range(6):
            corners = hex_corners(center,cc_dist1,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        for i in range(3):
            corners = hex_corners(center,cc_dist2,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = 0*offsetx0, offsety = 6*offsety0 + round(12*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000))
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
