# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:59:14 2024

@author: sib16nk
"""

from generate_pattern import Pattern, circle, ellipse
from math import pi
import numpy as np
import time

diameter_list = [2.0, 3.0, 6.0]
overlappx_list = [0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
resolution_ratio = 15
file_name = "dimers.pat"

with open(file_name, 'w') as file:
    for diameter in diameter_list:
        resolution = round(diameter * resolution_ratio) 
        off = resolution/2
        for overlappx in overlappx_list:
            start_time = time.time()
            pn = f"dim_d{diameter}_v{overlappx}_res{resolution}"
            pattern_name = pn.replace(".","p")
            print(pn)
            
            # intitialize pattern object
            pattern = Pattern(diameter*(1+overlappx)*1e3+off, diameter*1e3+off, resolution, pattern_name)
            
            # add both circles
            pattern.add_parametrized_shape(circle, diameter/2*1e3, diameter/2*1e3, diameter/2*1e3)
            pattern.add_parametrized_shape(circle, diameter*(.5+overlappx)*1e3, diameter/2*1e3, diameter/2*1e3)          
            
            # generate .pat string and export
            pattern_string = pattern.export_pattern(complete=True, export=False) 
            file.write(pattern_string + '\n'+ '\n')
            nlines = pattern_string.count('\n') - 3
            end_time=time.time()
            duration = end_time - start_time
            print(f"this pattern took {duration:.4f} seconds and is {nlines} rectangles long" + '\n')
    

#%%
