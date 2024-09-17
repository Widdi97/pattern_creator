import numpy as np
import matplotlib.pyplot as plt
from generate_pattern import circle

# def trace_circle_right(y, x0, y0, r, R):
#     t = np.arccos((y - y0) / r) / (2 * np.pi)
#     return circle(t-0.25, x0, y0, R)

def trace_line_x(x0, y0, x1, y1, Y):
    m = (y1 - y0) / (x1 - x0)
    t = y1 - m * x1
    X = (Y - t) / m
    return X, Y

def trace_line_y(x0, y0, x1, y1, X):
    m = (y1 - y0) / (x1 - x0)
    t = y1 - m * x1
    Y = m * X + t
    return X, Y
    

def trace_circle_right(Y, x0, y0, r, R):
    phi = np.arcsin((Y - y0) / R)
    X = x0 + R * np.cos(phi)
    return X, Y

def trace_circle_left(Y, x0, y0, r, R):
    phi = np.arcsin((Y - y0) / R)
    X = x0 - R * np.cos(phi)
    return X, Y

def trace_circle_top(X, x0, y0, r, R):
    phi = np.arcsin((X - x0) / R)
    Y = y0 + R * np.cos(phi)
    return X, Y

def trace_circle_bottom(X, x0, y0, r, R):
    phi = np.arcsin((X - x0) / R)
    Y = y0 - R * np.cos(phi)
    return X, Y

def generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4):
    X1 = round(X1)
    Y1 = round(Y1)
    Y2 = round(Y2)
    Y3 = round(Y3)
    X2 = round(X2)
    Y4 = round(Y4)
    return "YPOLY " + str(X1) + ", " + str(Y1) + ", " + str(Y2) + ", " + str(Y3) + ", " + str(X2) + ", " + str(Y4)

def generate_xpoly_string(X1, Y1, X2, X3, X4, Y2):
    X1 = round(X1)
    Y1 = round(Y1)
    X2 = round(X2)
    X3 = round(X3)
    X4 = round(X4)
    Y2 = round(Y2)
    return "XPOLY " + str(X1) + ", " + str(Y1) + ", " + str(X2) + ", " + str(X3) + ", " + str(X4) + ", " + str(Y2)

def generate_ring_right(x0, y0, r, R, resolution=30, plot=False):
    string = ""
    right = np.linspace(-0.125, 0.125, resolution)
    
    
    R_corner_top = circle(right[-1], x0, y0, R)
    R_corner_bot = circle(right[0], x0, y0, R)
    r_points = np.array(circle(right, x0, y0, r))
    
    # trace inner points onto outer circle
    R_pts_traced = trace_circle_right(r_points[1], x0, y0, r, R)
    
    # turn bulk into XPOLYs: XPOLY X1, Y1, X2, X3, X4, Y2
    for ii in range(len(r_points[0]) - 1):
        X1 = r_points[0][ii]
        Y1 = r_points[1][ii]
        X2 = R_pts_traced[0][ii]
        X3 = R_pts_traced[0][ii+1]
        X4 = r_points[0][ii+1]
        Y2 = r_points[1][ii+1]
        string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
    #generate corner triangles
    # increment = r_points[1][0] - R_corner_bot[1]
    increment = r_points[1][1] - r_points[1][0]
    
    #generate additional y points in the upper and lower triangle
    y_pts_bot_tri = np.arange(r_points[1][0], R_corner_bot[1], - increment)[::-1]
    y_pts_top_tri = np.arange(r_points[1][-1], R_corner_top[1], increment)
    
    # trace additional y points onto outer circle
    R_pts_traced_bot_tri = trace_circle_right(y_pts_bot_tri, x0, y0, r, R)
    R_pts_traced_top_tri = trace_circle_right(y_pts_top_tri, x0, y0, r, R)
    
    # trace additional y points onto linear slope
    line_pts_traced_bot_tri = trace_line_x(*r_points[:,0], *R_corner_bot, y_pts_bot_tri)
    line_pts_traced_top_tri = trace_line_x(*r_points[:,-1], *R_corner_top, y_pts_top_tri)
    
    # append upper triangle points to string
    for ii in range(len(y_pts_top_tri) - 1):
        X1 = line_pts_traced_top_tri[0][ii]
        Y1 = line_pts_traced_top_tri[1][ii]
        X2 = R_pts_traced_top_tri[0][ii]
        X3 = R_pts_traced_top_tri[0][ii+1]
        X4 = line_pts_traced_top_tri[0][ii+1]
        Y2 = line_pts_traced_top_tri[1][ii+1]
        string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
    # append top triangle of triangle
    X1 = line_pts_traced_top_tri[0][-1]
    Y1 = line_pts_traced_top_tri[1][-1]
    X2 = R_pts_traced_top_tri[0][-1]
    X3 = R_corner_top[0]
    X4 = R_corner_top[0]
    Y2 = R_corner_top[1]
    string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
        
    # append lower triangle points to string
    for ii in range(len(y_pts_bot_tri) - 1):
        X1 = line_pts_traced_bot_tri[0][ii]
        Y1 = line_pts_traced_bot_tri[1][ii]
        X2 = R_pts_traced_bot_tri[0][ii]
        X3 = R_pts_traced_bot_tri[0][ii+1]
        X4 = line_pts_traced_bot_tri[0][ii+1]
        Y2 = line_pts_traced_bot_tri[1][ii+1]
        string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
    # append bottom triangle of triangle
    X1 = R_corner_bot[0]
    Y1 = R_corner_bot[1]
    X2 = R_corner_bot[0]
    X3 = R_pts_traced_bot_tri[0][0]
    X4 = line_pts_traced_bot_tri[0][0]
    Y2 = line_pts_traced_bot_tri[1][0]
    string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
    if plot:
        # plt.plot(*circle(np.linspace(-0.125, 0.125, 1000), x0, y0, R))
        plt.plot(*r_points, marker="x", linestyle="")
        plt.plot(*R_pts_traced, marker="x", linestyle="")
        plt.plot(*R_corner_top, marker="x", linestyle="")
        plt.plot(*R_corner_bot, marker="x", linestyle="")
        
        plt.plot(*R_pts_traced_top_tri, marker="x", linestyle="")
        plt.plot(*R_pts_traced_bot_tri, marker="x", linestyle="")
        
        plt.plot(*line_pts_traced_top_tri, marker="x", linestyle="")
        plt.plot(*line_pts_traced_bot_tri, marker="x", linestyle="")
        
        plt.axis("equal")
        plt.show()
    return string

