

def generate_skips(max_r, array_steps, a_field):
    skips = ""
    for jj in range(array_steps[1]):
        y_pos = jj * a_field[1]
        if abs(y_pos) >= max_r:
            x_max = 0
        else:
            x_max = (max_r**2 - y_pos**2)**0.5
        max_idx = int(x_max / a_field[0])
        if max_idx <= array_steps[0]:
            if max_idx == array_steps[0]:
                skips += f"   SKIP ({max_idx},{jj+1})\n"
            else:
                skips += f"   SKIP ({max_idx}-{array_steps[0]},{jj+1})\n"
        # print(jj, max_idx, y_pos, x_max)
        # max_x = np.sqrt(max_r**2 - y_pos**2)
    return skips

if __name__ == "__main__":
    
    #%% top right
    array_steps = [40, 50]
    a_field = [680, 530] # um
    
    max_r = 30e3 # um
    
    skip_str = generate_skips(max_r, array_steps, a_field)
    print(skip_str)
