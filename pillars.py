from generate_pattern import Pattern, circle, ellipse
from math import pi


# pattern = Pattern(2.5e4, 1.8e4, 500)
# pattern.add_parametrized_shape(circle, 1e4, 0.6e4, 5e3)
# pattern.add_parametrized_shape(ellipse, 1.5e4, 1.1e4, 0.5e4, 
#                                0.8e4, 60 / 180 * pi)
# pattern.add_parametrized_shape(ellipse, 1.8e4, 2.7e3, 0.2e4, 
#                                0.4e4, -40 / 180 * pi)
# pattern.visualize()


def overlapping_pillars(radius, overlap, step_size):
    pattern = Pattern(5 * radius, 3 * radius, step_size)
    x0 = y0 = 1.5 * radius
    pattern.add_parametrized_shape(circle, x0, y0, radius)
    pattern.add_parametrized_shape(circle, x0 + 2 * radius - overlap, y0, radius)
    pattern.visualize()

    return pattern.export_pattern()