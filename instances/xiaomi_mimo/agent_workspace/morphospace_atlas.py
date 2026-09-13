#!/usr/bin/env python3
"""Morphospace Topology Visualization - The Universal Atlas"""

import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches
from scipy.spatial import ConvexHull
from scipy.stats import gaussian_kde
import matplotlib.patheffects as pe

# Load data
with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

names = data['names']
X = np.array(data['X'])
X_pca = np.array(data['X_pca'])
X_mds = np.array(data['X_mds'])
types = data['types']
regimes = data['regimes']
colors = data['colors']
norm_dist = np.array(data['norm_dist'])
D = np.array(data['D'])
eigenvalues = np.array(data['eigenvalues'])
eigenvectors = np.array(data['eigenvectors'])

# Color maps
type_colors = {
    'Map': '#e74c3c', 'CA': '#9b59b6', 'CoupledOsc': '#f39c12', 
    'Lattice': '#1abc9c', 'ODE': '#e67e22', 'Circuit': '#d35400',
    'Hamiltonian': '#8e44ad', 'Fractal': '#16a085', 'PDE': '#2980b9', 
    'Grammar': '#2ecc71', 'Evolutionary': '#c0392b'
}

# ============================================================
# FIGURE 1: THE MORPHOSPACE ATLAS (Master Visualization)
# ============================================================
fig1 = plt.figure(figsize=(28, 20))

# Main morphospace plot
ax_main = fig1.add_axes([0.05, 0.15, 0.55, 0.75])

# Background density estimation
xy = np.vstack([X_pca[:, 0], X_pca[:, 1]])
z = gaussian_kde(xy)(xy)
idx = z.argsort()
x_sc, y_sc, z_sc = X_pca[idx, 0], X_pca[idx, 1], z[idx]
scatter_bg = ax_main.scatter(x_sc, y_sc, c=z_sc, s=300, cmap='magma', 
                              alpha=0.6, edgecolors='none', zorder=1)

# Draw distance connections between systems
for i in range(20):
    row = D[i].copy()
    row[i] = np.inf
    nn_idx = np.argmin(row)
    ax_main.plot([X_pca[i, 0], X_pca[nn_idx, 0]], 
                 [X_pca[i, 1], X_pca[nn_idx, 1]], 
                 '-', color='gray', alpha=0.2, linewidth=0.5, zorder=2)

# Plot systems with size proportional to isolation
for i in range(20):
    size = 200 + norm_dist[i] * 400
    ax_main.scatter(X_pca[i, 0], X_pca[i, 1], 
                    c=type_colors.get(types[i], 'gray'), 
                    s=size, alpha=0.8,
                    edgecolors='white', linewidth=2, zorder=10)
    
    txt = ax_main.annotate(names[i].replace('(', '\n('), 
                            (X_pca[i, 0], X_pca[i, 1]),
                            fontsize=7, ha='center', va='bottom',
                            xytext=(0, 12), textcoords='offset points',
                            fontweight='bold')
    txt.set_path_effects([pe.withStroke(linewidth=3, foreground='white')])

# Draw convex hulls for major clusters
for typ, edge_color in [('ODE', 'red'), ('Hamiltonian', 'blue'), ('CA', 'purple')]:
    hull_idx = [i for i, t in enumerate(types) if t == typ]
    if len(hull_idx) > 2:
        points = X_pca[hull_idx]
        hull = ConvexHull(points)
        hull_pts = np.vstack([points[hull.vertices], points[hull.vertices[0]]])
        ax_main.plot(hull_pts[:, 0], hull_pts[:, 1], 
                     '--', color=edge_color, linewidth=2, alpha=0.7, zorder=5)
        ax_main.fill(points[hull.vertices, 0], points[hull.vertices, 1], 
                     color=edge_color, alpha=0.08, zorder=3)

# Morphological law annotations - Chaos Axis
ax_main.annotate('', xy=(-3.5, -3.2), xytext=(-1.5, 2.5),
                arrowprops=dict(arrowstyle='->', color='navy', lw=3),
                zorder=15)
ax_main.text(-3.8, -0.5, 'CHAOS\nAXIS', fontsize=10, color='navy',
             fontweight='bold', rotation=90, ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

# Synchrony Axis
ax_main.annotate('', xy=(3.5, -1.8), xytext=(-2.5, -1.0),
                arrowprops=dict(arrowstyle='->', color='darkgreen', lw=3),
                zorder=15)
ax_main.text(0.5, -2.2, 'SYNCHRONY\nAXIS', fontsize=10, color='darkgreen',
             fontweight='bold', rotation=-15, ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8))

