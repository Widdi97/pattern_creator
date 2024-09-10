import numpy as np
import matplotlib.pyplot as plt
from rectangulize import rectangulize, dtype
from raycasting import points_in_closed_curve
import numba as nb
import matplotlib.patches as patches

# @nb.njit
def circle(t, x0, y0, r):
    x = r * np.cos(2 * np.pi * t +0.1) + x0
    y = r * np.sin(2 * np.pi * t +0.1) + y0
    return x, y

@nb.njit
def ellipse(t, x0, y0, ra, rb, phi):
    x = x0 + ra * np.cos(phi) * np.cos(2 * np.pi * t) - rb * np.sin(phi) * np.sin(2 * np.pi * t)
    y = y0 + ra * np.sin(phi) * np.cos(2 * np.pi * t) + rb * np.cos(phi) * np.sin(2 * np.pi * t)
    return x, y


# @nb.njit
def rectangle_point(t, x0, y0, x1, y1):
    if 0 <= t and t < 0.25:
        return x0 + (x1 - x0) * 4 * t, y0
    elif 0.25 <= t and t < 0.5:
        return x1, y0 + (y1 - y0) * 4 * (t - 0.25)
    elif 0.5 <= t and t < 0.75:
        return x1 - (x1 - x0) * 4 * (t - 0.5), y1
    elif 0.75 <= t and t <= 1:
        return x0, y1 - (y1 - y0)  * 4 * (t - 0.75)

# @nb.njit
def rectangle(t, x0, y0, x1, y1):
    if type(t) == float or type(t) == np.float64:
        # print(type(t), t)
        return rectangle_point(t, x0, y0, x1, y1)
    else:
        return [rectangle_point(t_, x0, y0, x1, y1) for t_ in t]

class Pattern:
    def __init__(self, x_size, y_size, step_size, pattern_name="pattern_name", increment=1, dwell_time=100):
        self.step_size = step_size
        self.x_size = x_size
        self.y_size = y_size
        self.pattern_name = pattern_name
        self.increment = increment
        self.dwell_time = dwell_time
        self.pattern_header = self.generate_pattern_header()
        self.pat_shape = np.array([int(y_size / step_size), int(x_size / step_size)])
        self.x_ax = step_size * np.arange(self.pat_shape[1])
        self.y_ax = step_size * np.arange(self.pat_shape[0])
        self.XY_meshgrid = np.meshgrid(self.x_ax, self.y_ax)
        self.pattern = np.zeros(shape=self.pat_shape, dtype=dtype)
        self.shapes = []
        self.rects = []
        self.rects_updated = True
        self.pat_file_string = ""
        self.pat_file_string_updated = True
        
    def visualize(self, rectangulize=True):
        if not self.rects_updated and rectangulize:
            self.rectangulize()
        fig, ax = plt.subplots()
        ax.pcolor(self.x_ax, self.y_ax, self.pattern, cmap="Greys", vmin=-0.3, vmax=1.5)
        
        #plot rectangles
        colors = plt.cm.get_cmap("prism", len(self.rects))
        for idx, rec_coords in enumerate(self.rects):
            rect = patches.Rectangle([rec_coords[0], rec_coords[1]], rec_coords[2] - rec_coords[0], rec_coords[3] - rec_coords[1], linewidth=1, 
                                      edgecolor=colors(idx), facecolor="None", alpha=0.5, hatch="xxx")
            ax.add_patch(rect)
        
        #plot shapes
        for parametrization, args in self.shapes:
            plt.plot(*parametrization(np.linspace(0, 1, 100), *args), color="k")
        
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axis('equal')
        fig.tight_layout()
        plt.savefig("plot.png", dpi=1000)
        plt.show()
        
    def translate_coords(self, rec_coords):
        x1 = self.x_ax[rec_coords[0]] - self.step_size / 2
        y1 = self.y_ax[rec_coords[1]] - self.step_size / 2
        x2 = self.x_ax[rec_coords[2]] + self.step_size / 2
        y2 = self.y_ax[rec_coords[3]] + self.step_size / 2
        return np.array([x1, y1, x2, y2])
        
    def add_parametrized_shape(self, parametrization, *args, boolean_operation="add"):
        self.shapes.append([parametrization, args])
        res = []
        parametrization_ = lambda t: parametrization(t, *args)
        for y in self.y_ax:
            res.append(points_in_closed_curve(self.x_ax, y, parametrization_))
        res = np.array(res, dtype=bool)
        allowed_types = ["add", "subtract"]
        if boolean_operation not in allowed_types:
            raise Exception(f"Boolean operation {boolean_operation} not allowed. only {allowed_types} are valid.")
        if boolean_operation == "add":
            self.pattern = self.pattern | res
        elif boolean_operation == "subtract":
            self.pattern = self.pattern & ~res
        self.rects_updated = False
        self.pat_file_string_updated = False
        
    def rectangulize(self):
        rects = rectangulize(self.pattern)
        translated_rects = []
        for rect in rects:
            translated_rects.append(self.translate_coords(rect))
        self.rects = translated_rects
        self.rects_updated = True
        
    def export_pattern(self, complete=False, export=False, offsetx=0, offsety=0):
        if not self.rects_updated:
            self.rectangulize()
        if not self.pat_file_string_updated:
            pat_string = ""
            for rect in self.rects:
                rounded_rect = np.round(rect).astype(int)
                rounded_rect[0] += offsetx
                rounded_rect[1] += offsety
                rounded_rect[2] += offsetx
                rounded_rect[3] += offsety
                pat_string += "RECT " + str(rounded_rect[0]) + ", " + str(rounded_rect[1]) + ", " + str(rounded_rect[2]) + ", " + str(rounded_rect[3]) + "\n"
            # if complete:
            #     pat_string = self.pattern_header + pat_string + "\nEND"
            self.pat_string = pat_string
        if complete:
            result = self.pattern_header + self.pat_string + "END"
        else:
            result = self.pat_string
        if export:
            with open(self.pattern_name + '.txt', 'w') as f:
                f.write(result)
        return result
    
    def generate_pattern_header(self):
        header = ""
        header += "D " + self.pattern_name + "\n"
        header += "I " + str(int(self.increment)) + "\n"
        header += "C " + str(int(self.dwell_time)) + "\n"
        return header

