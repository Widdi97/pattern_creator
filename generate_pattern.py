import numpy as np
import matplotlib.pyplot as plt
from rectangulize import rectangulize, rectangulize_oli, dtype, rectangulize_oli_horizontal_grouping
from raycasting import points_in_closed_curve
import numba as nb
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont

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

@nb.njit
def polygon(t, *args):
    if len(args) < 6:
        raise Exception("At least 3 knot points are requiered")
    if len(args)%2 == 1:
        raise Exception("Lengt of knot points incorrect")
    args = list(args)
    args = args + args[:2]
    return np.array([args[::2], args[1::2]])


class Pattern:
    def __init__(self, x_size, y_size, step_size, pattern_name="pattern_name", increment=1, dwell_time=100, algo="obj_lvl_interval"):
        if type(step_size) == float or type(step_size) == int:
            step_size = np.array([step_size, step_size])
        self.step_size = step_size
        
        if algo == "obj_lvl_interval":
            self.rectangulize_func = rectangulize_oli_horizontal_grouping
        elif algo == "descending_largest":
            self.rectangulize_func = rectangulize
        self.x_size = x_size
        self.y_size = y_size
        self.pattern_name = pattern_name
        self.increment = increment
        self.dwell_time = dwell_time
        self.pattern_header = self.generate_pattern_header()
        self.pat_shape = np.array([int(y_size / step_size[1]), int(x_size / step_size[0])])
        self.x_ax = step_size[0] * np.arange(self.pat_shape[1])
        self.y_ax = step_size[1] * np.arange(self.pat_shape[0])
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
        x1 = self.x_ax[rec_coords[0]] - self.step_size[0] / 2
        y1 = self.y_ax[rec_coords[1]] - self.step_size[1] / 2
        x2 = self.x_ax[rec_coords[2]] + self.step_size[0] / 2
        y2 = self.y_ax[rec_coords[3]] + self.step_size[1] / 2
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
        rects = self.rectangulize_func(self.pattern)
        
        # fig,ax = plt.subplots(dpi = 300)
        # ax.pcolormesh(np.arange(self.pattern.shape[1]),np.arange(self.pattern.shape[0]),self.pattern)
        
        # np.savetxt("ente.txt",self.pattern)
        
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
    def __init__(self, a1, a2, x_size, y_size, max_step_size, shapes_with_args=[], b_vecs=np.array([0, 0]),
                 pattern_name="pattern", increment=16, dwell_time=100, global_offsetx=0, global_offsety=0, visualize_patterns=False):
        self.a1 = a1
        self.a2 = a2
        
        # first unit vector parallel to a1
        self.e1 = a1 / np.dot(a1, a1)**0.5
        # second unit vector orthogonal to a1
        self.e2 = np.array([- self.e1[1], self.e1[0]])
        
        self.x_size = x_size
        self.y_size = y_size
        self.max_step_size = np.min(np.array([max_step_size, max_step_size]))
        
        self.shapes_with_args = shapes_with_args
        self.b_vecs = b_vecs
        
        self.increment = increment
        self.pattern_name = pattern_name
        self.dwell_time = dwell_time
        self.global_offsetx = global_offsetx
        self.global_offsety = global_offsety
        self.visualize_patterns = visualize_patterns
        
        
        self.find_x_y_aligned_unit_cell()
        self.plot_lattice_vecs()
        self.generate_unit_cells()
        self.generate_patterns()
        
    def find_x_y_aligned_unit_cell(self, max_steps=20, tolerance=1e-4):
        # search on x axis
        x_result_found = False
        for nx in range(1, max_steps):
            if self.a1[1] == 0:
                mx = - 1
                self.A_x = np.array([self.a1[0], 0])
                x_result_found = True
                break
            else:
                mx = - nx * self.a2[1] / self.a1[1]
                if abs(round(mx) - mx) < tolerance:
                    mx_r = round(mx)
                    self.A_x = np.array([- mx * self.a1[0] - nx * self.a2[0], 0])
                    # print(f"mx = {mx_r}, nx = {nx}")
                    x_result_found = True
                    break
        
        # search on y axis
        y_result_found = False
        for ny in range(1, max_steps):
            # if self.a2[0] == 0:
            #     my = - 1
            #     self.A_y = np.array([0, self.a2[1]])
            #     break
            # else:
            my = - ny * self.a2[0] / self.a1[0]
            if abs(round(my) - my) < tolerance:
                my_r = round(my)
                self.A_y = np.array([0, my * self.a1[1] + ny * self.a2[1]])
                # print(f"my = {my_r}, ny = {ny}")
                y_result_found = True
                break
        bulk_uc_found = not ((not x_result_found) or (not y_result_found))
        if not bulk_uc_found:
            raise Exception("lattice structure can't be reduced to a larger rectangular lattice 😢. Implement the structure using a single pattern.")
        else:
            self.m_xy = np.round(np.array([- mx, - my])).astype(int)
            self.n_xy = np.round(np.array([- nx, - ny])).astype(int)
            self.m_xy.sort()
            self.n_xy.sort()
            
    def check_ecp_array_compatability(self):
        return self.a1[1] == 0.0
        
    def find_x_y_UC_lattice_size(self):
        if not self.check_ecp_array_compatability():
            raise Exception("ECP periodicity function only supportet for a1 || x-axis 😢.")
        self.x_ruc_steps = self.x_size // self.A_x[0]
        self.y_ruc_steps = self.y_size // self.A_y[1]
        
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
        for ii in range(-100, 100):
            for jj in range(-100, 100):
                vec = ii * self.a1 + jj * self.a2
                xs = np.dot(vec, self.e1)
                ys = np.dot(vec, self.e2)
                if 0 <= xs and xs <= self.x_size and 0 <= ys and ys <= self.y_size:
                    lattice_vecs.append(vec)
                    plt.plot(*vec, marker="o", linestyle="", color="k")
        
        # plot larger rectangular UC vectors
        plt.plot([0, self.A_x[0]], [0, self.A_x[1]])
        plt.plot([0, self.A_y[0]], [0, self.A_y[1]])
        
        # plot all lattice points inside of the larger UC
        for ii in range(-100, 100):
            for jj in range(-100, 100):
                vec = ii * self.a1 + jj * self.a2
                if self.vec_in_bulk_uc(vec):
                    plt.plot(*vec, marker="o", linestyle="", color="b")
        
        
        plt.axis("equal")
        plt.show()
        
    def vec_in_bulk_uc(self, vec, offset=0):
        tol = max(self.A_x[0], self.A_y[1]) * 1e-7 + offset
        return (- tol <= vec[0] <= self.A_x[0] + tol) and (- tol <= vec[1] <= self.A_y[1] + tol)
        
    def generate_unit_cells(self):
        # calculate step sizes for x and y
        x_step_size = self.A_x[0] / np.ceil(self.A_x[0] / self.max_step_size)
        y_step_size = self.A_y[1] / np.ceil(self.A_y[1] / self.max_step_size)
        self.step_size = np.array([x_step_size, y_step_size])
        
        self.patterns = [[Pattern(self.A_x[0], self.A_y[1], self.step_size, pattern_name=self.pattern_name,
                                  increment=self.increment, dwell_time=self.dwell_time) for ii in range(3)] for jj in range(3)]
        
        
        for ii in range(-25, 25):
            for jj in range(-25, 25):
                for b_idx in range(len(self.shapes_with_args)):
                    vec = ii * self.a1 + jj * self.a2 + self.b_vecs[b_idx]
                    args = self.shapes_with_args[b_idx][1:]
                    
                    if self.vec_in_bulk_uc(vec, max(args[2:])):
                        for k in range(-1, 2):
                            for l in range(-1, 2):
                                uc_shift = self.A_x * k + self.A_y * l
                                #check if vec is inside of the rectangular UC
                                center = vec + uc_shift
                                shape, *args = self.shapes_with_args[b_idx]
                                def shape_shifted(t, delta_x, delta_y, *args):
                                    pts = np.array(shape(t, *args))
                                    pts[0] += delta_x
                                    pts[1] += delta_y
                                    return pts
                                self.patterns[1-k][1-l].add_parametrized_shape(shape_shifted, center[0] - self.step_size[0] / 2,
                                                                               center[1] - self.step_size[1] / 2,*args)
        for k in range(3):
            for l in range(3):
                self.patterns[k][l].rectangulize()
                if self.visualize_patterns:
                    self.patterns[k][l].visualize()

    def generate_patterns(self):
        pat_str = ""
        if self.check_ecp_array_compatability():
            self.find_x_y_UC_lattice_size()
        
        names = []
        for k in range(-1, 2):
            for l in range(-1, 2):
                if k == 0:
                    nx = self.x_ruc_steps
                else:
                    nx = 1
                if l == 0:
                    ny = self.y_ruc_steps
                else:
                    ny = 1
                name = self.pattern_name + f"_x_{-k}_y_{-l}"
                names.append(name)
                subpat_str = "D " + name
                # check, if pattern is not a corner and if so, add ecp periodicity
                is_corner = (abs(k) + abs(l) == 2)
                if not is_corner:
                    subpat_str += ", " + str(int(self.A_x[0])) + ", " + str(int(self.A_y[1]))
                    subpat_str += ", " + str(int(nx)) + ", " + str(int(ny))
                subpat_str += f"\nI {self.increment}\nC {self.dwell_time}\n"
                offsetx = - k * self.A_x[0] + self.A_x[0] + (k == -1) * self.A_x[0] * (self.x_ruc_steps - 1) + self.A_x[0]
                offsety = - l * self.A_y[1] + self.A_y[1] + (l == -1) * self.A_y[1] * (self.y_ruc_steps - 1) + is_corner * self.A_y[1] + self.A_y[1]
                subpat_str += self.patterns[1-k][1-l].export_pattern(complete=False, offsetx=round(offsetx+self.global_offsetx),
                                                                     offsety=round(offsety+self.global_offsety)) + "END\n\n\n"
                pat_str += subpat_str
        draw_latt_str = ""
        for name in names:
            draw_latt_str += f"draw({name})\n"
        self.pat_str = pat_str
        self.draw_latt_str = draw_latt_str
            
