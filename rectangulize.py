import numpy as np
import matplotlib.pyplot as plt
# import cv2
import numba as nb

dtype = np.dtype('i1')

@nb.njit
def rectangle(pat_shape, p1i, p1j, p2i, p2j):
    rec = np.zeros(pat_shape, dtype=dtype)
    rec[p1j:p2j+1, p1i:p2i+1] = True
    return rec

@nb.njit(parallel=True)
def rectangle_area_matrix(pattern):
    #returns a 4d matrix with the areas of all rectangle corner combinations.
    #this is pure brute force. Allows for further smart optimizations.
    #axes of the output array are orderd like  x0, y0, x1, y1.
    ny, nx = pattern.shape
    result = np.zeros(shape=(nx, ny, nx, ny), dtype=nb.int32)
    for x1 in nb.prange(nx):
        for x0 in nb.prange(x1 + 1):
            for y1 in nb.prange(ny):
                for y0 in nb.prange(y1 + 1):
                    
                    chunk = pattern[y0:y1+1, x0:x1+1]
                    area = (1 + x1 - x0) * (1 + y1 - y0)
                    sum_ = np.sum(chunk)
                    if sum_ == area:
                        result[x0, y0, x1, y1] = area
    return result

@nb.njit
def update_rec_A_mat(rec_A_mat, idxs):
    #disallow all pairs of points which the resulting
    #rectangle would intersect the found rectangle.
    rec_A_mat[:idxs[2]+1, idxs[1]:idxs[3]+1, idxs[0]:, :] = 0 # x of point 1
    rec_A_mat[idxs[0]:idxs[2]+1, :idxs[3]+1, :, idxs[1]:] = 0 # y of point 1
    rec_A_mat[:idxs[2]+1, :, idxs[0]:, idxs[1]:idxs[3]+1] = 0 # x of point 2
    rec_A_mat[:, :idxs[3]+1, idxs[0]:idxs[2]+1, idxs[1]:] = 0 # y of point 2
    return rec_A_mat

def rectangulize(pattern, debug=False, plot=False):
    #calculates the rec_A_mat only once in the beginning and updates it using indexing.
    #Fast, but the index escalation is not completely understood.
    rectangles = []
    
    rec_A_mat = rectangle_area_matrix(pattern)
    while len(np.argwhere(pattern==1)) > 0:
        if debug: # check validity of updated rec_A_mat
            if not (rec_A_mat == rectangle_area_matrix(pattern)).all():
                raise Exception("Some error occured in the indexing updating of rec_A_mat (wrong code)!")
        idxs = np.unravel_index(rec_A_mat.argmax(), rec_A_mat.shape)
        rec = rectangle(pattern.shape, *idxs)
        
        if plot:
            plt.pcolor(x, y, pattern)
            plt.axis('equal')
            plt.title("pattern reduction")
            plt.colorbar()
            plt.show()
            
            plt.pcolor(x, y, rec)
            plt.colorbar()
            plt.axis('equal')
            plt.title("rec")
            plt.show()
            print(pattern.max())
        
        rec_A_mat = update_rec_A_mat(rec_A_mat, idxs)
        
        rectangles.append(idxs)
        pattern = pattern - rec
        
    
    if plot:
        plt.pcolor(x, y, pattern)
        plt.axis('equal')
        plt.title("pattern reduction")
        plt.show()
    return rectangles

def accurate_rectangulize(pattern):
    #calculates the rec_A_mat after every found rectangle. Slow but works 100%.
    rectangles = []
    while len(np.argwhere(pattern==1)) > 0:
        rec_A_mat = rectangle_area_matrix(pattern)
        max_rec_idxs = np.unravel_index(rec_A_mat.argmax(), rec_A_mat.shape)
        rec = rectangle(pattern.shape, *max_rec_idxs)
        rectangles.append(max_rec_idxs)
        pattern = pattern - rec
    return rectangles

