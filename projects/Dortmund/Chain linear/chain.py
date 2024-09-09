# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 08:46:42 2024

@author: sib16nk
"""

from generate_pattern import Pattern, circle, ellipse
from math import pi
import numpy as np
import time

diameter_list = [2.0, 3.0, 6.0]
overlappx_list = [0.7, 0.75, 0.8, 0.85, 0.9]
resolution_ratio = 10
file_name = "linear_chain_DO.pat"

with open(file_name, 'w') as file:
    for diameter in diameter_list:
        resolution = round(diameter * resolution_ratio) 
        off = resolution/2
        for overlappx in overlappx_list:
            start_time = time.time()
            pn = f"linstart_d{diameter}_v{overlappx}"
            pattern_name = pn.replace(".","p")
            print(pn)

            # intitialize first pattern object
            pattern = Pattern(diameter*1e3+off, diameter*1e3+off, resolution, pattern_name)

            # add circles; idea: use a single pillar as starting point
            pattern.add_parametrized_shape(circle, diameter/2*1e3, diameter/2*1e3, diameter/2*1e3)   
            
            # generate .pat string and export, including y-offset to correct ecp "shift mistake"
            pattern_string = pattern.export_pattern(complete=True, export=False, offsety = round(diameter*overlappx*1000)) 
            file.write(pattern_string + '\n'+ '\n')
            nlines = pattern_string.count('\n') - 3
            end_time=time.time()
            duration = end_time - start_time
            print(f"this pattern took {duration:.4f} seconds and is {nlines} rectangles long" + '\n')

            start_time = time.time()
            pn = f"lin_d{diameter}_v{overlappx},{round(diameter*overlappx*1000)},{round(diameter*overlappx*1000)},19,1"
            pattern_name = pn.replace(".","p")
            print(pn)
            
            # intitialize second pattern object
            pattern = Pattern(diameter*(1+overlappx)*1e3+off, diameter*1e3+off, resolution, pattern_name)

            # add all circles; idea: add single pillars -> no problem with alignment
            pattern.add_parametrized_shape(circle, diameter*(.5+overlappx)*1e3, diameter/2*1e3, diameter/2*1e3)
            pattern.add_parametrized_shape(circle, diameter/2*1e3, diameter/2*1e3, diameter/2*1e3, boolean_operation = "subtract")        
           
            # generate .pat string and export
            pattern_string = pattern.export_pattern(complete=True, export=False) 
            file.write(pattern_string + '\n'+ '\n')
            nlines = pattern_string.count('\n') - 3
            end_time=time.time()
            duration = end_time - start_time
            print(f"this pattern took {duration:.4f} seconds and is {nlines} rectangles long" + '\n')


#%%