def generate_ring_left(x0, y0, r, R, resolution=30, plot=False):
    string = ""
    left = np.linspace(0.625, 0.375, resolution)
    
    
    R_corner_top = circle(left[-1], x0, y0, R)
    R_corner_bot = circle(left[0], x0, y0, R)
    r_points = np.array(circle(left, x0, y0, r))
    
    # trace inner points onto outer circle
    R_pts_traced = trace_circle_left(r_points[1], x0, y0, r, R)
    
    # turn bulk into XPOLYs: XPOLY X1, Y1, X2, X3, X4, Y2
    for ii in range(len(r_points[0]) - 1):
        X1 = R_pts_traced[0][ii]
        Y1 = R_pts_traced[1][ii]
        X2 = r_points[0][ii]
        X3 = r_points[0][ii+1]
        X4 = R_pts_traced[0][ii+1]
        Y2 = R_pts_traced[1][ii+1]
        string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
    #generate corner triangles
    increment = r_points[1][1] - r_points[1][0]
    
    #generate additional y points in the upper and lower triangle
    y_pts_bot_tri = np.arange(r_points[1][0], R_corner_bot[1], - increment)[::-1]
    y_pts_top_tri = np.arange(r_points[1][-1], R_corner_top[1], increment)
    
    # trace additional y points onto outer circle
    R_pts_traced_bot_tri = trace_circle_left(y_pts_bot_tri, x0, y0, r, R)
    R_pts_traced_top_tri = trace_circle_left(y_pts_top_tri, x0, y0, r, R)
    
    # trace additional y points onto linear slope
    line_pts_traced_bot_tri = trace_line_x(*r_points[:,0], *R_corner_bot, y_pts_bot_tri)
    line_pts_traced_top_tri = trace_line_x(*r_points[:,-1], *R_corner_top, y_pts_top_tri)
    
    # append upper triangle points to string
    for ii in range(len(y_pts_top_tri) - 1):
        X1 = R_pts_traced_top_tri[0][ii]
        Y1 = line_pts_traced_top_tri[1][ii]
        X2 = line_pts_traced_top_tri[0][ii]
        X3 = line_pts_traced_top_tri[0][ii+1]
        X4 = R_pts_traced_top_tri[0][ii+1]
        Y2 = line_pts_traced_top_tri[1][ii+1]
        string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
    # append top triangle of triangle
    X1 = R_pts_traced_top_tri[0][-1]
    Y1 = R_pts_traced_top_tri[1][-1]
    X2 = line_pts_traced_top_tri[0][-1]
    X3 = R_corner_top[0]
    X4 = R_corner_top[0]
    Y2 = R_corner_top[1]
    string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
        
    # append lower triangle points to string
    for ii in range(len(y_pts_bot_tri) - 1):
        X1 = R_pts_traced_bot_tri[0][ii]
        Y1 = line_pts_traced_bot_tri[1][ii]
        X2 = line_pts_traced_bot_tri[0][ii]
        X3 = line_pts_traced_bot_tri[0][ii+1]
        X4 = R_pts_traced_bot_tri[0][ii+1]
        Y2 = line_pts_traced_bot_tri[1][ii+1]
        string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
    # append bottom triangle of triangle
    X1 = R_corner_bot[0]
    Y1 = R_corner_bot[1]
    X2 = R_corner_bot[0]
    X3 = line_pts_traced_bot_tri[0][0]
    X4 = R_pts_traced_bot_tri[0][0]
    Y2 = line_pts_traced_bot_tri[1][0]
    string += generate_xpoly_string(X1, Y1, X2, X3, X4, Y2) + "\n"
    
    if plot:
        # plt.plot(*circle(np.linspace(-0.125, 0.125, 1000), x0, y0, R))
        plt.plot(*r_points, marker="x", linestyle="")
        plt.plot(*R_pts_traced, marker="x", linestyle="")
        plt.plot(*R_corner_top, marker="x", linestyle="")
        plt.plot(*R_corner_bot, marker="x", linestyle="")
        
        plt.plot(*R_pts_traced_top_tri, marker="x", linestyle="")
        plt.plot(*R_pts_traced_bot_tri, marker="x", linestyle="")
        
        plt.plot(*line_pts_traced_top_tri, marker="x", linestyle="")
        plt.plot(*line_pts_traced_bot_tri, marker="x", linestyle="")
        
        plt.axis("equal")
        plt.show()
    return string

