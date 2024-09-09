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
overlapp_list = [0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
resolution_ratio = 10
file_name = "trimers_DO.pat"

with open(file_name, 'w') as file:
    for diameter in diameter_list:
        dia_string = f"{diameter}".replace(".","p")
        file.write("D trimers_do_"+ dia_string + '\n' + "I 1" + '\n' + "C 100" + '\n')
        resolution = round(diameter * resolution_ratio) 
        off = resolution/2
        start_time = time.time()
        if diameter == 6.0:
            offx = 35 * 1e3
        else:
            offx = 25 * 1e3
        for overlapp in overlapp_list:
            
            pn = f"tris_d{diameter}"
            pattern_name = pn.replace(".","p")
            print(pn)
            position = overlapp_list.index(overlapp)
            
            # intitialize pattern object
            pattern = Pattern(diameter*(1+overlapp)*1e3+off, (diameter*(np.sqrt(3)/2+overlapp))*1e3+off/2+off, resolution)

            # add all circles
            pattern.add_parametrized_shape(circle, diameter/2*1e3, (diameter*(np.sqrt(3)/2+overlapp-0.5))*1e3, diameter/2*1e3)
            pattern.add_parametrized_shape(circle, diameter*(.5+overlapp)*1e3, (diameter*(np.sqrt(3)/2+overlapp-0.5))*1e3, diameter/2*1e3)
            pattern.add_parametrized_shape(circle, (diameter*(1+overlapp))/2*1e3, diameter/2*1e3, diameter/2*1e3)

            # generate .pat string and export
            pattern_string = pattern.export_pattern(complete=False, export=False,offsetx=offx*position) 
            file.write(pattern_string + '\n')
        file.write("END"+ '\n')
        end_time=time.time()
        duration = end_time - start_time
        print(f"this pattern took {duration:.4f} seconds" + '\n')
    

#%%
