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

def generate_nbr(index, num, scaling=1, custom_offset=[0, 0]):
    res = f"D nbr_{index}\nI 16\nC 100\n"
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

start_nbr = 1
start_x = -20000
start_y = 65000 + 85000
x_abstand = 120000  # Abstand zwischen den Spalten
y_abstand = 112000  # Abstand zwischen den Zeilen
spalten = 4

all_nbrs = ""
for index, jj in enumerate(range(start_nbr,18)):
    x_offset = start_x + x_abstand * ((index-1)%spalten)
    y_offset = start_y + y_abstand * ((index-1)//spalten)
    string = generate_nbr(index, jj-1, scaling=0.45,custom_offset=[x_offset,y_offset])
    print(string)
    all_nbrs += string + "\n\n"
    with open(f"numbers_honey_{start_nbr}.pat", "w") as f:
        f.write(all_nbrs)
