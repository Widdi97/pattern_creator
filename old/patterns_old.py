import numpy as np
import matplotlib.pyplot as plt
import cv2
import numba as nb
from scipy.optimize import dual_annealing, basinhopping

dtype=np.dtype('u1')

@nb.njit#(parallel=True) parallel only used with prange
def rectangle(pat_shape, p1i, p1j, p2i, p2j):
    rec = np.zeros(pat_shape, dtype=dtype)
    # rec = rec.astype(bool)
    rec[p1j:p2j+1, p1i:p2i+1] = True
    return rec

def circle(pat_shape, i, j, r):
    # cir = np.zeros(pat_shape, dtype=bool)
    x = np.arange(pat_shape[1])
    y = np.arange(pat_shape[0])
    
    X, Y = np.meshgrid(x, y)
    cir = np.sqrt((X - i)**2 + (Y - j)**2) < r
    return cir
    
def split_pattern(pattern):
    result = []
    reduced_pattern = pattern
    seeds = np.argwhere(reduced_pattern==True)
    while len(seeds) > 0:
        filled = cv2.floodFill(reduced_pattern.astype(dtype), None, seeds[0][::-1], 0)[1]
        result.append(reduced_pattern & ~ filled)
        reduced_pattern = filled
        seeds = np.argwhere(reduced_pattern==True)
    return result

# @nb.njit
def reduce_to_subspace(pattern):
    args = np.argwhere(pattern==1)
    mn = np.min(args, axis=0)
    mx = np.max(args, axis=0) + 1
    return pattern[mn[0]:mx[0],mn[1]:mx[1]], np.array([mn, mx])

# # @nb.njit
# def allowed_rectangle_area(pattern, x0, y0, x1, y1):
#     # reduce amount of allowed rectangles by factor of 4
#     if x1 < x0 or y1 < y0:
#         return np.nan
#     rect = rectangle(pattern.shape, x0, y0, x1, y1)
    
#     # plt.matshow(rect)
#     # plt.title(x0, y0, x1, y1)
#     # plt.show()
    
#     #check if all pixels of the rectangle are inside of the shape
#     is_rect_and_not_shape = rect & ~ pattern
#     if np.all(is_rect_and_not_shape == False):
#         #calculate area
#         a = np.sum(rect)
#         # print(a)
#         return a#(x1 - x0 + 1) * (y1 - y0 + 1)
#     else:
#         return np.nan

def rectangle_area_matrix(pattern):
    #returns a 4d matrix with the areas of all rectangle corner combinations.
    #this is pure brute force. Allows for further smart optimizations.
    #axes of the output array are orderd like  x0, y0, x1, y1.
    
    ny, nx = pattern.shape
    result = np.zeros(shape=(nx, ny, nx, ny), dtype=int)
    for x1 in range(nx):
        for x0 in range(x1 + 1):
            for y1 in range(ny):
                for y0 in range(y1 + 1):
                    
                    chunk = pattern[y0:y1+1, x0:x1+1]
                    
                    area = (1 + x1 - x0) * (1 + y1 - y0)
                    sum_ = np.sum(chunk)
                    if x0 == x1 and y0 == y1:
                        print(area)
                    if sum_ == area:
                        result[x0, y0, x1, y1] = area
    return result

# # @nb.njit
# def fit_largest_rectangle(pattern):
#     args = np.argwhere(pattern==True)
#     #find two random starting points inside of the shape
#     p0 = args[np.random.randint(0, len(args))]
#     # bounds = np.array([[0,0], pattern.shape])
#     pshape = pattern.shape
#     bounds = np.array([[0,0,0,0],[pshape[0]-1,pshape[1]-1,pshape[0]-1,pshape[1]-1]])
    
#     rec0_args = p0[1], p0[0], p0[1], p0[0]
    
#     #fit
#     fun = lambda args: - allowed_rectangle_area(pattern, *args)
#     res = dual_annealing(fun, bounds.T, x0=rec0_args, maxiter=1000)
    
#     found_rect_params = res.x
#     res_rec = rectangle(pattern.shape, *found_rect_params)
#     print(rec0_args, bounds)
    
#     #visualize
#     rec0 = rectangle(pattern.shape, *rec0_args)
#     plt.matshow(pattern)
#     plt.axhline(p0[0])
#     plt.axvline(p0[1])
#     plt.show()
    
#     plt.matshow(rec0)
#     plt.axhline(p0[0])
#     plt.axvline(p0[1])
#     plt.show()
    
#     plt.matshow(res_rec)
#     plt.show()
#     # print(bounds)
#     print(res)
#     print("rectangle area of result:", allowed_rectangle_area(pattern, *found_rect_params))
    
#     reduced_pattern = pattern & ~ res_rec
#     return found_rect_params, reduced_pattern

# def fully_reduce_patterns(pattern_list):
#     res = []
#     for pattern in pattern_list:
#         res.append(split_pattern(pattern))
#     if len(res) > len(pattern_list):
#         return split_patterns(res)
#     else:
#         return res

# def rectangulize(input_pattern):
#     rectangles = []
#     splited_patterns = split_pattern(input_pattern)
#     new_splited_patterns = []
#     for splited_pattern in splited_patterns:
        
#         reduced_splited_pattern, mn, mx = reduce_to_subspace(splited_pattern)
#         found_rect_params, reduced_pattern = fit_largest_rectangle(reduced_splited_pattern)
#         rectangles.append(found_rect_params)
#         new_splited_patterns.append(split_pattern(reduced_pattern))


#steps
nx = 15
ny = 14

x = np.arange(nx)
y = np.arange(ny)


pattern = np.zeros((ny, nx), dtype=dtype)#np.sqrt((X - x0)**2 + (Y - y0)**2) < r

#add circle
# pattern = pattern | circle(pattern.shape, 5, 7, 5)

pattern = rectangle(pattern.shape, 11, 5, 11, 5) | pattern


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
split_patterns = split_pattern(pattern)

# for idx, shape in enumerate(split_patterns):
#     plt.pcolor(x, y, shape)
#     plt.title(f"shape {idx+1}")
#     plt.axis('equal')
#     plt.show()

#%% calculate area array
area_mat = rectangle_area_matrix(split_patterns[0])
max_idx = np.unravel_index(area_mat.argmax(), area_mat.shape)

#plot foudn rectangle
rec = rectangle(pattern.shape, *max_idx)

plt.pcolor(x, y, rec)
plt.title("largest fitting rectangle")
plt.axis('equal')
plt.show()


#%% fit rectangle
# found_rect_params, reduced_pattern = fit_largest_rectangle(split_patterns[0])
# rec = rectangle(pattern.shape, *found_rect_params)

# plt.matshow(reduced_pattern)
# plt.show()

# plt.matshow(rec)
# plt.show()

#%% reduce pattern
# res = fully_reduce_patterns([pattern])

# params = 2, 14, 5, 17
# rec = rectangle(*params)
# plt.matshow(rec)
# plt.show()
# print(allowed_rectangle_area(split_patterns[1], *params))

#%% fit all
# rectangulize(pattern)











































