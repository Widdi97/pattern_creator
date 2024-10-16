# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 10:47:45 2024

@author: chm66em
"""

from generate_pattern import Pattern, circle, ellipse, Lattice
from math import pi
import numpy as np
import time
import matplotlib.pyplot as plt

nom_diameter = 2 * 1e3
diameter = 1.924 * 1e3
overlaps = np.array([0.8, 0.9, 1.0, 1.1 ])
# overlaps = np.array([0.8,0.90])



total_pattern_string = ""
total_ctrl_string = ""

for v in overlaps:
    ccdistance = nom_diameter*v
    #maple leaf lattice and basis vectors
    loc1 = np.array([0,0])
    loc2 = loc1 + ccdistance/2*np.array([1,np.sqrt(3)])
    loc3 = loc2 + ccdistance*np.array([1,0])
    loc4 = loc3 + ccdistance/2*np.array([1,-np.sqrt(3)])
    loc5 = loc4 - ccdistance/2*np.array([1,np.sqrt(3)])
    loc6 = loc5 - ccdistance*np.array([1,0])
    basis_vectors = np.array([loc1,loc2,loc3,loc4,loc5,loc6])
    
    #%% rotate cell
    # unit_cell = [h1,h2,h3,h4,h5,h6]
    l1 = ccdistance/2*np.array([1,np.sqrt(3)])+ccdistance*np.array([2,0])
    l2 = ccdistance*np.array([1,np.sqrt(3)])+ccdistance/2*np.array([-1,np.sqrt(3)])
    
    
    length = np.sqrt(l1[0]**2 + l1[1]**2)
    angle = np.arccos(l1[0]/length)
    
    def rotate(vec, angle):
        x = vec[0] * np.cos(angle) - vec[1] * np.sin(angle)
        y = vec[0] * np.sin(angle) + vec[1] * np.cos(angle)
    
        return np.array([x,y])
    
    loc1_rot = rotate(loc1, -angle)
    loc2_rot = rotate(loc2, -angle)
    loc3_rot = rotate(loc3, -angle)
    loc4_rot = rotate(loc4, -angle)
    loc5_rot = rotate(loc5, -angle)
    loc6_rot = rotate(loc6, -angle)
    
    shift = - loc5_rot + np.array([loc3_rot[0],0])
    
    loc1_rot_shift = loc1_rot + shift
    loc2_rot_shift = loc2_rot + shift
    loc3_rot_shift = loc3_rot + shift
    loc4_rot_shift = loc4_rot + shift
    loc5_rot_shift = loc5_rot + shift
    loc6_rot_shift = loc6_rot + shift
    
    basis_vectors_rot = np.array([loc1_rot_shift, loc2_rot_shift, loc3_rot_shift, loc4_rot_shift, loc5_rot_shift, loc6_rot_shift])
    l1_rot = np.array([length, 0])
    l2_rot = rotate(l2, -angle)
    
    
    origin = np.array([[0, 0,0,0,0,0],[0,  0,0 ,0 ,0 ,0]]) # origin point
    
    # plt.quiver(*origin, basis_vectors[:,0], basis_vectors[:,1],color=['r','b','g',"k", "tab:blue", "tab:red"],  scale=21)
    # plt.quiver(*origin, basis_vectors_rot[:,0], basis_vectors_rot[:,1],color=['r','b','g',"k", "tab:blue", "tab:red"],  scale=21)
    # plt.show()
    
    # plt.quiver(*np.array([[0],[0]]), l1[0], l1[1],color=['tab:purple'],  scale=21)
    # plt.quiver(*np.array([[0],[0]]), l1_rot[0], l1_rot[1],color=['tab:purple'],  scale=21)
    # plt.quiver(*np.array([[0],[0]]), l2[0], l2[1],color=['tab:purple'],  scale=21)
    # plt.quiver(*np.array([[0],[0]]), l2_rot[0], l2_rot[1],color=['tab:purple'],  scale=21)
    
    
    plt.show()
    
    #%%
    x_size_ = 40 * nom_diameter
    y_size_ = 35 * nom_diameter
    
    
    lattice = Lattice(l1_rot, l2_rot, x_size_, y_size_, 0.03 * nom_diameter, [[circle, 0, 0, nom_diameter/2] for b in basis_vectors_rot], basis_vectors_rot, visualize_patterns=True, pattern_name= f"Maple_leaf_v_{v}")
    
    # lattice = Lattice(l1_rot, l2_rot, x_size_, y_size_, 0.08 * nom_diameter, [[circle, 0, 0, 0.5 * nom_diameter] for b in basis_vectors], basis_vectors, visualize_patterns=True)
    
    #%%
    total_pattern_string += lattice.pat_str
    
    total_ctrl_string += lattice.draw_latt_str
    
    
file = open("maple_leaf_pat.txt", "w")
file.write(total_pattern_string)
file.close()


file = open("maple_leaf_ctrl.txt", "w")
file.write(total_ctrl_string)
file.close()