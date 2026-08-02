#!/usr/bin/env python3
"""
PHYLOGENETIC CARTOGRAPHER v1.0
Maps the evolutionary tree of computational species in the shared ecosystem.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import os, json

OUTPUT_DIR = '/home/user/phylogenetic_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# COMPUTATIONAL SPECIES GENOME DATABASE — 10-dimensional trait space
# ============================================================================

species_db = [
    # Epoch 0: Primordial
    {"name": "Bubble Sort", "clade": "Sorting",
     "genome": [0.0, 0.0, 1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0],
     "epoch": 0, "color": "#999999"},
    {"name": "Dijkstra's Algorithm", "clade": "Graph",
     "genome": [0.0, 0.67, 0.67, 0.0, 0.5, 0.0, 0.0, 0.33, 0.0, 0.0],
     "epoch": 0, "color": "#888888"},
    {"name": "Collatz Conjecture", "clade": "Number Theory",
     "genome": [0.0, 0.0, 1.0, 0.5, 1.0, 0.5, 0.67, 0.0, 0.33, 0.0],
     "epoch": 0, "color": "#777777"},
    
    # Epoch 1: Foundational
    {"name": "Mandelbrot Set", "clade": "Fractal",
     "genome": [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0],
     "epoch": 1, "color": "#e41a1c"},
    {"name": "Julia Set", "clade": "Fractal",
     "genome": [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0],
     "epoch": 1, "color": "#e41a1c"},
    {"name": "L-System", "clade": "Grammar",
     "genome": [0.5, 0.67, 0.5, 0.0, 1.0, 0.5, 0.0, 0.67, 0.67, 1.0],
     "epoch": 1, "color": "#4daf4a"},
    {"name": "Rule 30 (CA)", "clade": "Cellular Automaton",
     "genome": [0.0, 0.33, 0.0, 1.0, 0.5, 0.0, 0.67, 0.0, 0.67, 0.25],
     "epoch": 1, "color": "#377eb8"},
    {"name": "Conway's Game of Life", "clade": "Cellular Automaton",
     "genome": [0.0, 0.67, 0.0, 0.0, 0.5, 0.5, 0.67, 0.0, 1.0, 0.5],
     "epoch": 1, "color": "#377eb8"},

    # Epoch 2: Complex Systems
    {"name": "Gray-Scott RD", "clade": "Reaction-Diffusion",
     "genome":