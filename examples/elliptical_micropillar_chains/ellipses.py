from generate_pattern import Pattern, circle, ellipse
from shape_intersections import find_intersections
from math import pi
import numpy as np
import matplotlib.pyplot as plt


resolution = 50

lattice_const = 4350 # um
center_line = 1500
ellipticity = 0.48


r1 = 1000
r2 = r1 * (1 - ellipticity)

#%% fit offset

def calc_overlap_difference(lattice_const, center_line, resolution, o, r1, r2, visualize=False):
    
    # ellipses at the border of the unit cell
    args_intercell_1 = [ (-1 + 0.5) * lattice_const + o - resolution / 2, 1.1 * center_line, r1, r2, 150 / 180 * pi]
    args_intercell_2 = [ ( 0 + 0.5) * lattice_const - o - resolution / 2, 1.1 * center_line, r1, r2, 30 / 180 * pi]
    if visualize:
        pattern = Pattern(lattice_const, 2.2 * center_line, resolution)
        pattern.add_parametrized_shape(ellipse, *args_intercell_1)
        pattern.add_parametrized_shape(ellipse, *args_intercell_2)
        pattern.visualize()
    
    # ellipses inside the unit cell
    args_intracell_1 = [ (0.5) * lattice_const - resolution / 2, 1.1 * center_line, r1, r2, 90 / 180 * pi]
    args_intracell_2 = [ ( 0 + 0.5) * lattice_const - o - resolution / 2, 1.1 * center_line, r1, r2, 30 / 180 * pi]
    if visualize:
        pattern = Pattern(lattice_const, 2.2 * center_line, resolution)
        pattern.add_parametrized_shape(ellipse, *args_intracell_1)
        pattern.add_parametrized_shape(ellipse, *args_intracell_2)
        pattern.visualize()
    
    intersections_intercell = find_intersections(ellipse, args_intercell_1, ellipse, args_intercell_2)
    intersections_intracell = find_intersections(ellipse, args_intracell_1, ellipse, args_intracell_2)
    
    distance_intercell = ((intersections_intercell[0][0] - intersections_intercell[1][0])**2 + (intersections_intercell[0][1] - intersections_intercell[1][1])**2)**0.5
    distance_intracell = ((intersections_intracell[0][0] - intersections_intracell[1][0])**2 + (intersections_intracell[0][1] - intersections_intracell[1][1])**2)**0.5
    # print(distance_intercell, distance_intracell)
    overlap_difference = distance_intercell - distance_intracell
    # print(overlap_difference)
    return distance_intercell, distance_intracell#overlap_difference

offset_ax = np.linspace(1250, 1400, 3)
# overlap_difference = [calc_overlap_difference(lattice_const, center_line, resolution, o_, r1, r2, False) for o_ in offset_ax]
o1o2 = np.array([calc_overlap_difference(lattice_const, center_line, resolution, o_, r1, r2, True) for o_ in offset_ax]).T

plt.plot(offset_ax, o1o2[0] - o1o2[1], color="b", marker="x", linestyle="")
plt.xlabel("pillar offset")
plt.xlabel("overlap difference")
plt.axhline(0, color="k")
plt.show()



o = 1280

#%% plot nicely for talk
fig, ax = plt.subplots()
ax.plot(np.array(offset_ax)*1e-3, o1o2[1]*1e-3, color="r", label="$o_1$")
ax.plot(np.array(offset_ax)*1e-3, o1o2[0]*1e-3, color="b", label="$o_2$")
ax.set_xlabel("Pillar offset $\\Delta x$ [$\\mathrm{\\mu m}$]")
ax.set_ylabel("Overlap [$\\mathrm{\\mu m}$]")
plt.axhline(0, color="k")
plt.axvline(o*1e-3, color="g")
ax.minorticks_on()
ax.xaxis.set_ticks_position("both")
ax.yaxis.set_ticks_position("both")
ax.tick_params(which='major', width=1.00,length=4,direction="in")
ax.tick_params(which='minor', width=0.75,length=2,direction="in")
ax.legend()
fig.tight_layout()
plt.savefig("overlap_optimization.png", dpi=300)
plt.show()


#%% center unit cell
pattern = Pattern(lattice_const, 2.2 * center_line, resolution, pattern_name = "center", increment=2, dwell_time=200)


for i in range(-1, 2):
    # e2
    pattern.add_parametrized_shape(ellipse, (i + 0.5) * lattice_const - resolution / 2, 1.1 * center_line, r1, r2, 90 / 180 * pi)
    # e1
    pattern.add_parametrized_shape(ellipse, (i + 0.5) * lattice_const - o - resolution / 2, 1.1 * center_line, r1, r2, 30 / 180 * pi)
    # e3
    pattern.add_parametrized_shape(ellipse, (i + 0.5) * lattice_const + o - resolution / 2, 1.1 * center_line, r1, r2, 150 / 180 * pi)

pattern.visualize()
string = pattern.export_pattern(complete=True, export=True)
print(string)

#%% left unit cell

# pattern_l = Pattern(lattice_const, 2.2 * center_line, resolution, pattern_name = "left", increment=2, dwell_time=200)

# i = 1
# # e1
# pattern_l.add_parametrized_shape(ellipse, (i + 0.5) * lattice_const - o - resolution / 2, 1.1 * center_line, r1, r2, 30 / 180 * pi)
# # e2
# pattern_l.add_parametrized_shape(ellipse, (i + 0.5) * lattice_const - resolution / 2, 1.1 * center_line, r1, r2, 90 / 180 * pi)
# # e3
# pattern_l.add_parametrized_shape(ellipse, (i + 0.5) * lattice_const + o - resolution / 2, 1.1 * center_line, r1, r2, 150 / 180 * pi)

# pattern_l.visualize()
# string_l = pattern_l.export_pattern(complete=True, export=True)
# print(string_l)

#%% right unit cell

# pattern_r = Pattern(lattice_const, 2.2 * center_line, resolution, pattern_name = "right", increment=2, dwell_time=200)

# i = -1
# # e1
# pattern_r.add_parametrized_shape(ellipse, (i + 0.5) * lattice_const - o - resolution / 2, 1.1 * center_line, r1, r2, 30 / 180 * pi)
# # e2
# pattern_r.add_parametrized_shape(ellipse, (i + 0.5) * lattice_const - resolution / 2, 1.1 * center_line, r1, r2, 90 / 180 * pi)
# # e3
# pattern_r.add_parametrized_shape(ellipse, (i + 0.5) * lattice_const + o - resolution / 2, 1.1 * center_line, r1, r2, 150 / 180 * pi)

# pattern_r.visualize()
# string_r = pattern_r.export_pattern(complete=True, export=True)
# print(string)