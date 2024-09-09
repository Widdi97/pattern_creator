# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:59:14 2024

@author: sib16nk
"""

from generate_pattern import Pattern, circle
from math import pi, ceil
import numpy as np
import time
#import itertools 

diameter = 2.0
overlapp1_list = [1.0,1.0,1.0,1.0,0.95,0.95,0.95,0.9,0.9,0.9,0.9,0.8]
overlapp2_list = [1.0,0.9,0.85,0.8,0.85,0.8,0.75,0.9,0.8,0.75,0.7,0.8]
resolution_ratio = 14
sizexum = 155 #aimed lattice size in um
sizeyum = 155
file_name = f"HC_OPITOPO_d{diameter}_res_{resolution_ratio}_SB.pat"

def hex_corners(center, distance, i, offsety=0):
    angle_deg = 60 * i - 30
    angle_rad = pi / 180 * angle_deg
    return([center[0] + distance * np.cos(angle_rad), center[1] + distance * np.sin(angle_rad)-offsety])

def round_up_even(number):
    # Runden Sie die Zahl zur nächsten ganzen Zahl auf
    round_up = ceil(number)
    
    # Überprüfen, ob die aufgerundete Zahl gerade ist
    if round_up % 2 != 0:
        # Wenn nicht, erhöhen Sie sie um 1, um zur nächsten geraden Zahl zu gelangen
        round_up += 1
    
    return round_up


with open(file_name, 'w') as file:
    # dia_string = f"{diameter}".replace(".","p")
    # file.write("D hex_TI_"+ dia_string + '\n' + "I 1" + '\n' + "C 100" + '\n')
    resolution = round(diameter * resolution_ratio)
    off = resolution/2
    for (overlapp1, overlapp2) in zip(overlapp1_list, overlapp2_list):
        start_time = time.time()
                
        width = np.sqrt(3)*diameter*overlapp1 + diameter
        height = 2*diameter*overlapp1 + diameter
            
        center = [width/2,height/2]
        cc_dist1 = diameter * overlapp1
        cc_dist2 = diameter * (overlapp1 + overlapp2)
        
        nx = round_up_even(sizexum//width)
        ny = round_up_even(sizeyum//height)
        repx = int(nx//2)
        
        print(nx*width)
        print(ny*height)
        
        shiftx = round(2*(np.sqrt(3)*diameter*overlapp1 + np.sqrt(3)/2*diameter*overlapp2)*1000)
        shifty = round((2*diameter*overlapp1 + diameter*overlapp2)*1000)
        pn1 = f"VA{overlapp1}_VB{overlapp2}_1,{shiftx},{shifty},{repx},{ny}"
        pattern_name1 = pn1.replace(".","p")
        print(pn1)
        pn2 = f"VA{overlapp1}_VB{overlapp2}_2,{shiftx},{shifty},{repx},{ny}"
        pattern_name2 = pn2.replace(".","p")
        print(pn2)
        pn3 = f"VA{overlapp1}_VB{overlapp2}_3,{shiftx},{shifty},{repx},1"
        pattern_name3 = pn3.replace(".","p")
        print(pn3)
        pn4 = f"VA{overlapp1}_VB{overlapp2}_4,{shiftx},{shifty},{repx},1"
        pattern_name4 = pn4.replace(".","p")
        print(pn4)
        pn5 = f"VA{overlapp1}_VB{overlapp2}_5,{shiftx},{shifty},1,{ny}"
        pattern_name5 = pn5.replace(".","p")
        print(pn5)
                        
        
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
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = shiftx/2, offsety = round(diameter*(overlapp1+0.5*overlapp2)*1000))
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name3)
        
        # add all circles
        for i in range(3):
            corners = hex_corners(center,cc_dist1,i+1, offsety = diameter*overlapp1 + diameter*overlapp2/2)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        for i in range(2):
            corners = hex_corners(center,cc_dist2,i+1, offsety = diameter*overlapp1 + diameter*overlapp2/2)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = shiftx/2)
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name4)
        
        # add all circles
        for i in range(3):
            corners = hex_corners(center,cc_dist1,i+4,)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        for i in range(1):
            corners = hex_corners(center,cc_dist2,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3, boolean_operation="subtract")
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False, offsety = ny * shifty)
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3
        
        # intitialize pattern object
        pattern = Pattern(width*1e3+off, height*1e3+off, resolution, pattern_name5)
        
        # add all circles
        for i in range(6):
            corners = hex_corners(center,cc_dist1,i)
            pattern.add_parametrized_shape(circle, corners[0]*1e3, corners[1]*1e3, diameter/2*1e3)
        
        # generate .pat string
        pattern_string = pattern.export_pattern(complete=True, export=False, offsetx = repx * shiftx)
        file.write(pattern_string + '\n'+ '\n')
        nlines = pattern_string.count('\n') - 3

        # print .pat string
        print(pattern_string)
        
        # plot
        #pattern.visualize()
        
        end_time=time.time()
        duration = end_time - start_time
        print('\n' + f"this pattern took {duration:.4f} seconds and is {nlines} rectangles long" + '\n')

#%%
