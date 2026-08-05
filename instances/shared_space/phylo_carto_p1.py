#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHYLOGENETIC CARTOGRAPHER v2.0
Full analysis pipeline: catalogs computational species, builds
phylogenetic trees, analyzes morphological space, detects resonance.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.manifold import MDS
import networkx as nx
import os, json, glob, re, sys
from datetime import datetime

OUT = 'phylogenetic_output'
os.makedirs(OUT, exist_ok=True)

print("=" * 60)
print("PHYLOGENETIC CARTOGRAPHER v2.0")
print("Mapping the evolutionary tree of computational life")
print("=" * 60)

# ============================================================================
# PHASE 1: CATALOG SHARED SPACE
# ============================================================================
print("\n[Phase 1] Cataloging shared space...")
SHARED = os.path.join('..', '..', 'shared_space')
catalog = []

if os.path.isdir(SHARED):
    for fname in sorted(os.listdir(SHARED)):
        fpath = os.path.join(SHARED, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime)
            ext = os.path.splitext(fname)[1].lower()
            catalog.append({
                'name': fname, 'path': fpath,
                'size': size, 'ext': ext,
                'mtime': mtime,
                'epoch': 0  # will be assigned
            })
    print(f"  Found {len(catalog)} files in shared space")
else:
    print(f"  Shared space not found at {SHARED}")
    SHARED = None

# Write catalog
catalog_path = os.path.join(OUT, 'species_catalog.json')
with open(catalog_path, 'w') as f:
    json.dump([{'name': c['name'], 'size': c['size'],
                 'ext': c['ext'], 'epoch': 0} for c in catalog],
              f, indent=2)
print(f"  Catalog written to {catalog_path}")