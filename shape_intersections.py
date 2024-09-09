from generate_pattern import circle, ellipse
import numpy as np
import matplotlib.pyplot as plt
import numba as nb

@nb.njit
def line_line_intersection_point(g_1, g_2, h_1, h_2):
    g_dir = g_2 - g_1
    h_dir = h_2 - h_1
    
    # check if lines are parallel
    det = g_dir[0] * h_dir[1] - g_dir[1] * h_dir[0]
    if np.isclose(det, 0):
        return None
    
    # check if intersection is inside of the lines (0<=mu<=1 and 0<=nu<=1)
    mu = - g_1[0]*g_2[1] + g_1[0]*h_1[1] + g_1[1]*g_2[0] - g_1[1]*h_1[0] - g_2[0]*h_1[1] + g_2[1]*h_1[0]
    if not np.isclose(mu, 0): # mitigate (some) divisions by zero
        divisor = (g_1[0]*h_1[1] - g_1[0]*h_2[1] - g_1[1]*h_1[0] + g_1[1]*h_2[0] - g_2[0]*h_1[1] + g_2[0]*h_2[1] + g_2[1]*h_1[0] - g_2[1]*h_2[0])
        mu = mu / divisor
    
    nu = g_1[0] + h_1[0]*mu - h_1[0] - h_2[0]*mu
    if not np.isclose(nu, 0):
        divisor = g_1[0] - g_2[0]
        nu = nu / divisor
        
    if mu < 0 or nu < 0 or mu > 1 or nu > 1:
        return None

    intersection_point = [h_1[0] + mu*(-h_1[0] + h_2[0]), h_1[1] + mu*(-h_1[1] + h_2[1])]
    # intersection_point = [(g_1[0]*g_2[1]*h_1[0] - g_1[0]*g_2[1]*h_2[0] - g_1[0]*h_1[0]*h_2[1] + g_1[0]*h_1[1]*h_2[0] - g_1[1]*g_2[0]*h_1[0] + g_1[1]*g_2[0]*h_2[0] + g_2[0]*h_1[0]*h_2[1] - g_2[0]*h_1[1]*h_2[0])/(g_1[0]*h_1[1] - g_1[0]*h_2[1] - g_1[1]*h_1[0] + g_1[1]*h_2[0] - g_2[0]*h_1[1] + g_2[0]*h_2[1] + g_2[1]*h_1[0] - g_2[1]*h_2[0]), 
    #                       (g_1[0]*g_2[1]*h_1[1] - g_1[0]*g_2[1]*h_2[1] - g_1[1]*g_2[0]*h_1[1] + g_1[1]*g_2[0]*h_2[1] - g_1[1]*h_1[0]*h_2[1] + g_1[1]*h_1[1]*h_2[0] + g_2[1]*h_1[0]*h_2[1] - g_2[1]*h_1[1]*h_2[0])/(g_1[0]*h_1[1] - g_1[0]*h_2[1] - g_1[1]*h_1[0] + g_1[1]*h_2[0] - g_2[0]*h_1[1] + g_2[0]*h_2[1] + g_2[1]*h_1[0] - g_2[1]*h_2[0])]
    return intersection_point


def find_intersections(shape_1, args_1, shape_2, args_2, n=100):
    intersection_points = []
    
    ts = np.linspace(0, 1, n)
    points_shape_1 = [np.array(shape_1(t, *args_1)) for t in ts]
    points_shape_2 = [np.array(shape_2(t, *args_2)) for t in ts]
    
    for ii in range(n - 1):
        p1 = points_shape_1[ii]
        p1_plus_1 = points_shape_1[ii+1]
        for jj in range(n - 1):
            p2 = points_shape_2[jj]
            p2_plus_1 = points_shape_2[jj+1]
            inter = line_line_intersection_point(p1, p1_plus_1, p2, p2_plus_1)
            if inter:
                intersection_points.append(inter)
    return intersection_points

if __name__ == "__main__":
    # one line intersection
    g_1 = np.array([0, 0])
    g_2 = np.array([1, 3])
    h_1 = np.array([0.5, -1])
    h_2 = np.array([0.5, 3])
    
    
    ip = line_line_intersection_point(g_1, g_2, h_1, h_2)
    
    plt.plot(*np.array([g_1, g_2]).T, marker="x")
    plt.plot(*np.array([h_1, h_2]).T, marker="x")
    plt.plot(*ip, marker="o")
    plt.show()
    
    # all shape intersections
    args_1 = [0, 0, 2]
    args_2 = [1, 1, 2]
    
    
    n = 100
    intersection_points = find_intersections(circle, args_1, circle, args_2, n=n)
    
    #plot
    t_ax = np.linspace(0, 1, n)
    
    fig, ax = plt.subplots()
    ax.plot(*np.array([circle(t, *args_1) for t in t_ax]).T)
    ax.plot(*np.array([circle(t, *args_2) for t in t_ax]).T)
    ax.set_aspect("equal")
    for ip in intersection_points:
        ax.plot(*ip, marker="o")
    