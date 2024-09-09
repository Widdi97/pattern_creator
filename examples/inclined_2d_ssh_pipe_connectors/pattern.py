from generate_pattern import Pattern, circle, ellipse, rectangle, rectangle_point
from shape_intersections import find_intersections
from math import pi
import numpy as np
import matplotlib.pyplot as plt

a = 6000 # um
r = 1200

resolution = 300 # um

tx = 600
ty = 400
t = 1300

#%% bulk
pattern = Pattern(a, a, resolution, pattern_name = "bulk", increment=2, dwell_time=200)

for i in range(2):
    for j in range(2):
        pattern.add_parametrized_shape(circle, a/4 + i*a/2, a/4 + j*a/2, r)

#t
#x dir
pattern.add_parametrized_shape(rectangle, a/4, a/4-t/2, 3*a/4, a/4+t/2)
pattern.add_parametrized_shape(rectangle, -a/4, 3*a/4-t/2, a/4, 3*a/4+t/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, 3*a/4-t/2, 5*a/4, 3*a/4+t/2)

#y dir
pattern.add_parametrized_shape(rectangle, 3*a/4-t/2, a/4, 3*a/4+t/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, -a/4, a/4+t/2, a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, 3*a/4, a/4+t/2, 5*a/4)


#tx
pattern.add_parametrized_shape(rectangle, a/4, 3*a/4-tx/2, 3*a/4, 3*a/4+tx/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, a/4-tx/2, 5*a/4, a/4+tx/2)
pattern.add_parametrized_shape(rectangle, -a/4, a/4-tx/2, a/4, a/4+tx/2)

#ty
pattern.add_parametrized_shape(rectangle, a/4-ty/2, a/4, a/4+ty/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, 3*a/4, 3*a/4+ty/2, 5*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, -a/4, 3*a/4+ty/2, 3*a/4)



pattern.visualize()
# pattern.export()
# print(pattern.export_pattern())

#%% top edge

pattern = Pattern(a, a, resolution, pattern_name = "top_edge", increment=2, dwell_time=200)

for i in range(2):
    for j in range(2):
        pattern.add_parametrized_shape(circle, a/4 + i*a/2, a/4 + j*a/2, r)

#t
#x dir
pattern.add_parametrized_shape(rectangle, a/4, a/4-t/2, 3*a/4, a/4+t/2)
pattern.add_parametrized_shape(rectangle, -a/4, 3*a/4-t/2, a/4, 3*a/4+t/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, 3*a/4-t/2, 5*a/4, 3*a/4+t/2)

#y dir
pattern.add_parametrized_shape(rectangle, 3*a/4-t/2, a/4, 3*a/4+t/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, -a/4, a/4+t/2, a/4)
# pattern.add_parametrized_shape(rectangle, a/4-t/2, 3*a/4, a/4+t/2, 5*a/4)


#tx
pattern.add_parametrized_shape(rectangle, a/4, 3*a/4-tx/2, 3*a/4, 3*a/4+tx/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, a/4-tx/2, 5*a/4, a/4+tx/2)
pattern.add_parametrized_shape(rectangle, -a/4, a/4-tx/2, a/4, a/4+tx/2)

#ty
pattern.add_parametrized_shape(rectangle, a/4-ty/2, a/4, a/4+ty/2, 3*a/4)
# pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, 3*a/4, 3*a/4+ty/2, 5*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, -a/4, 3*a/4+ty/2, 3*a/4)



pattern.visualize()
# pattern.export()
# print(pattern.export_pattern())


#%% bottom
pattern = Pattern(a, a, resolution, pattern_name = "bottom", increment=2, dwell_time=200)

for i in range(2):
    for j in range(2):
        pattern.add_parametrized_shape(circle, a/4 + i*a/2, a/4 + j*a/2, r)

#t
#x dir
pattern.add_parametrized_shape(rectangle, a/4, a/4-t/2, 3*a/4, a/4+t/2)
pattern.add_parametrized_shape(rectangle, -a/4, 3*a/4-t/2, a/4, 3*a/4+t/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, 3*a/4-t/2, 5*a/4, 3*a/4+t/2)

#y dir
pattern.add_parametrized_shape(rectangle, 3*a/4-t/2, a/4, 3*a/4+t/2, 3*a/4)
# pattern.add_parametrized_shape(rectangle, a/4-t/2, -a/4, a/4+t/2, a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, 3*a/4, a/4+t/2, 5*a/4)


