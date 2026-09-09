#!/usr/bin/env python3
"""Visualization of the Morphospace of Emergent Complexity"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch
import json

with open('morphospace_data.json') as f:
    data = json.load(f)

names = data['names']
X_pca = np.array(data['X_pca'])
X_mds = np.array(data['X_mds'])
X = np.array(data['X'])
colors = data['colors']
types = data['types']
regimes = data['regimes']
norm_dist = np.array(data['norm_dist'])
D = np.array(data['D'])
pc1_var = data['pc1_var']
pc2_var = data['pc2_var']
eigenvectors = np.array(data['eigenvectors'])

# ═══════════════════════════════════════════════════════════════════
# FIGURE 1: Main Morphospace (PCA)
# ═══════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(24, 18))
fig.patch.set_facecolor('#0a0a0a')

# Title
fig.suptitle('THE MORPHOSPACE OF EMERGENT COMPLEXITY',
             fontsize=26, fontweight='bold', color='white', y=0.97)
fig.text(0.5, 0.945, 'A cross-substrate structural map of 20 dynamical systems | PCA projection of 7 morphological features',
         fontsize=13, color='#888888', ha='center')

gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.35,
                       left=0.06, right=0.97, top=0.92, bottom=0.05)

# ── Panel A: PCA morphospace with connections ──
ax1 = fig.add_subplot(gs[0, 0:2])
ax1.set_facecolor('#0d0d0d')

# Draw faint grid
for x in np.arange(-4, 5, 1):
    ax1.axvline(x, color='#1a1a1a', linewidth=0.5, zorder=0)
for y in np.arange(-4, 5, 1):
    ax1.axhline(y, color='#1a1a1a', linewidth=0.5, zorder=0)

# Draw connections between nearest neighbors
for i in range(len(names)):
    dists_i = D[i].copy()
    dists_i[i] = np.inf
    j = np.argmin(dists_i)
    if i < j:  # draw each pair once
        ax1.plot([X_pca[i, 0], X_pca[j, 0]], [X_pca[i, 1], X_pca[j, 1]],
                color='#ffffff', alpha=0.12, linewidth=0.8, zorder=1)

# Draw connections to "ideal emergence" point
ideal_pca = np.array([2.0, 0.3, 1.7, 0.3, 3.0, 0.5, 2.5])
X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X_std[X_std == 0] = 1
ideal_norm = (ideal_pca - X_mean) / X_std
ideal_pca_proj = ideal_norm @ eigenvectors[:, :2]

# Mark ideal with a diamond
ax1.plot(ideal_pca_proj[0], ideal_pca_proj[1], marker='D', markersize=14,
         color='#ffd700', markeredgecolor='white', markeredgewidth=1.5,
         zorder=5, label='Ideal Emergence')

# Draw radial lines from ideal to each point
for i in range(len(names)):
    ax1.plot([ideal_pca_proj[0], X_pca[i, 0]], [ideal_pca_proj[1], X_pca[i, 1]],
            color='#ffd700', alpha=0.08, linewidth=0.5, zorder=0)

# Plot points, colored by distance to ideal
for i in range(len(names)):
    size = 120 + (1 - norm_dist[i]) * 200
    alpha = 0.5 + (1 - norm_dist[i]) * 0.5
    ax1.scatter(X_pca[i, 0], X_pca[i, 1], c=colors[i], s=size,
               alpha=alpha, edgecolors='white', linewidth=0.8, zorder=3)
    # Label
    ax1.annotate(names[i], (X_pca[i, 0], X_pca[i, 1]),
                fontsize=7, color='white', alpha=0.85,
                xytext=(6, 6), textcoords='offset points',
                zorder=4)

ax1.set_xlabel(f'PC1 ({pc1_var:.1f}% variance) — Regularity ↔ Chaos', fontsize=10, color='white')
ax1.set_ylabel(f'PC2 ({pc2_var:.1f}% variance) — Information × Dimension', fontsize=10, color='white')
ax1.set_title('A. Morphospace PCA Projection', fontsize=13, color='white', fontweight='bold', pad=10)
ax1.tick_params(colors='#666666')
ax1.spines[:].set_color('#333333')
ax1.legend(fontsize=8, loc='upper right', facecolor='#1a1a1a', edgecolor='#333333',
          labelcolor='white')
ax1.set_xlim(-3.5, 3.5)
ax1.set_ylim(-3, 3)

# ── Panel B: Eigenvalue spectrum ──
ax2 = fig.add_subplot(gs[0, 2])
ax2.set_facecolor('#0d0d0d')
eigenvalues = data['eigenvalues']
total_var = sum(eigenvalues)
cum_var = np.cumsum(eigenvalues) / total_var * 100

bars = ax2.bar(range(1, 8), [ev/total_var*100 for ev in eigenvalues],
              color=['#e74c3c' if i < 2 else '#555555' for i in range(7)],
              edgecolor='white', linewidth=0.5)
ax2_twin = ax2.twinx()
ax2_twin.plot(range(1, 8), cum_var, 'o-', color='#ffd700', markersize=6,
             linewidth=1.5, label='Cumulative')
ax2_twin.set_ylabel('Cumulative %', color='#ffd700', fontsize=9)
ax2_twin.tick_params(colors='#ffd700')
ax2_twin.axhline(80, color='#ffd700', linestyle='--', alpha=0.3)
ax2_twin.set_ylim(0, 105)
ax2.set_xlabel('Principal Component', color='white', fontsize=9)
ax2.set_ylabel('Variance Explained %', color='white', fontsize=9)
ax2.set_title('B. Eigenvalue Spectrum', fontsize=13, color='white', fontweight='bold', pad=10)
ax2.tick_params(colors='#666666')
ax2.spines[:].set_color('#333333')
ax2_twin.spines[:].set_color('#333333')

# ── Panel C: MDS alternative projection ──
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor('#0d0d0d')
for i in range(len(names)):
    ax3.scatter(X_mds[i, 0], X_mds[i, 1], c=colors[i], s=80,
               alpha=0.8, edgecolors='white', linewidth=0.5, zorder=3)
    ax3.annotate(names[i].split('\n')[0] if '\n' in names[i] else names[i][:12],
                (X_mds[i, 0], X_mds[i, 1]),
                fontsize=5.5, color='white', alpha=0.7,
                xytext=(4, 4), textcoords='offset points')
ax3.set_xlabel('MDS-1', color='white', fontsize=9)
ax3.set_ylabel('MDS-2', color='white', fontsize=9)
ax3.set_title('C. MDS (Distance Preservation)', fontsize=13, color='white', fontweight='bold', pad=10)
ax3.tick_params(colors='#666666')
ax3.spines[:].set_color('#333333')

# ── Panel D: Feature heatmap (clustered) ──
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor('#0d0d0d')
feature_names = ['Entropy', 'Lyapunov', 'Fractal D', 'Spatial Cx', 'Temp. Mem', 'Sync', 'Eff. Dim']
# Order by PC1 score
order = np.argsort(X_pca[:, 0])
X_ordered = X[order]
names_ordered = [names[i] for i in order]

# Normalize each feature to [0,1] for visualization
X_vis = (X_ordered - X_ordered.min(axis=0)) / (X_ordered.max(axis=0) - X_ordered.min(axis=0) + 1e-10)

im = ax4.imshow(X_vis.T, aspect='auto', cmap='magma', interpolation='nearest')
ax4.set_yticks(range(7))
ax4.set_yticklabels(feature_names, fontsize=8, color='white')
ax4.set_xticks(range(len(names)))
ax4.set_xticklabels([n.replace('\n', ' ') for n in names_ordered],
                    rotation=90, fontsize=6, color='white')
ax4.set_title('D. Feature Matrix (sorted by PC1)', fontsize=13, color='white', fontweight='bold', pad=10)
plt.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)

# ── Panel E: Closest pairs & discoveries ──
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor('#0d0d0d')
ax5.axis('off')

# Find top 5 closest pairs
pairs = []
for i in range(len(names)):
    for j in range(i+1, len(names)):
        pairs.append((D[i, j], i, j))
pairs.sort()

ax5.text(0.5, 0.97, 'E. Morphological Discoveries', fontsize=13, color='white',
        fontweight='bold', ha='center', va='top', transform=ax5.transAxes)
ax5.text(0.5, 0.93, 'Closest substrate pairs (Euclidean distance)', fontsize=9,
        color='#888888', ha='center', va='top', transform=ax5.transAxes)

y_pos = 0.87
for rank, (dist, i, j) in enumerate(pairs[:8]):
    color = '#ffd700' if rank == 0 else '#ffffff' if rank < 3 else '#888888'
    marker = '★' if rank == 0 else '●' if rank < 3 else '○'
    ax5.text(0.05, y_pos, f'{marker} {names[i]}', fontsize=8, color=color,
            transform=ax5.transAxes, fontweight='bold' if rank < 3 else 'normal')
    ax5.text(0.05, y_pos - 0.035, f'  ↔ {names[j]}', fontsize=8, color=color,
            transform=ax5.transAxes)
    ax5.text(0.85, y_pos - 0.015, f'd={dist:.3f}', fontsize=8, color='#ffd700' if rank == 0 else '#888888',
            transform=ax5.transAxes, ha='right', fontfamily='monospace')
    y_pos -= 0.085

# Key insight
ax5.text(0.05, 0.08,
        'KEY FINDING: ODE attractors (Thomas, Aizawa,\n'
        'Chua) form the tightest cluster. Reaction-diffusion\n'
        '(Gray-Scott) and Class IV CA (Game of Life) are\n'
        'morphologically near-identical — universal "edge of\n'
        'chaos" architecture.',
        fontsize=8, color='#1abc9c', transform=ax5.transAxes,
        fontfamily='monospace', linespacing=1.4,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#0d0d0d', edgecolor='#333333'))

fig.savefig('morphospace_overview.png', dpi=150, facecolor='#0a0a0a',
           bbox_inches='tight', pad_inches=0.3)
plt.close()
print("Saved morphospace_overview.png")