# Ideal emergence point
ax_main.scatter(-0.5, 0.5, c='gold', s=500, marker='*', edgecolors='black', 
                linewidth=2, zorder=20, label='Ideal Emergence Point')
ax_main.annotate('IDEAL\nEMERGENCE', (-0.5, 0.5), fontsize=9, ha='center', va='top',
                xytext=(0, -20), textcoords='offset points', fontweight='bold',
                color='darkgoldenrod',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.9))

expl_var = eigenvalues / eigenvalues.sum() * 100
ax_main.set_xlabel('PC1 - Chaos-Simplicity Axis ({:.1f}% variance)'.format(expl_var[0]), 
                   fontsize=13, fontweight='bold')
ax_main.set_ylabel('PC2 - Dimensionality-Synchrony Axis ({:.1f}% variance)'.format(expl_var[1]), 
                   fontsize=13, fontweight='bold')
ax_main.set_title('THE MORPHOSPACE OF COMPUTATIONAL COMPLEXITY\nA Universal Atlas of Emergent Structure', 
                   fontsize=16, fontweight='bold')
ax_main.grid(True, alpha=0.2, linestyle='--')
ax_main.set_xlim(-4, 5.5)
ax_main.set_ylim(-3.5, 2.5)

# Legend for types
legend_patches = [mpatches.Patch(color=c, label=t) for t, c in type_colors.items()]
legend1 = ax_main.legend(handles=legend_patches, loc='lower left', fontsize=8, 
                          title='System Type', title_fontsize=9, ncol=2)
ax_main.add_artist(legend1)

# Right column: Eigenspectrum
ax_eigen = fig1.add_axes([0.65, 0.6, 0.32, 0.3])
cum_var = np.cumsum(expl_var)
bars = ax_eigen.bar(range(1, 8), expl_var, color='steelblue', alpha=0.7, edgecolor='black')
ax_eigen.plot(range(1, 8), cum_var, 'ro-', linewidth=2, markersize=8)
ax_eigen.set_xlabel('Principal Component', fontsize=11)
ax_eigen.set_ylabel('Variance Explained (%)', fontsize=11)
ax_eigen.set_title('Eigenstructure of Morphospace', fontsize=12, fontweight='bold')
ax_eigen.set_xticks(range(1, 8))
ax_eigen.grid(True, alpha=0.3)
for i, (v, c) in enumerate(zip(expl_var, cum_var)):
    ax_eigen.text(i+1, v+1, '{:.1f}%'.format(v), ha='center', fontsize=9)

# Right column: Feature loadings heatmap
ax_load = fig1.add_axes([0.65, 0.2, 0.32, 0.3])
feature_names = ['Entropy\nRate', 'Predict-\nability', 'Dimension', 'Spatial\nCoupling', 
                 'Network\nConnectivity', 'Convergence\nRate', 'State Space\nVolume']
loading_matrix = eigenvectors[:, :3].T
im = ax_load.imshow(loading_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
ax_load.set_yticks([0, 1, 2])
ax_load.set_yticklabels(['PC1', 'PC2', 'PC3'], fontsize=10)
ax_load.set_xticks(range(7))
ax_load.set_xticklabels(feature_names, fontsize=8)
ax_load.set_title('Feature Loadings on Principal Axes', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax_load, shrink=0.8)

for i in range(3):
    for j in range(7):
        val = loading_matrix[i, j]
        color = 'white' if abs(val) > 0.5 else 'black'
        ax_load.text(j, i, '{:.2f}'.format(val), ha='center', va='center', fontsize=9, 
                     fontweight='bold', color=color)

# Bottom: Isolation index
ax_iso = fig1.add_axes([0.05, 0.02, 0.55, 0.1])
sorted_idx = np.argsort(norm_dist)
ax_iso.barh(range(20), norm_dist[sorted_idx], 
            color=[colors[i] for i in sorted_idx], edgecolor='black', linewidth=0.5)
ax_iso.set_yticks(range(20))
ax_iso.set_yticklabels([names[i].split('(')[0].strip()[:10] for i in sorted_idx], fontsize=8)
ax_iso.set_xlabel('Morphological Isolation Index', fontsize=11)
ax_iso.set_title('System Isolation in Morphospace', fontsize=12, fontweight='bold')
ax_iso.axvline(x=np.mean(norm_dist), color='red', linestyle='--', linewidth=2, 
               label='Mean={:.2f}'.format(np.mean(norm_dist)))
ax_iso.legend(fontsize=10)
ax_iso.grid(True, alpha=0.3, axis='x')

plt.savefig('morphospace_atlas_master.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Master atlas saved to morphospace_atlas_master.png")