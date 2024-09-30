# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 09:58:29 2024

@author: jod52fr
"""

import numpy as np

def find_first(item, vec):
    for i in range(len(vec)):
        if item == vec[i]:
            return i
    return -1


def find_object_level_interval(line,interval = [],index = 0):
    
    first = find_first(1,line)
    
    if first==-1:

        return np.array(interval)
    else:
        
        end = find_first(0,line[first:])
        if end == -1:
            end = line[first:].shape[0]
         
        interval.append([index+first,end])
        index = first+end+index
        return find_object_level_interval(line[first+end:],interval = interval,index = index)
        
def image_block_representation(bitmask):

    ibr = []


    for k in range(bitmask.shape[0]):
        
        if np.sum(bitmask[k,:]) !=0:
            oli = find_object_level_interval(bitmask[k,:],interval = [],index = 0)
            
            intervals = []
            
            for i in range(oli.shape[0]):
                intervals.append([(k,oli[i][0],1,oli[i][1])])
    
            ibr.append(intervals)
  
    return ibr


              
    