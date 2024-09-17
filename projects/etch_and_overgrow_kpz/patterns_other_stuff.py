from generate_pattern import Pattern, Lattice, circle, ellipse
from shape_intersections import find_intersections
from math import pi
import numpy as np
import matplotlib.pyplot as plt

pat_str = ""
draw_strs = ""
pixel_res = 25

#%% overlap series

# ds = [1.8e3, 2.1e3]
# vs = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]

# str_ = ""
# ax = np.array([1, 0]) * 15e3
# ay = np.array([0, 1]) * 12e3

# for d_idx, d in enumerate(ds):
#     r = d / 2
#     for v_idx, v in enumerate(vs):
        
#         offsets = 2 * d_idx * ax + (v_idx // 5) * ax + (v_idx % 5) * ay
#         # offsety = 
        
#         width = d * (1.2 + v)
#         height = 1.2 * d
#         pattern = Pattern(width, height, pixel_res)
#         x_c = width / 2
#         y_c = height / 2
#         pattern.add_parametrized_shape(circle, x_c - v * d / 2, y_c, r)
#         pattern.add_parametrized_shape(circle, x_c + v * d / 2, y_c, r)
#         pattern.visualize()
#         # print(offsets)
#         str_ += pattern.export_pattern(offsetx=offsets[0], offsety=offsets[1])
# print(str_)

#%% export pattern file

# file = open("misc_str.txt", "w")
# file.write(str_)
# file.close()

#%% 1d ssh chains

pixel_res = 100

d = 1.8e3
v0 = 1.05

a0 = v0 * d
axy = a0 / np.sqrt(2)


dvs = [-0.18, -0.09, 0.0, 0.09, 0.18]
str_ = ""

# add short chains
N = 5
for dv_idx, dv in enumerate(dvs):
    width = (d + axy) * 1.1
    height = 2 * axy
    
    
    pattern_bulk = Pattern(width, height, pixel_res)
    ay_num = pattern_bulk.y_ax[-1] + pixel_res
    x_c = pattern_bulk.x_ax[-1] / 2
    y_c = pattern_bulk.y_ax[-1] / 2
    
    
    bulk_str = f"D ssh_1d_short_bulk_{dv_idx+1}, 123, {pattern_bulk.y_ax[-1] + pixel_res}, 1, {N-1}"
    bulk_str += "\nI 2\nC 200\n"
    for i in range(-1, 2):
        pattern_bulk.add_parametrized_shape(circle, x_c + axy / 2, i * ay_num + y_c - ay_num / 4 - dv * ay_num / 4, d / 2)
        pattern_bulk.add_parametrized_shape(circle, x_c - axy / 2, i * ay_num + y_c + ay_num / 4 + dv * ay_num / 4, d / 2)
    pattern_bulk.visualize()
    bulk_str += pattern_bulk.export_pattern(offsetx=1000,offsety=1000)
    bulk_str += "END\n\n\n"
    
    top_str = f"D ssh_1d_short_top_{dv_idx+1}"
    top_str += "\nI 2\nC 200\n"
    i = -1
    pattern_top = Pattern(width, height, pixel_res)
    pattern_top.add_parametrized_shape(circle, x_c + axy / 2, i * ay_num + y_c - ay_num / 4 - dv * ay_num / 4, d / 2)
    pattern_top.add_parametrized_shape(circle, x_c + axy / 2, 0 * ay_num + y_c - ay_num / 4 - dv * ay_num / 4, d / 2)
    pattern_top.add_parametrized_shape(circle, x_c - axy / 2, i * ay_num + y_c + ay_num / 4 + dv * ay_num / 4, d / 2)
    pattern_top.visualize()
    top_str += pattern_top.export_pattern(offsetx=1000,offsety=1000 + N * ay_num)
    top_str += "END\n\n\n"
    
    bot_str = f"D ssh_1d_short_bot_{dv_idx+1}"
    bot_str += "\nI 2\nC 200\n"
    i = 1
    pattern_bot = Pattern(width, height, pixel_res)
    pattern_bot.add_parametrized_shape(circle, x_c + axy / 2, i * ay_num + y_c - ay_num / 4 - dv * ay_num / 4, d / 2)
    pattern_bot.add_parametrized_shape(circle, x_c - axy / 2, i * ay_num + y_c + ay_num / 4 + dv * ay_num / 4, d / 2)
    pattern_bot.add_parametrized_shape(circle, x_c - axy / 2, 0 * ay_num + y_c + ay_num / 4 + dv * ay_num / 4, d / 2)
    pattern_bot.visualize()
    bot_str += pattern_bot.export_pattern(offsetx=1000,offsety=1000)
    bot_str += "END\n\n\n"
    
    str_ = str_ + bulk_str + top_str + bot_str