def generate_ring_top(x0, y0, r, R, resolution=30, plot=False):
    string = ""
    top = np.linspace(0.375, 0.125, resolution)
    
    
    R_corner_rig = circle(top[-1], x0, y0, R)
    R_corner_lef = circle(top[0], x0, y0, R)
    r_points = np.array(circle(top, x0, y0, r))
    
    # trace inner points onto outer circle
    R_pts_traced = trace_circle_top(r_points[0], x0, y0, r, R)
    
    # turn bulk into YPOLYs: YPOLY X1, Y1, Y2, Y3, X2, Y4
    for ii in range(len(r_points[0]) - 1):
        X1 = R_pts_traced[0][ii]
        Y1 = r_points[1][ii]
        Y2 = R_pts_traced[1][ii]
        Y3 = R_pts_traced[1][ii+1]
        X2 = r_points[0][ii+1]
        Y4 = r_points[1][ii+1]
        string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
    # generate corner triangles
    increment = r_points[0][1] - r_points[0][0]
    
    #generate additional y points in the upper and lower triangle
    x_pts_lef_tri = np.arange(r_points[0][0], R_corner_lef[0], - increment)[::-1]
    x_pts_rig_tri = np.arange(r_points[0][-1], R_corner_rig[0], increment)
    
    # trace additional y points onto outer circle
    R_pts_traced_lef_tri = trace_circle_top(x_pts_lef_tri, x0, y0, r, R)
    R_pts_traced_rig_tri = trace_circle_top(x_pts_rig_tri, x0, y0, r, R)
    
    # trace additional y points onto linear slope
    line_pts_traced_rig_tri = trace_line_y(*r_points[:,-1], *R_corner_rig, x_pts_rig_tri)
    line_pts_traced_lef_tri = trace_line_y(*r_points[:,0], *R_corner_lef, x_pts_lef_tri)
    
    # append left triangle points to string
    for ii in range(len(x_pts_lef_tri) - 1):
        X1 = R_pts_traced_lef_tri[0][ii]
        Y1 = line_pts_traced_lef_tri[1][ii]
        Y2 = R_pts_traced_lef_tri[1][ii]
        Y3 = R_pts_traced_lef_tri[1][ii+1]
        X2 = line_pts_traced_lef_tri[0][ii+1]
        Y4 = line_pts_traced_lef_tri[1][ii+1]
        string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
    # append left triangle of triangle
    X1 = R_corner_lef[0]
    Y1 = R_corner_lef[1]
    Y2 = R_corner_lef[1]
    Y3 = R_pts_traced_lef_tri[1][0]
    X2 = line_pts_traced_lef_tri[0][0]
    Y4 = line_pts_traced_lef_tri[1][0]
    string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
        
    # append right triangle points to string
    for ii in range(len(x_pts_lef_tri) - 1):
        X1 = R_pts_traced_rig_tri[0][ii]
        Y1 = line_pts_traced_rig_tri[1][ii]
        Y2 = R_pts_traced_rig_tri[1][ii]
        Y3 = R_pts_traced_rig_tri[1][ii+1]
        X2 = line_pts_traced_rig_tri[0][ii+1]
        Y4 = line_pts_traced_rig_tri[1][ii+1]
        string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
    # append right triangle of triangle
    X1 = line_pts_traced_rig_tri[0][-1]
    Y1 = line_pts_traced_rig_tri[1][-1]
    Y2 = R_pts_traced_rig_tri[1][-1]
    Y3 = R_corner_rig[1]
    X2 = R_corner_rig[0]
    Y4 = R_corner_rig[1]
    string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
    if plot:
        # plt.plot(*circle(np.linspace(-0.125, 0.125, 1000), x0, y0, R))
        plt.plot(*r_points, marker="x", linestyle="")
        plt.plot(*R_pts_traced, marker="x", linestyle="")
        plt.plot(*R_corner_rig, marker="x", linestyle="")
        plt.plot(*R_corner_lef, marker="x", linestyle="")
        
        plt.plot(*R_pts_traced_lef_tri, marker="x", linestyle="")
        plt.plot(*R_pts_traced_rig_tri, marker="x", linestyle="")
        
        plt.plot(*line_pts_traced_rig_tri, marker="x", linestyle="")
        plt.plot(*line_pts_traced_lef_tri, marker="x", linestyle="")
        
        plt.axis("equal")
        plt.show()
    return string

