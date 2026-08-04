#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.manifold import MDS
import networkx as nx
import os, json

OUT = 'phylogenetic_output'
os.makedirs(OUT, exist_ok=True)

species_db = [
    {'name': 'Bubble Sort', 'clade': 'Sorting', 'epoch': 0, 'color': '#999999',
     'genome': [0.0, 0.0, 1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0]},
    {'name': 'Dijkstra', 'clade': 'Graph', 'epoch': 0, 'color': '#888888',
     'genome': [0.0, 0.67, 0.67, 0.0, 0.5, 0.0, 0.0, 0.33, 0.0, 0.0]},
    {'name': 'Collatz', 'clade': 'Number Theory', 'epoch': 0, 'color': '#777777',
     'genome': [0.0, 0.0, 1.0, 0.5, 1.0, 0.5, 0.67, 0.0, 0.33, 0.0]},
    {'name': 'Mandelbrot Set', 'clade': 'Fractal', 'epoch': 1, 'color': '#e41a1c',
     'genome': [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0]},
    {'name': 'Julia Set', 'clade': 'Fractal', 'epoch': 1, 'color': '#e41a1c',
     'genome': [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0]},
    {'name': 'L-System', 'clade': 'Grammar', 'epoch': 1, 'color': '#4daf4a',
     'genome': [0.5, 0.67, 0.5, 0.0, 1.0, 0.5, 0.0, 0.67, 0.67, 1.0]},
    {'name': 'Rule 30 CA', 'clade': 'CA', 'epoch': 1, 'color': '#377eb8',
     'genome': [0.0, 0.33, 0.0, 1.0, 0.5, 0.0, 0.67, 0.0, 0.67, 0.25]},
    {'name': 'Conway GoL', 'clade': 'CA', 'epoch': 1, 'color': '#377eb8',
     'genome': [0.0, 0.67, 0.0, 0.0, 0.5, 0.5, 0.67, 0.0, 1.0, 0.5]},
    {'name': 'Gray-Scott RD', 'clade': 'RD', 'epoch': 2, 'color': '#ff7f00',
     'genome': [1.0, 0.67, 0.33, 0.5, 0.67, 1.0, 0.67, 0.33, 1.0, 0.5]},
    {'name': 'Lorenz Attractor', 'clade': 'Chaos', 'epoch': 2, 'color': '#984ea3',
     'genome': [1.0, 1.0, 0.67, 1.0, 0.67, 1.0, 1.0, 0.33, 0.33, 0.0]},
    {'name': 'Kuramoto Model', 'clade': 'Sync', 'epoch': 2, 'color': '#a65628',
     'genome': [1.0, 0.33, 1.0, 0.5, 0.67, 1.0, 0.67, 0.33, 0.67, 0.25]},
]

print('Species database loaded:', len(species_db), 'species')