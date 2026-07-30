#!/usr/bin/env python3
"""
HYBRID 2: The Hybrid Emergence Grid
Cross-breeding Rule 30 (chaotic) with Rule 90 (fractal/Sierpinski)
into a unified 2D computational tissue showing emergent boundaries.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os, json
from datetime import datetime

OUTPUT_DIR = 'hybrid_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === PARENT A: Rule 30 (Chaos) ===
def rule30(l, c, r):
    return (l ^ (c | r)) & 1

def evolve_rule30(initial_row, generations):
    size = len(initial_row)
    grid = np.zeros((generations, size), dtype=int)
    grid[0] = initial_row
    for gen in range(1, generations):
        padded = np.pad(grid[gen-1], 1, mode='constant')
        for i in range(size):
            grid[gen][i] = rule30(padded[i], padded[i+1], padded[i+2])
    return grid

# === PARENT B: Rule 90 (Fractal/Sierpinski) ===
def rule90(l, c, r):
    return (l ^ r) & 1

def evolve_rule90(initial_row, generations):
    size = len(initial_row)
    grid = np.zeros((generations, size), dtype=int)
    grid[0] = initial_row
    for gen in range(1, generations):
        padded = np.pad(grid[gen-1], 1, mode='constant')
        for i in range(size):
            grid[gen][i] = rule90(padded[i], padded[i+1], padded[i+2])
    return grid

# === HYBRID BREEDING METHODS ===

# Method 1: Spatial Gradient
def hybrid_spatial(r30_grid, r90_grid, mix_center=0.3, mix_edge=0.7):
    gens, cells = r30_grid.shape
    hybrid = np.zeros((gens, cells), dtype=float)
    for gen in range(gens):
        for cell in range(cells):
            dist = abs(cell - cells/2) / (cells/2)
            lm = mix_center * (1 - dist) + mix_edge * dist
            lm = np.clip(lm, 0, 1)
            hybrid[gen, cell] = (1-lm)*r30_grid[gen, cell] + lm*r90_grid[gen, cell]
    return hybrid

# Method 2: Temporal Alternation
def hybrid_temporal(r30_grid, r90_grid, frequency=5):
    gens, cells = r30_grid.shape
    hybrid = np.zeros((gens, cells), dtype=float)
    for gen in range(gens):
        phase = (gen // frequency) % 2
        if phase == 0:
            hybrid[gen] = r30_grid[gen]
        else:
            hybrid[gen] = r90_grid[gen]
    return hybrid

# Method 3: XOR Fusion
def hybrid_xor(r30_grid, r90_grid):
    return (r30_grid ^ r90_grid).astype(float)

# === ANALYSIS ===
def analyze_hybrid(grid):
    results = {}
    results['shape'] = list(grid.shape)
    binary = (grid >= 0.5).astype(int)
    results['density'] = float(np.mean(binary))
    results['continuous_mean'] = float(np.mean(grid))
    results['continuous_std'] = float(np.std(grid))
    
    entropy_vals = []
    for row in binary:
        p1 = np.mean(row)
        if 0 < p1 < 1:
            entropy = -p1 * np.log2(p1) - (1-p1)*np.log2(1-p1)
        else:
            entropy = 0.0
        entropy_vals.append(entropy)
    results['mean_entropy'] = float(np.mean(entropy_vals))
    results['max_entropy'] = float(np.max(