import numpy as np

with open("individual_numbers.txt", "r") as f:
    numbers = f.read()
    # print(numbers)
    
split = numbers.split("\n\n")

dct = {}
for idx, s in enumerate(split):
    rectangles = s[19:-3]
    lines = rectangles.split("\n")[:-1]
    nbrs_arr = []
    for line in lines:
        line_nbrs = [int(n_) for n_ in line[2:].split(", ")]
        nbrs_arr.append(line_nbrs) # rectangle with (x1, y1, x2, y2)
    nbrs_arr = np.array(nbrs_arr)
    dct[idx] = nbrs_arr

def generate_nbr(num, scaling=1, custom_offset=[0, 0], name_addition=""):
    res = f"D nbr{name_addition}_{num}\nI 16\nC 122\n"
    dx_vec = np.array([0, 1, 0, 1, 0]) * - 18000 * scaling
    for offset, char in enumerate(str(num)[::-1]):
        char_lines = dct[int(char)].copy()
        for line in char_lines:
            line = line * scaling
            line += dx_vec * offset + np.array([0, 1, 0, 1, 0]) * 18000
            line = np.round(line).astype(int)
            line[1] += custom_offset[0]
            line[3] += custom_offset[0]
            line[2] += custom_offset[1]
            line[4] += custom_offset[1]
            res += "P "
            for _ in range(5):
                res += str(line[_]) +", "
            res = res[:-2] + "\n"
    res += "END"
    return res

all_nbrs = ""
for jj in range(99):
    string = generate_nbr(jj)
    # print(string)
    all_nbrs += string + "\n\n"
    with open("numbers.pat", "w") as f:
        f.write(all_nbrs)

all_nbrs = ""
for jj in range(99):
    string = generate_nbr(jj, custom_offset=[0, 35000], name_addition="_x")
    # print(string)
    all_nbrs += string + "\n\n"
    
    string = generate_nbr(jj, name_addition="_y")
    # print(string)
    all_nbrs += string + "\n\n"
    with open("numbers_xy.pat", "w") as f:
        f.write(all_nbrs)

# smaller numbers
for jj in [650, 800, 950]:
    print(generate_nbr(jj, 0.5, np.array([100, 55])*1000))