class Lattice:
    def __init__(self, a1, a2, x_size, y_size, shapes_with_args=[], b_vecs=[]):
        self.a1 = a1
        self.a2 = a2
        
        # first unit vector parallel to a1
        self.e1 = a1 / np.dot(a1, a1)**0.5
        # second unit vector orthogonal to a1
        self.e2 = np.array([- self.e1[1], self.e1[0]])
        
        self.x_size = x_size
        self.y_size = y_size
        
        self.plot_lattice_vecs()
        self.find_x_y_aligned_unit_cell()
        
    def find_x_y_aligned_unit_cell(self, max_steps=20, tolerance=0.01):
        for n in range(max_steps, - (max_steps + 1), -1):
            if n != 0:
                m = - n * self.a2[1] / self.a1[1]
                if m%1 < tolerance:
                    print("found solution in y:", m, n)
                print(m, m%1)
        
    
    def plot_lattice_vecs(self):
        #plot maximum allowed lattice vector box
        plt.plot([0, (self.x_size * self.e1)[0]], [0, (self.x_size * self.e1)[1]], linestyle=":", color="grey")
        plt.plot([(self.x_size * self.e1)[0], (self.x_size * self.e1 + self.y_size * self.e2)[0]],
                  [(self.x_size * self.e1)[1], (self.x_size * self.e1 + self.y_size * self.e2)[1]], linestyle=":", color="grey")
        plt.plot([(self.x_size * self.e1 + self.y_size * self.e2)[0], (self.y_size * self.e2)[0]],
                  [(self.x_size * self.e1 + self.y_size * self.e2)[1], (self.y_size * self.e2)[1]], linestyle=":", color="grey")
        plt.plot([(self.y_size * self.e2)[0], 0], [(self.y_size * self.e2)[1], 0], linestyle=":", color="grey")
        
        # plot unit vectors
        plt.plot([0, self.e1[0]], [0, self.e1[1]], color="r")
        plt.plot([0, self.e2[0]], [0, self.e2[1]], color="r")
        
        
        lattice_vecs = []
        # iterate x direction (parallel to a1)
        for ii in range(-10, 10):
            for jj in range(-10, 10):
                vec = ii * self.a1 + jj * self.a2
                xs = np.dot(vec, self.e1)
                ys = np.dot(vec, self.e2)
                if 0 <= xs and xs <= self.x_size and 0 <= ys and ys <= self.y_size:
                    lattice_vecs.append(vec)
                    plt.plot([0, vec[0]], [0, vec[1]], marker="o", linestyle="", color="k")
        
        
        plt.axis("equal")
        plt.show()
        

if __name__ == "__main__":
    #%% test pattern class
    
    pattern = Pattern(3e4, 2.5e4, 250)
    pattern.add_parametrized_shape(circle, 8e3, 18e3, 3e3)
    pattern.add_parametrized_shape(ellipse, 8e3, 14e3, 0.15e4, 0.4e4, -40 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 5e3, 17e3, 0.1e4, 0.3e4, 90 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 17e3, 6e3, 1e3, 3e3, 0 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 14e3, 4e3, 1.2e3, 3e3, 90 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 22e3, 11e3, 2.2e3, 5e3, -50 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 1.5e4, 1.1e4, 0.4e4, 1e4, 90 / 180 * np.pi, boolean_operation="subtract")
    # pattern.add_parametrized_shape(rectangle, 1e4, 0.5e3, 1.7e4, 2e3)
    pattern.visualize()
    print(pattern.export_pattern())
    
    #%% test lattice class
    # a1_ = np.array([1, 1e-9])
    # a2_ = np.array([0.25, 1.234])
    # x_size_ = 5
    # y_size_ = 4
    # lattice = Lattice(a1_, a2_, x_size_, y_size_)