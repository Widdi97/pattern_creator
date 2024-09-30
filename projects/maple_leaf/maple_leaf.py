# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 00:44:18 2024

@author: jod52fr
"""
from generate_pattern import Pattern, circle, ellipse
from math import pi
import numpy as np
import time

nom_diameter = 2
diameter = 1.924
overlaps = np.array([0.8,0.85,0.9,0.95,1,1.05,1.1])
# overlaps = np.array([0.8,0.85])

total_pattern_string = ""
for v in overlaps:
    ccdistance = nom_diameter*v
    
    #maple leaf lattice and basis vectors
    loc1 = np.array([0,0])
    loc2 = loc1 + ccdistance/2*np.array([1,np.sqrt(3)])
    loc3 = loc2 + ccdistance*np.array([1,0])
    loc4 = loc3 + ccdistance/2*np.array([1,-np.sqrt(3)])
    loc5 = loc4 - ccdistance/2*np.array([1,np.sqrt(3)])
    loc6 = loc5 - ccdistance*np.array([1,0])
    
    # unit_cell = [h1,h2,h3,h4,h5,h6]
    l1 = ccdistance/2*np.array([1,np.sqrt(3)])+ccdistance*np.array([2,0])
    l2 = ccdistance*np.array([1,np.sqrt(3)])+ccdistance/2*np.array([-1,np.sqrt(3)])
    
    ay = int(np.rint(l2*5*1e3-l1*1e3)[1])
    bx = int(np.rint(l1*3*1e3-l2*1e3)[0])
    # print()
    # print()
    
    l_vectors =np.array([l1,l2]) 
    basis_vectors = np.array([loc1,loc2,loc3,loc4,loc5,loc6])
    
    minbx = np.min(basis_vectors[:,0])
    minby = np.min(basis_vectors[:,1])
    
    basis_vectors[:,0] = basis_vectors[:,0]+(np.abs(minbx)+nom_diameter/2)*np.ones_like(basis_vectors[:,0])
    basis_vectors[:,1] = basis_vectors[:,1]+(np.abs(minby)+nom_diameter/2)*np.ones_like(basis_vectors[:,1])
    
    name_start = "dred_1um924_"+str(v).replace(".","v")+"_res15_big"
    
    
    
    # overlapp = 0.7
    resolution_ratio = 18
    
    resolution = round(diameter * resolution_ratio) 
    off = resolution/2
    start_time = time.time()
    
    pattern_boundX = np.max(basis_vectors[:,0])*1e3-np.min(basis_vectors[:,0])*1e3+nom_diameter*1e3
    pattern_boundY = np.max(basis_vectors[:,1])*1e3-np.min(basis_vectors[:,1])*1e3+nom_diameter*1e3
    
    # # intitialize first pattern object
    # pattern = Pattern(3*pattern_boundX, 3*pattern_boundY, resolution,pattern_name=name_start+name_start+"_start")
    
    # # # add all circles; idea: use a dimer as starting point and add single pillars -> no problem with alignment
    basis_vectors = basis_vectors*1e3+ np.array([off,off])+ np.array([4000,0])
    
  
    
    start_time = time.time()
    if v>=1:
        a = 1
        
        header = ""
        header += "D " +name_start+"_use,"+str(bx)+","+str(ay)+","+"10,7" + "\n"
        header += "I " + str(int(16)) + "\n"
        header += "C " + str(int(100)) + "\n"
        
        total_pattern_string += header 
        pattern_string = ""
        
        for vec in basis_vectors:
            vec = vec+np.array([6000,10000])
            pattern_string+= "CIRCLE " +str(int(vec[0]))+","+str(int(vec[1]))+","+str(int(diameter*1e3/2))+"\n"
            total_pattern_string+=pattern_string
            
    
    
            ##########
            m = np.arange(0,5)
            n = np.arange(0,3)
            mn = np.meshgrid(m,n)
            mn = np.array([mn[0].flatten(),mn[1].flatten()]).T
            mn[-1] = np.array([-1,2])
            mn = np.delete(mn,0,axis = 0)
            #############
            
            
            for m,n in mn:
                
                offsetX = vec[0]+m*l2[0]*1e3+n*l1[0]*1e3
                offsetY = vec[1]+m*l2[1]*1e3+n*l1[1]*1e3
   
                # pattern_string = pattern.export_pattern(complete=False, export=False, offsetx=offsetX, offsety=offsetY)
                pattern_string+= "CIRCLE " +str(int(offsetX))+","+str(int(offsetY))+","+str(int(diameter*1e3/2))+"\n"
                total_pattern_string+=pattern_string

             
         
        
        total_pattern_string+=pattern_string
        total_pattern_string+="END \n\n"

    else:
        
        # intitialize second pattern object
        pattern = Pattern(2*pattern_boundX,pattern_boundY+5*off, resolution,pattern_name = name_start+"_use,"+str(bx)+","+str(ay)+","+"10,7")
        
        # add all circles; idea: use a dimer as starting point and add single pillars -> no problem with alignment
        
        for vec in basis_vectors:
            shift_r = vec+l1*1e3
            shift_o =  vec+l2*1e3
            shift_u = vec+(l2-l1)*1e3
            pattern.add_parametrized_shape(circle, *shift_r, diameter/2*1e3, boolean_operation = "subtract") 
            pattern.add_parametrized_shape(circle, *shift_u, diameter/2*1e3, boolean_operation = "subtract") 
        
            pattern.add_parametrized_shape(circle, *shift_o, diameter/2*1e3, boolean_operation = "subtract") 
        
            pattern.add_parametrized_shape(circle, *vec, diameter/2*1e3)      
        # # generate .pat string
        # pattern_string = pattern.export_pattern(complete=False, export=False, offsetx=6000, offsety=10000)
        total_pattern_string+=pattern.generate_pattern_header()
        # total_pattern_string+=pattern_string

        
        ##########
        m = np.arange(0,5)
        n = np.arange(0,3)
        mn = np.meshgrid(m,n)
        mn = np.array([mn[0].flatten(),mn[1].flatten()]).T
        mn[-1] = np.array([-1,2])
        # mn = np.delete(mn,0,axis = 0)
        #############
        
        
        for m,n in mn:
            
            offsetX = 6000+vec[0]+m*l2[0]*1e3+n*l1[0]*1e3
            offsetY = 10000+vec[1]+m*l2[1]*1e3+n*l1[1]*1e3

            pattern_string = pattern.export_pattern(complete=False, export=False, offsetx=offsetX, offsety=offsetY)
            total_pattern_string+=pattern_string

            
        nlines = pattern_string.count('\n') - 3

        total_pattern_string+="END \n\n"
        
        # # print .pat string
        # # print(pattern_string)
        
        # # # plot
        pattern.visualize()
        
        end_time=time.time()
        duration = end_time - start_time
        print('\n' + f"this pattern took {duration:.4f} seconds and is {nlines} rectangles long" + '\n')
with open("maple_leaf_2d0_var_res18_big_nom_diameter_V2" + '.txt', 'w') as f:
    f.write(total_pattern_string)

