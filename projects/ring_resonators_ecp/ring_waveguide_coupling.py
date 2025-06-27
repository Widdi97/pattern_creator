from ring_resonators_ecp import generate_ring_right, generate_ring_left, generate_ring_top, generate_ring_bottom, generate_ring
from generate_pattern import circle
import numpy as np
import matplotlib.pyplot as plt

resolution=50

# ring parameters
x0 = 100000 # nm
y0 = 100000

r_c = 10000 # center radius
width = 900

r = r_c - width // 2
R = r_c + width // 2


# wg parameters
h = - 4000# height offset from the center of the ring


ring_r = generate_ring_right(x0, y0, r, R, resolution=resolution)
ring_l = generate_ring_left(x0, y0, r, R, resolution=resolution)
# ring_t = generate_ring_top(x0, y0, r, R, resolution=resolution)
ring_b = generate_ring_bottom(x0, y0, r, R, resolution=resolution, plot=True)
print(ring_r+ring_l+ring_b)

# print(generate_ring(x0, y0, r, R, resolution=resolution))

tax = np.linspace(0, 1, 100)

plt.plot(*circle(tax, x0, y0, r), c="k")
plt.plot(*circle(tax, x0, y0, R), c="k")
plt.axis("equal")
plt.show()