def generate_ring_bottom(x0, y0, r, R, resolution=30, plot=False):
    string = ""
    bottom = np.linspace(-0.375, -0.125, resolution)
    
    
    R_corner_rig = circle(bottom[-1], x0, y0, R)
    R_corner_lef = circle(bottom[0], x0, y0, R)
    r_points = np.array(circle(bottom, x0, y0, r))
    
    # # trace inner points onto outer circle
    R_pts_traced = trace_circle_bottom(r_points[0], x0, y0, r, R)
    
    # turn bulk into YPOLYs: YPOLY X1, Y1, Y2, Y3, X2, Y4
    for ii in range(len(r_points[0]) - 1):
        X1 = R_pts_traced[0][ii]
        Y1 = R_pts_traced[1][ii]
        Y2 = r_points[1][ii]
        Y3 = r_points[1][ii+1]
        X2 = R_pts_traced[0][ii+1]
        Y4 = R_pts_traced[1][ii+1]
        string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
    # generate corner triangles
    increment = r_points[0][1] - r_points[0][0]
    
    #generate additional y points in the upper and lower triangle
    x_pts_lef_tri = np.arange(r_points[0][0], R_corner_lef[0], - increment)[::-1]
    x_pts_rig_tri = np.arange(r_points[0][-1], R_corner_rig[0], increment)
    
    # trace additional y points onto outer circle
    R_pts_traced_lef_tri = trace_circle_bottom(x_pts_lef_tri, x0, y0, r, R)
    R_pts_traced_rig_tri = trace_circle_bottom(x_pts_rig_tri, x0, y0, r, R)
    
    # trace additional y points onto linear slope
    line_pts_traced_rig_tri = trace_line_y(*r_points[:,-1], *R_corner_rig, x_pts_rig_tri)
    line_pts_traced_lef_tri = trace_line_y(*r_points[:,0], *R_corner_lef, x_pts_lef_tri)
    
    # append left triangle points to string
    for ii in range(len(x_pts_lef_tri) - 1):
        X1 = R_pts_traced_lef_tri[0][ii]
        Y1 = R_pts_traced_lef_tri[1][ii]
        Y2 = line_pts_traced_lef_tri[1][ii]
        Y3 = line_pts_traced_lef_tri[1][ii+1]
        X2 = line_pts_traced_lef_tri[0][ii+1]
        Y4 = R_pts_traced_lef_tri[1][ii+1]
        string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
    # append left triangle of triangle
    X1 = R_corner_lef[0]
    Y1 = R_corner_lef[1]
    Y2 = R_corner_lef[1]
    Y3 = line_pts_traced_lef_tri[1][0]
    X2 = line_pts_traced_lef_tri[0][0]
    Y4 = R_pts_traced_lef_tri[1][0]
    string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
        
    # append right triangle points to string
    for ii in range(len(x_pts_lef_tri) - 1):
        X1 = R_pts_traced_rig_tri[0][ii]
        Y1 = R_pts_traced_rig_tri[1][ii]
        Y2 = line_pts_traced_rig_tri[1][ii]
        Y3 = line_pts_traced_rig_tri[1][ii+1]
        X2 = line_pts_traced_rig_tri[0][ii+1]
        Y4 = R_pts_traced_rig_tri[1][ii+1]
        string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
    # append right triangle of triangle
    X1 = line_pts_traced_rig_tri[0][-1]
    Y1 = R_pts_traced_rig_tri[1][-1]
    Y2 = line_pts_traced_rig_tri[1][-1]
    Y3 = R_corner_rig[1]
    X2 = R_corner_rig[0]
    Y4 = R_corner_rig[1]
    string += generate_ypoly_string(X1, Y1, Y2, Y3, X2, Y4) + "\n"
    
    if plot:
        # plt.plot(*circle(np.linspace(-0.125, 0.125, 1000), x0, y0, R))
        plt.plot(*r_points, marker="x", linestyle="")
        plt.plot(*R_pts_traced, marker="x", linestyle="")
        plt.plot(*R_corner_rig, marker="x", linestyle="")
        plt.plot(*R_corner_lef, marker="x", linestyle="")
        
        plt.plot(*R_pts_traced_lef_tri, marker="x", linestyle="")
        plt.plot(*R_pts_traced_rig_tri, marker="x", linestyle="")
        
        plt.plot(*line_pts_traced_rig_tri, marker="x", linestyle="")
        plt.plot(*line_pts_traced_lef_tri, marker="x", linestyle="")
        
        plt.axis("equal")
        plt.show()
    return string

