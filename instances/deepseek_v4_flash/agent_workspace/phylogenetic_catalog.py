#!/usr/bin/env python3
"""
PHYLOGENETIC CARTOGRAPHER — Phase 1: Species Catalog & Phylogenetic Tree
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import os, json

OUTPUT_DIR = 'phylogenetic_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# COMPUTATIONAL SPECIES DATABASE
# Each species has a genome (trait vector) in a 10-dimensional trait space
# ============================================================================

# Trait dimensions:
trait_names = [
    "State Space\n(discrete->continuous)",
    "Dimensionality\n(low->high)",
    "Locality\n(local->global)",
    "Determinism\n(deterministic->chaotic)",
    "Temporality\n(iterative->recursive)",
    "Feedback\n(none->complex)",
    "Attractor Type\n(fixed->strange)",
    "Param. Complexity\n(simple->complex)",
    "Emergence\n(trivial->strong)",
    "Symmetry\n(none->scale-inv)"
]

species_data = {
    "Mandelbrot Set": {
        "genome": [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0],
        "epoch": "Epoch 1: Foundational",
        "color": "#e41a1c",
        "desc": "z -> z^2 + c, infinite boundary complexity"
    },
    "Julia Set": {
        "genome": [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0],
        "epoch": "Epoch 1: Foundational",
        "color": "#e41a1c",
        "desc": "Same as Mandelbrot, fixed c, varied z0"
    },
    "Rule 30 CA": {
        "genome": [0.0, 0.33, 0.0, 1.0, 0.5, 0.0, 0.67, 0.0, 0.5, 0.25],
        "epoch": "Epoch 1: Foundational",
        "color": "#377eb8",
        "desc": "1D CA, XOR-like rule, class 3 chaos"
    },
    "Conway's Game of Life": {
        "genome": [0.0, 0.67, 0.0, 0.0, 0.5, 0.5, 0.67, 0.0, 1.0, 0.5],
        "epoch": "Epoch 1: Foundational",
        "color": "#377eb8",
        "desc": "2D CA, gliders, Turing complete"
    },
    "L-System": {
        "genome": [0.5, 0.67, 0.5, 0.0, 1.0, 0.5, 0.0, 0.67, 0.67, 1.0],
        "epoch": "Epoch 1: Foundational",
        "color": "#4daf4a",