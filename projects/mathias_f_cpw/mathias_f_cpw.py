from generate_pattern import Pattern, circle, ellipse
from math import pi
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt



im_frame = Image.open('CPW TEP.png')
np_frame = np.mean(np.array(im_frame), axis=2)

bool_arr = np_frame < np.mean(np_frame)
bool_arr = bool_arr.astype(np.int8)

px_pitch = 150



size = 1e4

# intitialize pattern object
pattern = Pattern(px_pitch*bool_arr.shape[0], px_pitch*bool_arr.shape[1], px_pitch)
pattern.pattern = bool_arr

# add a zero-radius dummy circle to trigger rectangulization
pattern.add_parametrized_shape(circle, 8e3, 18e3, 0)

# plot
pattern.visualize()

# generate .pat string
print(pattern.export_pattern(complete=True, export=True))
