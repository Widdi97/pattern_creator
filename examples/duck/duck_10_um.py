from generate_pattern import Pattern, circle, ellipse
from math import pi

# intitialize pattern object
pattern = Pattern(3e4, 2.5e4, 500)


# add a circle
pattern.add_parametrized_shape(circle, 8e3, 18e3, 3e3)

# add some ellipses
pattern.add_parametrized_shape(ellipse, 1.5e4, 1.1e4, 0.4e4, 1e4, 90 / 180 * pi)
pattern.add_parametrized_shape(ellipse, 8e3, 14e3, 0.15e4, 0.4e4, -40 / 180 * pi)
pattern.add_parametrized_shape(ellipse, 5e3, 17e3, 0.1e4, 0.3e4, 90 / 180 * pi)
pattern.add_parametrized_shape(ellipse, 17e3, 6e3, 1e3, 3e3, 0 / 180 * pi)
pattern.add_parametrized_shape(ellipse, 14e3, 4e3, 1.2e3, 3e3, 90 / 180 * pi)
pattern.add_parametrized_shape(ellipse, 22e3, 11e3, 2.2e3, 5e3, -50 / 180 * pi)

# plot
pattern.visualize()

# generate .pat string
print(pattern.export_pattern())