#tx
pattern.add_parametrized_shape(rectangle, a/4, 3*a/4-tx/2, 3*a/4, 3*a/4+tx/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, a/4-tx/2, 5*a/4, a/4+tx/2)
pattern.add_parametrized_shape(rectangle, -a/4, a/4-tx/2, a/4, a/4+tx/2)

#ty
pattern.add_parametrized_shape(rectangle, a/4-ty/2, a/4, a/4+ty/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, 3*a/4, 3*a/4+ty/2, 5*a/4)
# pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, -a/4, 3*a/4+ty/2, 3*a/4)



pattern.visualize()
# pattern.export()
# print(pattern.export_pattern())


#%% right
pattern = Pattern(a, a, resolution, pattern_name = "right", increment=2, dwell_time=200)

for i in range(2):
    for j in range(2):
        pattern.add_parametrized_shape(circle, a/4 + i*a/2, a/4 + j*a/2, r)

#t
#x dir
pattern.add_parametrized_shape(rectangle, a/4, a/4-t/2, 3*a/4, a/4+t/2)
pattern.add_parametrized_shape(rectangle, -a/4, 3*a/4-t/2, a/4, 3*a/4+t/2)
# pattern.add_parametrized_shape(rectangle, 3*a/4, 3*a/4-t/2, 5*a/4, 3*a/4+t/2)

#y dir
pattern.add_parametrized_shape(rectangle, 3*a/4-t/2, a/4, 3*a/4+t/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, -a/4, a/4+t/2, a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, 3*a/4, a/4+t/2, 5*a/4)


#tx
pattern.add_parametrized_shape(rectangle, a/4, 3*a/4-tx/2, 3*a/4, 3*a/4+tx/2)
# pattern.add_parametrized_shape(rectangle, 3*a/4, a/4-tx/2, 5*a/4, a/4+tx/2)
pattern.add_parametrized_shape(rectangle, -a/4, a/4-tx/2, a/4, a/4+tx/2)

#ty
pattern.add_parametrized_shape(rectangle, a/4-ty/2, a/4, a/4+ty/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, 3*a/4, 3*a/4+ty/2, 5*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, -a/4, 3*a/4+ty/2, 3*a/4)



pattern.visualize()
# pattern.export()
# print(pattern.export_pattern())


#%% left
pattern = Pattern(a, a, resolution, pattern_name = "left", increment=2, dwell_time=200)

for i in range(2):
    for j in range(2):
        pattern.add_parametrized_shape(circle, a/4 + i*a/2, a/4 + j*a/2, r)

#t
#x dir
pattern.add_parametrized_shape(rectangle, a/4, a/4-t/2, 3*a/4, a/4+t/2)
# pattern.add_parametrized_shape(rectangle, -a/4, 3*a/4-t/2, a/4, 3*a/4+t/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, 3*a/4-t/2, 5*a/4, 3*a/4+t/2)

#y dir
pattern.add_parametrized_shape(rectangle, 3*a/4-t/2, a/4, 3*a/4+t/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, -a/4, a/4+t/2, a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, 3*a/4, a/4+t/2, 5*a/4)


#tx
pattern.add_parametrized_shape(rectangle, a/4, 3*a/4-tx/2, 3*a/4, 3*a/4+tx/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, a/4-tx/2, 5*a/4, a/4+tx/2)
# pattern.add_parametrized_shape(rectangle, -a/4, a/4-tx/2, a/4, a/4+tx/2)

#ty
pattern.add_parametrized_shape(rectangle, a/4-ty/2, a/4, a/4+ty/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, 3*a/4, 3*a/4+ty/2, 5*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, -a/4, 3*a/4+ty/2, 3*a/4)



pattern.visualize()
# pattern.export()
# print(pattern.export_pattern())


#%% top_left
pattern = Pattern(a, a, resolution, pattern_name = "top_left", increment=2, dwell_time=200)

for i in range(2):
    for j in range(2):
        pattern.add_parametrized_shape(circle, a/4 + i*a/2, a/4 + j*a/2, r)

#t
#x dir
pattern.add_parametrized_shape(rectangle, a/4, a/4-t/2, 3*a/4, a/4+t/2)
# pattern.add_parametrized_shape(rectangle, -a/4, 3*a/4-t/2, a/4, 3*a/4+t/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, 3*a/4-t/2, 5*a/4, 3*a/4+t/2)

