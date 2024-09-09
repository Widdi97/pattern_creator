# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:59:14 2024

@author: sib16nk
"""

from generate_pattern import Pattern, circle, ellipse
from math import pi
import numpy as np
import time

diameter = 2.0
overlappx = 0.9
overlappy = 0.7
resolution_ratio = 15

resolution = round(diameter * resolution_ratio) 
off = resolution/2
start_time = time.time()

# intitialize pattern object
pattern = Pattern(diameter*(1+overlappx)*1e3+off, diameter*(1+overlappy)*1e3+off, resolution)


# add all circles
pattern.add_parametrized_shape(circle, diameter/2*1e3, diameter/2*1e3, diameter/2*1e3)
pattern.add_parametrized_shape(circle, diameter*(.5+overlappx)*1e3, diameter/2*1e3, diameter/2*1e3)
pattern.add_parametrized_shape(circle, diameter/2*1e3, diameter*(.5+overlappy)*1e3, diameter/2*1e3)
pattern.add_parametrized_shape(circle, diameter*(.5+overlappx)*1e3, diameter*(.5+overlappy)*1e3, diameter/2*1e3)

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
