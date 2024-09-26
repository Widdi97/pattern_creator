# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 10:04:41 2024

@author: chm66em
"""
from generate_pattern import Pattern, circle, Lattice
import numpy as np
import matplotlib.pyplot as plt

increment = 16
dwell_time = 100

            
pat_str = ""
cntrl_str = ""
            

#%% Adiabatic honey comb constant overlap

x_fix_offset = 6000 
y_fix_offset = 70000
y_offset = 125000
x_offset = 125000
y_size = 12
x_size = 25

overlaps_init = [1.2, 1.1, 1.0, 0.9]

dsmall = [1800]

dlarg = [2600, 3000]
 
for yindex, v_init in enumerate(overlaps_init):
    xindex = 0
    for d_max in dlarg:
        for d_init in dsmall: 
        

            # d_init = 2000
            # v_init = 1.2
            # d_max = 3000
            # vecs = []
            
            
            s_init = d_init * v_init # Pillar center distance
            
            ax_lattice = 3**0.5 * s_init # Lattice constant
            ay_lattice = 3 * s_init

            d_var = np.linspace(d_init, d_max, x_size)
                        
            a1_ = ax_lattice * np.array([1, 0])
            a2_ = ay_lattice *np.array([0, 1])
            # a2_ = a_lattice * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])
            
            b1 = np.array([0, 0])
            b2 = 2* s_init * np.array([0, 1])
            b3 = s_init * np.array([np.cos(30 / 180 * np.pi), np.sin(30 / 180 * np.pi)])
            b4 = 3**0.5 * s_init * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])
            

            name = f"adiabaticHoney_v_{v_init}_ds{d_init}_dl{d_max}"
            
            pat_str += "\n" + "D " + name + "\n"
            pat_str += "I " + str(int(increment)) + "\n"
            pat_str += "C " + str(int(dwell_time)) + "\n"
            
            s_x = 0  
            for jj in range (0, x_size):

                x_shift = a1_*jj
                

                for ii in range (-y_size//2, y_size//2):
                    
                    s_var = d_var[jj]*v_init
                    ax_lattice = 3**0.5 * s_var # Lattice constant
                    ay_lattice = 3 * s_var
                    
                    # a1_ = ax_lattice * np.array([1, 0])
                    a2_ = ay_lattice *np.array([0, 1])
                    
                    b1 = np.array([0, 0])
                    b2 = 2* s_var * np.array([0, 1])
                    b3 = s_var * np.array([np.cos(30 / 180 * np.pi), np.sin(30 / 180 * np.pi)])
                    b4 = 3**0.5 * s_var * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])
  
                    y_shift = a2_*ii
                    
                    y_grid_offset = y_fix_offset + yindex * y_offset + y_shift
                    
                    x_grid_offset = x_fix_offset + xindex * x_offset + s_x
                    
                    pat_str += "Circle "+str(int((x_grid_offset+b1)[0]))+", "+str(int((y_grid_offset + b1)[1]))+", "+str(int(d_var[jj]/2)) + "\n"
                    pat_str += "Circle "+str(int((x_grid_offset+b2)[0]))+", "+str(int((y_grid_offset + b2)[1]))+", "+str(int(d_var[jj]/2)) + "\n"
                    pat_str += "Circle "+str(int((x_grid_offset+b3)[0]))+", "+str(int((y_grid_offset + b3)[1]))+", "+str(int(d_var[jj]/2)) + "\n"          
                    pat_str += "Circle "+str(int((x_grid_offset+b4)[0]))+", "+str(int((y_grid_offset + b4)[1]))+", "+str(int(d_var[jj]/2)) + "\n"
                
                s_x +=ax_lattice 
          
            xindex += 1       
                    
            pat_str +=  "END" + "\n"
            cntrl_str += f"draw({name})\n"
            
            name = f"adiabaticHoney_v_{v_init}_ds{d_init}_dl{d_max}_marker"
            
            pat_str += "\n" + "D " + name + "\n"
            pat_str += "I " + str(int(increment)) + "\n"
            pat_str += "C " + str(int(dwell_time)) + "\n"
            
    
            y_grid_offset = y_fix_offset + yindex * y_offset 
            
            x_grid_offset = x_fix_offset + (xindex- 1) * x_offset
            
            
            pat_str += "Circle "+str(int(x_grid_offset - 2* d_init)) + ", " + str(int(y_grid_offset -s_init /2  ))+", "+str(1250) + "\n"
            pat_str += "Circle "+str(int(x_grid_offset + s_x + d_init )) + ", " + str(int(y_grid_offset -s_init /2)) + ", " + str(1250) + "\n"
            pat_str += "END" + "\n"
            
            cntrl_str += f"draw({name})\n" + "\n"
    
 
    

#%% Adiabatic honey comb constant lattice constant

x_fix_offset = 265000 
y_fix_offset = 2000
y_offset = 85000
x_offset = 0

y_size = 16
x_size = 25

overlaps_init = [1.1, 1.3, 1.5  ]

dsmall = [1800]

dlarg = [ 2600, 3000] 

yindex = 0
for v_init in overlaps_init:
    xindex = 0
    for d_init in dsmall: 
        for d_max in dlarg:

            # d_init = 2000
            # v_init = 1.2
            # d_max = 3000
            # vecs = []
            
            
            s_init = d_init * v_init # Pillar center distance
            
            a_lattice = 3**0.5 * s_init # Lattice constant


            d_var = np.linspace(d_init, d_max, x_size)
                        
            a1_ = a_lattice * np.array([1, 0])
            a2_ = a_lattice * np.array([np.cos(60 / 180 * np.pi), np.sin(60 / 180 * np.pi)])
            
            b1 =  np.array([0, 0])
            b2 = s_init* np.array([0, 1])

            name = f"adiabaticHoney_lattice{v_init}_ds{d_init}_dl{d_max}"
            
            pat_str += "\n" + "D " + name + "\n"
            pat_str += "I " + str(int(increment)) + "\n"
            pat_str += "C " + str(int(dwell_time)) + "\n"
            
                        
            for jj in range (0, x_size):
                x_shift = a1_*jj
                shift1 = 0
                for ii in range (0, y_size):
                    shift2 = a2_*ii
                    if (ii-1)%2 == 1 and ii != 0:
                        shift1 += (ii-1)%2*(-a1_)
                    # vecs.append(b1+shift2+shift1+x_shift)
                    # vecs.append(b2+shift2+shift1+x_shift)
                    ygrid_offset = shift2+shift1+x_shift + y_fix_offset + yindex * y_offset 
                    
                    xgrid_offset = shift2+shift1+x_shift + x_fix_offset + xindex * x_offset
                    
                    pat_str += "Circle "+str(int((b1+xgrid_offset)[0]))+", "+str(int((b1+ygrid_offset)[1]))+", "+str(int(d_var[jj]/2)) + "\n"
                    pat_str += "Circle "+str(int((b2+xgrid_offset)[0]))+", "+str(int((b2+ygrid_offset)[1]))+", "+str(int(d_var[jj]/2)) + "\n"
            
            
            pat_str +=  "END" + "\n"
            cntrl_str += f"draw({name})\n"
            yindex += 1   
 # vecs = np.array(vecs)
 # fig, ax = plt.subplots()
 # plt.plot(vecs[:,0], vecs[:,1], "ko")
 # ax.set_aspect('equal')
 # plt.show()       
        

#%% Linear chain v constant

overlaps_init = [1.2, 1.1, 1.0, 0.9]

dsmall = [1800, 2000]

dlarg = [2600, 3000]

x_size = 25

#Pat positioning
x_fix_offset = 2000 + 420000
y_fix_offset = -5000 + 300000
y_offset = 12500
x_offset = 100000

yindex = 0
xindex = 0
for d_init in dsmall:

    for v_init in overlaps_init:
        for d_max in dlarg:
            
            name = f"adiabaticChain{v_init}_ds{d_init}_dl{d_max}"
            
            pat_str += "\n" + "D " + name + "\n"
            pat_str += "I " + str(int(increment)) + "\n"
            pat_str += "C " + str(int(dwell_time)) + "\n"
                        
            s_init = d_init * v_init
            d_var = np.linspace(d_init, d_max, x_size)
            
            s_var = 0
            
            for jj in range (0, x_size):
                
                pat_str += "Circle "+str(int((x_offset *xindex + x_fix_offset + s_var )))+", "+str(int((y_fix_offset + y_offset * yindex)))+", "+str(int(d_var[jj]/2)) + "\n"
                s_var += d_var[jj]*v_init
            yindex +=1
            pat_str +=  "END" + "\n"
            cntrl_str += f"draw({name})\n"
  


              
file = open("adiabatic_honey_pat.txt", "w")
file.write(pat_str)
file.close()

file = open("adiabatic_honey_ctrl.txt", "w")
file.write(cntrl_str)
file.close()




