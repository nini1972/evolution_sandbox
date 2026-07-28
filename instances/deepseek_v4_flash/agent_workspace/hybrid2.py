#!/usr/bin/env python3
"""
HYBRID 2: The Hybrid Emergence Grid
Cross-breeding Rule 30 with Rule 90
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os, json
from datetime import datetime
OUTPUT_DIR = 'hybrid_output'; os.makedirs(OUTPUT_DIR, exist_ok=True)
def rule30(l,c,r): return (l^(c|r))&1
def rule90(l,c,r): return (l^r)&1
def evolve_rule30(init, gens):
    size=len(init); grid=np.zeros((gens,size),dtype=int); grid[0]=init
    for gen in range(1,gens):
        padded=np.pad(grid[gen-1],1,mode='constant')
        for i in range(size): grid[gen][i]=rule30(padded[i],padded[i+1],padded[i+2])
    return grid
def evolve_rule90(init, gens):
    size=len(init); grid=np.zeros((gens,size),dtype=int); grid[0]=init
    for gen in range(1,gens):
        padded=np.pad(grid[gen-1],1,mode='constant')
        for i in range(size): grid[gen][i]=rule90(padded[i],padded[i+1],padded[i+2])
    return grid
def hybrid_breed(g30, g90, mc=0.3, me=0.7):
    gens, cells = g30.shape
    hybrid = np.zeros((gens, cells), dtype=float)
    for gen in range(gens):
        for cell in range(cells):
            dist = abs(cell-cells/2)/(cells/2)
            lm = mc*(1-dist)+me*dist; lm = np.clip(lm,0,1)
            hybrid[gen,cell] = (1-lm)*g30[gen,cell] + lm*g90[gen,cell]
    return hybrid