#y dir
pattern.add_parametrized_shape(rectangle, 3*a/4-t/2, a/4, 3*a/4+t/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, -a/4, a/4+t/2, a/4)
# pattern.add_parametrized_shape(rectangle, a/4-t/2, 3*a/4, a/4+t/2, 5*a/4)


#tx
pattern.add_parametrized_shape(rectangle, a/4, 3*a/4-tx/2, 3*a/4, 3*a/4+tx/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, a/4-tx/2, 5*a/4, a/4+tx/2)
# pattern.add_parametrized_shape(rectangle, -a/4, a/4-tx/2, a/4, a/4+tx/2)

#ty
pattern.add_parametrized_shape(rectangle, a/4-ty/2, a/4, a/4+ty/2, 3*a/4)
# pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, 3*a/4, 3*a/4+ty/2, 5*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, -a/4, 3*a/4+ty/2, 3*a/4)



pattern.visualize()
# pattern.export()
# print(pattern.export_pattern())


#%% bottom_left
pattern = Pattern(a, a, resolution, pattern_name = "bottom_left", increment=2, dwell_time=200)

for i in range(2):
    for j in range(2):
        pattern.add_parametrized_shape(circle, a/4 + i*a/2, a/4 + j*a/2, r)

#t
#x dir
pattern.add_parametrized_shape(rectangle, a/4, a/4-t/2, 3*a/4, a/4+t/2)
# pattern.add_parametrized_shape(rectangle, -a/4, 3*a/4-t/2, a/4, 3*a/4+t/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, 3*a/4-t/2, 5*a/4, 3*a/4+t/2)

#y dir
pattern.add_parametrized_shape(rectangle, 3*a/4-t/2, a/4, 3*a/4+t/2, 3*a/4)
# pattern.add_parametrized_shape(rectangle, a/4-t/2, -a/4, a/4+t/2, a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, 3*a/4, a/4+t/2, 5*a/4)


#tx
pattern.add_parametrized_shape(rectangle, a/4, 3*a/4-tx/2, 3*a/4, 3*a/4+tx/2)
pattern.add_parametrized_shape(rectangle, 3*a/4, a/4-tx/2, 5*a/4, a/4+tx/2)
# pattern.add_parametrized_shape(rectangle, -a/4, a/4-tx/2, a/4, a/4+tx/2)

#ty
pattern.add_parametrized_shape(rectangle, a/4-ty/2, a/4, a/4+ty/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, 3*a/4, 3*a/4+ty/2, 5*a/4)
# pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, -a/4, 3*a/4+ty/2, 3*a/4)



pattern.visualize()
# pattern.export()
# print(pattern.export_pattern())


#%% bottom_right
pattern = Pattern(a, a, resolution, pattern_name = "bottom_right", increment=2, dwell_time=200)

for i in range(2):
    for j in range(2):
        pattern.add_parametrized_shape(circle, a/4 + i*a/2, a/4 + j*a/2, r)

#t
#x dir
pattern.add_parametrized_shape(rectangle, a/4, a/4-t/2, 3*a/4, a/4+t/2)
pattern.add_parametrized_shape(rectangle, -a/4, 3*a/4-t/2, a/4, 3*a/4+t/2)
# pattern.add_parametrized_shape(rectangle, 3*a/4, 3*a/4-t/2, 5*a/4, 3*a/4+t/2)

#y dir
pattern.add_parametrized_shape(rectangle, 3*a/4-t/2, a/4, 3*a/4+t/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, -a/4, a/4+t/2, a/4)
pattern.add_parametrized_shape(rectangle, a/4-t/2, 3*a/4, a/4+t/2, 5*a/4)


#tx
pattern.add_parametrized_shape(rectangle, a/4, 3*a/4-tx/2, 3*a/4, 3*a/4+tx/2)
# pattern.add_parametrized_shape(rectangle, 3*a/4, a/4-tx/2, 5*a/4, a/4+tx/2)
pattern.add_parametrized_shape(rectangle, -a/4, a/4-tx/2, a/4, a/4+tx/2)

#ty
pattern.add_parametrized_shape(rectangle, a/4-ty/2, a/4, a/4+ty/2, 3*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, 3*a/4, 3*a/4+ty/2, 5*a/4)
pattern.add_parametrized_shape(rectangle, 3*a/4-ty/2, -a/4, 3*a/4+ty/2, 3*a/4)



pattern.visualize()
# pattern.export()
# print(pattern.export_pattern())