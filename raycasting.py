import numpy as np
import numba as nb
# import matplotlib.pyplot as plt

# @nb.njit
def points_in_closed_curve(x, y, curve, num_samples=100):
    # Initialize the count of intersections
    is_inside = np.zeros(x.shape)#, dtype=nb.u1
    
    # Create a range of t values from 0 to 1
    t_values = np.linspace(0, 1, num_samples)
    xy_pts = np.array(curve(t_values)).T
    
    # Iterate through each t value
    for ii in range(1, len(xy_pts)):
        x1, y1 = xy_pts[ii-1]
        x2, y2 = xy_pts[ii]

        # Check if the ray from (x, y) intersects the curve segment (x1, y1) to (x2, y2)
        # Check if y is between y1 and y2
        if (y1 > y) != (y2 > y):
            # Check if (x, y) is on the right side of the line that connects (x1, y1) and (x2, y2) (ray cast to the left)
            # project the point (x, y) onto the curve segment in x direction
            x_intersect = (x1 * y - x1 * y2 - x2 * y + x2 * y1) / (y1 - y2)
            # plt.plot([x1, x2], [y1, y2], marker="x")
            # plt.plot(*curve(t_values))
            # plt.plot(x, y, marker="x")
            # plt.plot(x_intersect, y, marker="x")
            # plt.show()
            isbigger = x >= x_intersect
            # print(isbigger)
            # if x >= x_intersect:
            # is_inside = is_inside * (1 - isbigger) + (1 - is_inside) * isbigger
            is_inside = is_inside + isbigger - 2 * isbigger * is_inside
    return is_inside

@nb.njit(cache=True)
def _parity_rows(x, ys, xy_pts):
    # Same crossing test and intersection formula as points_in_closed_curve, for all rows at once.
    out = np.zeros((ys.size, x.size), dtype=np.bool_)
    y_min = xy_pts[:, 1].min()
    y_max = xy_pts[:, 1].max()
    for r in range(ys.size):
        y = ys[r]
        if y < y_min or y > y_max:  # no segment can be crossed: row stays outside
            continue
        for ii in range(1, xy_pts.shape[0]):
            x1, y1 = xy_pts[ii - 1, 0], xy_pts[ii - 1, 1]
            x2, y2 = xy_pts[ii, 0], xy_pts[ii, 1]
            if (y1 > y) != (y2 > y):
                x_intersect = (x1 * y - x1 * y2 - x2 * y + x2 * y1) / (y1 - y2)
                for c in range(x.size):
                    if x[c] >= x_intersect:
                        out[r, c] = not out[r, c]
    return out


def points_in_closed_curve_rows(x, ys, curve, num_samples=100):
    """Boolean mask[len(ys), len(x)]; identical to stacking points_in_closed_curve(x, y, curve)
    for every y in ys (cast to bool), but evaluated in one numba kernel."""
    t_values = np.linspace(0, 1, num_samples)
    xy_pts = np.ascontiguousarray(np.array(curve(t_values), dtype=np.float64).T)
    return _parity_rows(np.asarray(x, dtype=np.float64), np.asarray(ys, dtype=np.float64), xy_pts)


if __name__ == "__main__":
    @nb.njit
    def example_curve(t):
        x = np.cos(2 * np.pi * t)
        y = np.sin(2 * np.pi * t)
        return x, y
    
    def profile(n=1000):
        for i in range(n):
            points_in_closed_curve(np.random.uniform(-1,1,100), 0.5, example_curve)
    
    # Test the function with a point
    x_test, y_test = np.array([0.2, 0.3, 0.9]), 0.5
    is_inside = points_in_closed_curve(x_test, y_test, example_curve)
    print(f"The point ({x_test}, {y_test}) is inside the curve: {is_inside}")
    
    
    # x_test, y_test = 0.5, 0.9
    # is_inside = points_in_closed_curve(x_test, y_test, example_curve)
    # print(f"The point ({x_test}, {y_test}) is inside the curve: {is_inside}")
    
    # x_test, y_test = 0.0, 0.99
    # is_inside = points_in_closed_curve(x_test, y_test, example_curve)
    # print(f"The point ({x_test}, {y_test}) is inside the curve: {is_inside}")
        
    #%% profile
    # %load_ext snakeviz
    # %snakeviz profile(10000)