if __name__ == "__main__":
    #steps
    nx = 71
    ny = 31
    
    x = np.arange(nx)
    y = np.arange(ny)
    
    
    def circle(pat_shape, i, j, r):
        x = np.arange(pat_shape[1])
        y = np.arange(pat_shape[0])
        X, Y = np.meshgrid(x, y)
        cir = np.sqrt((X - i)**2 + (Y - j)**2) < r
        return cir
    
    def ellipsis(pat_shape, i, j, ri, rj, phi):
        result = np.zeros(pat_shape, dtype=dtype)
        x = np.arange(pat_shape[1]) - i
        y = np.arange(pat_shape[0]) - j
        rot_mat = np.array([[np.cos(phi),  np.sin(phi)],
                            [-np.sin(phi), np.cos(phi)]])
        XY_grid = np.einsum("ij, jkl", rot_mat, np.meshgrid(x, y))
        result = result | (np.sqrt(XY_grid[0]**2 / ri**2 + XY_grid[1]**2 / rj**2) < 1)
        return result
    
    pattern = np.zeros((ny, nx), dtype=dtype)#np.sqrt((X - x0)**2 + (Y - y0)**2) < r
    
    #one circle and rectangle
    # pattern = pattern | circle(pattern.shape, 25, 25.1, 20)
    # pattern = rectangle(pattern.shape, 1, 1, 11, 10) | pattern
    
    #add 3 ellipses
    pattern = pattern | ellipsis(pattern.shape, 13, 12, 10, 15, 60 / 180*np.pi)
    pattern = pattern | ellipsis(pattern.shape, 35, 15, 10, 15, 0 / 180*np.pi)
    pattern = pattern | ellipsis(pattern.shape, 57, 12, 10, 15, -60 / 180*np.pi)
    
    #add circles
    # r = 14
    # pattern = pattern | circle(pattern.shape, 0, 0, r)
    # pattern = pattern | circle(pattern.shape, nx-1, 0, r)
    # pattern = pattern | circle(pattern.shape, 0, ny-1, r)
    # pattern = pattern | circle(pattern.shape, nx-1, ny-1, r)
    
    
    #random pattern
    # pattern = np.random.randint(0,10, size=(ny, nx), dtype=dtype) < 9
    
    
    #%% plot original
    
    plt.pcolor(x, y, pattern)
    plt.title("input")
    plt.axis('equal')
    plt.show()
    
    #%% cut borders of original
    # reduced_pattern, borders  = reduce_to_subspace(pattern)
    # plt.pcolor(x[borders[0,1]:borders[1,1]], y[borders[0,0]:borders[1,0]], reduced_pattern)
    # plt.title("reduced subspace")
    # plt.axis('equal')
    # plt.show()
    
    #%% separate individual patterns
    # split_patterns = split_pattern(pattern)
    
    # for idx, shape in enumerate(split_patterns):
    #     plt.pcolor(x, y, shape)
    #     plt.title(f"shape {idx+1}")
    #     plt.axis('equal')
    #     plt.show()
    
    #%% calculate area array
    # area_mat = rectangle_area_matrix(split_patterns[0])
    # max_idx = np.unravel_index(area_mat.argmax(), area_mat.shape)
    
    # #plot foudn rectangle
    # rec = rectangle(pattern.shape, *max_idx)
    
    # plt.pcolor(x, y, rec)
    # plt.title("largest fitting rectangle")
    # plt.axis('equal')
    # plt.show()
    
    #%% reduce pattern
    
    import matplotlib.patches as patches
    
    rectangles = rectangulize(pattern)
    
    
    fig, ax = plt.subplots()
    ax.pcolor(x, y, pattern,cmap="Greys")
    plt.axis('equal')
    colors = plt.cm.get_cmap("prism", len(rectangles))
    for idx, rec_coords in enumerate(rectangles):
        
        rect = patches.Rectangle([rec_coords[0] - 0.3, rec_coords[1] - 0.3], 
                                 rec_coords[2] - rec_coords[0] + 0.6, 
                                 rec_coords[3] - rec_coords[1] + 0.6, linewidth=3, 
                                 edgecolor=colors(idx), facecolor='none', hatch="/")
        ax.add_patch(rect)
        
        # rec = rectangle(pattern.shape, *rec_coords)
        # plt.pcolor(x, y, rec, alpha=0.5)
    plt.title("found rectangles")
    plt.show()
    
    #%% profile
    # %load_ext snakeviz
    # %snakeviz rectangulize(pattern)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    