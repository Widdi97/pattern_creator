# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:59:14 2024

@author: sib16nk
"""

from generate_pattern import Pattern, circle, ellipse
from math import pi
import numpy as np
import time

diameter_list = [2.0, 2.5, 3.0]
overlappx_list = [0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
resolution_ratio = 40
file_name = f"dimers_res.pat"

with open(file_name, 'w') as file:
    for diameter in diameter_list:
        dia_string = f"{diameter}".replace(".","p")
        file.write("D dimers_do_"+ dia_string + '\n' + "I 1" + '\n' + "C 100" + '\n')
        resolution = round(diameter * resolution_ratio)
        off = resolution/2
        start_time = time.time()
        if diameter == 6.0:
            offx = 35 * 1e3
        else:
            offx = 25 * 1e3
        for overlappx in overlappx_list:
            
            pn = f"dims_d{diameter}"
            pattern_name = pn.replace(".","p")
            print(pn)
            position = overlappx_list.index(overlappx)
            
            # intitialize pattern object
            pattern = Pattern(diameter*(1+overlappx)*1e3+off, diameter*1e3+off, resolution)
            
            # add both circles
            pattern.add_parametrized_shape(circle, diameter/2*1e3, diameter/2*1e3, diameter/2*1e3)
            pattern.add_parametrized_shape(circle, diameter*(.5+overlappx)*1e3, diameter/2*1e3, diameter/2*1e3)          
            
            # generate .pat string and export
            pattern_string = pattern.export_pattern(complete=False, export=False, offsetx=offx*position) 
            file.write(pattern_string + '\n')
        file.write("END"+ '\n')
        end_time=time.time()
        duration = end_time - start_time
        print(f"this pattern took {duration:.4f} seconds" + '\n')
    

#%%