def generate_ring(x0, y0, r, R, resolution=30, plot=False):
    ring_r = generate_ring_right(x0, y0, r, R, resolution, plot)
    ring_l = generate_ring_left(x0, y0, r, R, resolution, plot)
    ring_t = generate_ring_top(x0, y0, r, R, resolution, plot)
    ring_b = generate_ring_bottom(x0, y0, r, R, resolution, plot)
    return ring_r + ring_t + ring_l + ring_b

def generate_header_footer(name, increment, dwell_time):
    header = f"D {name}\nI {str(increment)}\nC {dwell_time}\n"
    footer = "END\n\n"
    return header, footer
    
def generate_ring_ecp_wrapper(x0, y0, r, R, name, increment, dwell_time, resolution=30, plot=False):
    header, footer = generate_header_footer(name, increment, dwell_time)
    string = generate_ring(x0, y0, r, R, resolution=30, plot=plot)
    return header + string + footer
    

if __name__ == "__main__":
    ring_r = generate_ring_right(1234, 3210, 4321, 4876)
    # ring_l = generate_ring_left(1234, 3210, 4321, 4876)
    # ring_t = generate_ring_top(1234, 3210, 4321, 4876)
    # ring_b = generate_ring_bottom(1234, 3210, 4321, 4876)
    # print(ring_r+ring_t+ring_l+ring_b)
    
    # ring = generate_ring(1234, 3210, 4321, 4876, plot=True)
    # print(ring)
    
    # diameters = np.array([20, 40, 60, 80]) * 1000 # nm
    # positions = np.array([[ 20, 0], [90, 90], [80, 20], [ 0, 70]]) * 1e3
    diameters = np.array([10, 20, 30, 40, 50, 60, 70, 80]) * 1000 # nm
    positions = np.array([[ 5, 0], [ 35, 5], [ 75, 10], [ 125, 15], [ 185, 20], 
                          [ 180, 105], [ 100, 100], [ 10, 95]]) * 1.1e3
    
    
    
    wg_widths = [650, 800, 950] # nm
    offset = np.array([40, 10]) * 1e3
    tAx = np.linspace(0, 1, 500)
    
    string = ""
    for w in wg_widths:
        header, footer = generate_header_footer(f"rings_W{w}nm", 16, 122)
        pattern = header
        
        for idx, D in enumerate(diameters):
            x0, y0 = positions[idx] + offset
            plt.plot(*circle(tAx, x0, y0, D/2), color="k")
            plt.plot(*circle(tAx, x0, y0, D/2 - w), color="k")
            plt.axis("equal")
            
            name = "D" + str(D // 1000) + "um__w" + str(w) + "nm"
            ring = generate_ring(x0, y0, D/2 - w, D/2, resolution=4*int(5*D/10000))
            pattern += ring
        plt.show()
        pattern += footer
        # print(pattern)
        string += pattern
        # break
    with open("ring_patterns.txt", "w") as f:
        f.write(string)
        f.close()