# add long chains
N = 20
for dv_idx, dv in enumerate(dvs):
    width = (d + axy) * 1.1
    height = 2 * axy
    
    
    pattern_bulk = Pattern(width, height, pixel_res)
    ay_num = pattern_bulk.y_ax[-1] + pixel_res
    x_c = pattern_bulk.x_ax[-1] / 2
    y_c = pattern_bulk.y_ax[-1] / 2
    
    
    bulk_str = f"D ssh_1d_long_bulk_{dv_idx+1}, 123, {pattern_bulk.y_ax[-1] + pixel_res}, 1, {N-1}"
    bulk_str += "\nI 2\nC 200\n"
    for i in range(-1, 2):
        pattern_bulk.add_parametrized_shape(circle, x_c + axy / 2, i * ay_num + y_c - ay_num / 4 - dv * ay_num / 4, d / 2)
        pattern_bulk.add_parametrized_shape(circle, x_c - axy / 2, i * ay_num + y_c + ay_num / 4 + dv * ay_num / 4, d / 2)
    pattern_bulk.visualize()
    bulk_str += pattern_bulk.export_pattern(offsetx=1000,offsety=1000)
    bulk_str += "END\n\n\n"
    
    top_str = f"D ssh_1d_long_top_{dv_idx+1}"
    top_str += "\nI 2\nC 200\n"
    i = -1
    pattern_top = Pattern(width, height, pixel_res)
    pattern_top.add_parametrized_shape(circle, x_c + axy / 2, i * ay_num + y_c - ay_num / 4 - dv * ay_num / 4, d / 2)
    pattern_top.add_parametrized_shape(circle, x_c + axy / 2, 0 * ay_num + y_c - ay_num / 4 - dv * ay_num / 4, d / 2)
    pattern_top.add_parametrized_shape(circle, x_c - axy / 2, i * ay_num + y_c + ay_num / 4 + dv * ay_num / 4, d / 2)
    pattern_top.visualize()
    top_str += pattern_top.export_pattern(offsetx=1000,offsety=1000 + N * ay_num)
    top_str += "END\n\n\n"
    
    bot_str = f"D ssh_1d_long_bot_{dv_idx+1}"
    bot_str += "\nI 2\nC 200\n"
    i = 1
    pattern_bot = Pattern(width, height, pixel_res)
    pattern_bot.add_parametrized_shape(circle, x_c + axy / 2, i * ay_num + y_c - ay_num / 4 - dv * ay_num / 4, d / 2)
    pattern_bot.add_parametrized_shape(circle, x_c - axy / 2, i * ay_num + y_c + ay_num / 4 + dv * ay_num / 4, d / 2)
    pattern_bot.add_parametrized_shape(circle, x_c - axy / 2, 0 * ay_num + y_c + ay_num / 4 + dv * ay_num / 4, d / 2)
    pattern_bot.visualize()
    bot_str += pattern_bot.export_pattern(offsetx=1000,offsety=1000)
    bot_str += "END\n\n\n"
    
    str_ = str_ + bulk_str + top_str + bot_str
    
    # str_ += pattern.export_pattern(offsetx=offsets[0], offsety=offsets[1])
print(str_)


file = open("ssh_chains.pat", "w")
file.write(str_)
file.close()