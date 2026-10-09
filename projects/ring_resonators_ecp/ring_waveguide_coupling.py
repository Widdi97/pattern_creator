from ring_resonators_ecp import generate_ring_right, generate_ring_left, generate_ring_top, generate_ring_bottom, generate_ring, circle
import numpy as np
import matplotlib.pyplot as plt


resolution=20


def gauss(x, x0, sigma):
    return np.exp(- (x - x0)**2 / sigma**2)


# ring parameters
x0 = 250000 # all space units are in nm
y0 = 250000

r_c = 10000 # center radius
width = 900

r = r_c - width // 2
R = r_c + width // 2


# wg parameters
h = - 5000 # height offset from the center of the ring
a = 0.27
wg_width = 900

# taper that is positioned on the left side of the structure
taper_start_offset = 50000
taper_length = 30000
sigma_slim = 5000
slim_factor = 0.4

def wg_center_line(x, x0, y0, h):
    # x=0 defines the ring
    return 0 * x + y0 + h

def ring_taylor_expansion_N2(x, x0, y0, r_c):
    x_r = x - x0
    
    return y0 - r_c + 1 / 2 * x_r**2 / r_c

def waveguide(x, x0, y0, r_c, h, a):
    return (ring_taylor_expansion_N2(x, x0, y0, r_c) + y0 + h) / 2 - 1 / 2 * np.sqrt((ring_taylor_expansion_N2(x, x0, y0, r_c) - y0 - h)**2 + a * r_c**2)

def waveguide_slope(x, x0, y0, r_c, h, a, dx=10):
    return (waveguide(x + dx / 2, x0, y0, r_c, h, a) - waveguide(x - dx / 2, x0, y0, r_c, h, a)) / (2 * dx)

def waveguide_width_muliplier(x, x0, taper_start_offset, taper_length):
    result = []
    for x_ in x:
        x_r = x_ - x0
        if x_r < -taper_start_offset:
            result.append(0.0)
        elif x_r < - taper_start_offset + taper_length:
            result.append((x_r + taper_start_offset) / taper_length)
        else:
            result.append(1.0)
    return np.array(result)

def waveguide_width(x, x0, y0, r_c, h, a):
    slope_adjusted = wg_width * np.sqrt(1 + waveguide_slope(x, x0, y0, r_c, h, a)**2)
    tapered = slope_adjusted * waveguide_width_muliplier(x, x0, taper_start_offset, taper_length)
    slimmed = tapered * (1 - slim_factor * gauss(x, x0, sigma_slim))
    return slimmed

def waveguide_upper_line(x, x0, y0, r_c, h, a):
    return waveguide(x, x0, y0, r_c, h, a) + waveguide_width(x, x0, y0, r_c, h, a) / 2
    
def waveguide_lower_line(x, x0, y0, r_c, h, a):
    return waveguide(x, x0, y0, r_c, h, a) - waveguide_width(x, x0, y0, r_c, h, a) / 2

# ring_r = generate_ring_right(x0, y0, r, R, resolution=resolution)
# ring_l = generate_ring_left(x0, y0, r, R, resolution=resolution)
# ring_t = generate_ring_top(x0, y0, r, R, resolution=resolution)
# ring_b = generate_ring_bottom(x0, y0, r, R, resolution=resolution, plot=True)
# print(ring_r+ring_l+ring_b+ring_t)




print(generate_ring(x0, y0, r, R, resolution=resolution))

tax = np.linspace(0, 1, 100)

xAx_wg = np.linspace(x0 - taper_start_offset, x0 + 4 * r_c, 100)
xAx_ring_taylor = np.linspace(x0 - 1.5 * r_c, x0 + 1.5 * r_c, 100)


# plt.plot(xAx_wg, wg_center_line(xAx_wg, x0, y0, h), c="b")
# plt.plot(xAx_wg, waveguide(xAx_wg, x0, y0, r_c, h, a), c="g", linestyle=":")
plt.plot(xAx_wg, waveguide_upper_line(xAx_wg, x0, y0, r_c, h, a), c="g", linestyle="-")
plt.plot(xAx_wg, waveguide_lower_line(xAx_wg, x0, y0, r_c, h, a), c="g", linestyle="-")
# plt.plot(xAx_ring_taylor, ring_taylor_expansion_N2(xAx_ring_taylor, x0, y0, r_c), c="r")
plt.plot(*circle(tax, x0, y0, r), c="k")
plt.plot(*circle(tax, x0, y0, R), c="k")
plt.axis("equal")
plt.show()


# plt.plot(xAx_wg, waveguide_slope(xAx_wg, x0, y0, r_c, h, a, dx=10))
# plt.show()

# plt.plot(xAx_wg, waveguide_width(xAx_wg, x0, y0, r_c, h, a))
# plt.show()

# plt.plot(xAx_wg, waveguide_width_muliplier(xAx_wg, x0, taper_start_offset, taper_length))
# plt.show()



#%% convert waveguide to trapezoids

xAx_wg_ecp = np.round(xAx_wg).astype(int)

wg_string = ""


for ii in range(len(xAx_wg_ecp) - 1):
    _x1 = int(xAx_wg_ecp[ii])
    _x2 = int(xAx_wg_ecp[ii+1])
    
    _y1 = int(np.round(waveguide_lower_line(np.array([_x1]), x0, y0, r_c, h, a)[0]))
    _y2 = int(np.round(waveguide_upper_line(np.array([_x1]), x0, y0, r_c, h, a)[0]))
    _y3 = int(np.round(waveguide_upper_line(np.array([_x2]), x0, y0, r_c, h, a)[0]))
    _y4 = int(np.round(waveguide_lower_line(np.array([_x2]), x0, y0, r_c, h, a)[0]))
    
    wg_string += f"YPOLY {_x1}, {_y1}, {_y2}, {_y3}, {_x2}, {_y4}\n"
    
    
print(wg_string)