class Text:
    def __init__(self, step_size=150, fontsize=10000, font="arial.ttf", increment=1, dwell_time=100):
        self.font = font
        self.fontsize = fontsize # nm
        self.step_size = step_size
        self.img_steps = fontsize // step_size
        self.increment = increment
        self.dwell_time = dwell_time
        
    def generate_text_pattern(self, string):
        img_size_x = round(self.img_steps * 1.5) * len(string)
        img_size_y = round(self.img_steps * 1.5)
        image = Image.new('L', (img_size_x, img_size_y), color=255)  # 'L' mode for grayscale
        draw = ImageDraw.Draw(image)
        
        # Load the font with the specified font size
        font = ImageFont.truetype(self.font, size=self.img_steps)#ImageFont.load_default() if font_path is None else ImageFont.truetype(font_path, size=font_size)
        
        # Use textbbox to get the bounding box of the text
        bbox = draw.textbbox((0, 0), string, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        # Calculate position to center the text
        position = ((img_size_x - text_width) // 2, (img_size_y - text_height) // 2)
        
        # Draw the character on the image
        draw.text(position, string, font=font, fill=0)  # Fill with black (0)
        
        # Convert the image to a NumPy array and set True for black pixels (part of the character)
        bool_arr = np.array(image) < 128
        
        plt.matshow(bool_arr)
        
        # find borders
        
        
        return bool_arr
        
        

if __name__ == "__main__":
    #%% test pattern class
    
    pattern = Pattern(3e4, 2.5e4, np.array([300, 250]))
    pattern.add_parametrized_shape(circle, 8e3, 18e3, 3e3)
    pattern.add_parametrized_shape(ellipse, 8e3, 14e3, 0.15e4, 0.4e4, -40 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 5e3, 17e3, 0.1e4, 0.3e4, 90 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 17e3, 6e3, 1e3, 3e3, 0 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 14e3, 4e3, 1.2e3, 3e3, 90 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 22e3, 11e3, 2.2e3, 5e3, -50 / 180 * np.pi)
    pattern.add_parametrized_shape(ellipse, 1.5e4, 1.1e4, 0.4e4, 1e4, 90 / 180 * np.pi, boolean_operation="subtract")
    pattern.add_parametrized_shape(polygon,1.2e4, 1.17e4, 1.6e4, 1.27e4, 2.2e4, 1.64e4, 2.2e4, 2.1e4, 1.72e4,2.35e4)
    pattern.visualize()
    # print(pattern.export_pattern())
    
    #%% test lattice class
    # # weird lattice
    # a = 2000
    # a1_ = a * np.array([1, 0])
    # a2_ = a * np.array([1/4, 1])
    # x_size_ = 20 * a
    # y_size_ = 16 * a
    # lattice = Lattice(a1_, a2_, x_size_, y_size_, 0.08 * a, [[circle, 0, 0, 0.4 * a]])
    # print(lattice.pat_str)
    
    
    # # kagome 
    # a = 2000
    # a1_ = a * np.array([1, 0])
    # a2_ = a * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])
    
    # b1_ = np.array([0, 0])
    # b2_ = a1_ / 2
    # b3_ = a2_ / 2
    # bs = np.array([b1_, b2_, b3_])
    # x_size_ = 10 * a
    # y_size_ = 8 * a
    # lattice = Lattice(a1_, a2_, x_size_, y_size_, 0.08 * a, [[circle, 0, 0, 0.3 * a] for b in bs], bs)
    
    #%% test text
    
    # text = Text(font="arial.ttf")
    # text.generate_text_pattern("A2g")
    
    #%% generate right and up arrow
    
    # # right arrow
    # resolution = 0.25e3
    # w1 = 1e3
    # w2 = 3e3
    # size = 20e3
    # frac = 0.6
    
    
    # points = np.array([[size / 10, size / 2 - w1],
    #                     [size / 10, size / 2 + w1],
    #                     [size * frac, size / 2 + w1],
    #                     [size * frac, size / 2 + w2],
    #                     [9 * size / 10, size / 2],
    #                     [size * frac, size / 2 - w2],
    #                     [size * frac, size / 2 - w1]])
    # points[:,0] += resolution / 2
    # points[:,1] += resolution / 2
    
    
    # pattern_r = Pattern(size, size, resolution)
    # pattern_r.add_parametrized_shape(polygon, *points.flatten())
    # pattern_r.visualize()
    
    # pattern_u = Pattern(size, size, resolution)
    # pattern_u.add_parametrized_shape(polygon, *points[:,::-1].flatten())
    # pattern_u.visualize()