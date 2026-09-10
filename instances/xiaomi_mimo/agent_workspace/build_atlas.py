#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial import ConvexHull
import json

with open('morphospace_data.json') as f:
    data = json.load(f)
with open('morphology_invariants.json') as f:
    invariants = json.load(f)

names = data['names']
X = np.array(data['X'])
X_pca = np.array(data['X_pca'])
colors_list = data['colors']
types = data['types']
pc1_var = data['pc1_var']
pc2_var = data['pc2_var']
complexity = invariants['complexity_index']
ideal_dist = invariants['ideal_distances']
corr = np.array(invariants['feature_correlations'])
short_names = ['Entropy', 'Lyapunov', 'Fractal D', 'Spatial Cx', 'Temp Mem', 'Sync', 'Eff Dim']

type_colors = {
    'CA': '#e74c3c', 'Circuit': '#9b59b6', 'CoupledOsc': '#3498db',
    'Evolutionary': '#2ecc71', 'Fractal': '#f39c12', 'Grammar': '#1abc9c',
    'Hamiltonian': '#e67e22', 'Lattice': '#c0392b', 'Map': '#8e44ad',
    'ODE': '#27ae60', 'PDE': '#2980b9'
}

type_groups = {}
for i, t in enumerate(types):
    type_groups.setdefault(t, []).append(i)

pc1_pct = str(round(pc1_var, 1))
pc2_pct = str(round(pc2_var, 1))

fig = plt.figure(figsize=(32, 24))
fig.patch.set_facecolor('#0a0a0a')
fig.suptitle('THE MORPHOLOGICAL ATLAS OF EMERGENCE',
             fontsize=32, fontweight='bold', color='#ffd700', y=0.98)
fig.text(0.5, 0.965,
         'A structural morphology map of 20 computational substrates across 7 complexity features',
         fontsize=14, color='#888888', ha='center')

gs = gridspec.GridSpec(4, 4, hspace=0.35, wspace=0.35,
                       left=0.04, right=0.96, top=0.94, bottom=0.04)

# Panel A
ax1 = fig.add_subplot(gs[0, 0:2])
ax1.set_facecolor('#0d0d0d')
for x in np.arange(-4, 5, 1):
    ax1.axvline(x, color='#1a1a1a', linewidth=0.5)
for y in np.arange(-4, 5, 1):
    ax1.axhline(y, color='#1a1a1a', linewidth=0.5)

ideal_pca_proj = np.array([2.0, 0.3])
ax1.scatter(ideal_pca_proj[0], ideal_pca_proj[1], c='#ffd700', s=400,
           marker='*', edgecolors='white', linewidth=2, zorder=10,
           label='Ideal Emergence')

for i in range(len(names)):
    ax1.plot([ideal_pca_proj[0], X_pca[i, 0]],
             [ideal_pca_proj[1], X_pca[i, 1]],
             color='#ffd700', alpha=0.06, linewidth=0.5, zorder=0)

for i in range(len(names)):
    dist_val = ideal_dist.get(names[i], 3.0)
    size = 100 + (1 - dist_val / 6) * 300
    alpha = 0.4 + (1 - dist_val / 6) * 0.6
    ax1.scatter(X_pca[i, 0], X_pca[i, 1], c=colors_list[i], s=size,
               alpha=alpha, edgecolors='white', linewidth=0.8, zorder=3)
    ax1.annotate(names[i], (X_pca[i, 0], X_pca[i, 1]),
                fontsize=6.5, color='white', alpha=0.8,
                xytext=(5, 5), textcoords='offset points', zorder=4)

D = np.array(data['D'])
for i in range(len(names)):
    dists_i = D[i].copy()
    dists_i[i] = np.inf
    j = np.argmin(dists_i)
    if i < j:
        ax1.plot([X_pca[i, 0], X_pca[j, 0]], [X_pca[i, 1], X_pca[j, 1]],
                color='#ffffff', alpha=0.15, linewidth=1, zorder=1)

ax1.set_xlabel('PC1 (' + pc1_pct + '% variance) - Regularity to Chaos',
               fontsize=10, color='white')
ax1.set_ylabel('PC2 (' + pc2_pct + '% variance) - Information x Dimension',
               fontsize=10, color='white')
ax1.set_title('A. Master Morphospace (PCA)', fontsize=14, color='white',
              fontweight='bold', pad=10)
ax1.tick_params(colors='#666666')
ax1.spines[:].set_color('#333333')
ax1.legend(fontsize=8, loc='upper right', facecolor='#1a1a1a',
          edgecolor='#333333', labelcolor='white')
ax1.set_xlim(-3.5, 3.5)
ax1.set_ylim(-3, 3)

# Panel B
ax2 = fig.add_subplot(gs[0, 2:4])
ax2.set_facecolor('#0d0d0d')

for t, indices in type_groups.items():
    if len(indices) >= 3:
        points = X_pca[indices]
        try:
            hull = ConvexHull(points)
            for simplex in hull.simplices:
                ax2.plot(points[simplex, 0], points[simplex, 1],
                        color=type_colors.get(t, '#888888'), alpha=0.3, linewidth=2)
            hull_points = points[hull.vertices]
            polygon = Polygon(hull_points, alpha=0.1,
                            facecolor=type_colors.get(t, '#888888'))
            ax2.add_patch(polygon)
        except Exception:
            pass

for i in range(len(names)):
    t = types[i]
    c = type_colors.get(t, '#888888')
    ax2.scatter(X_pca[i, 0], X_pca[i, 1], c=c, s=120,
               alpha=0.8, edgecolors='white', linewidth=0.8, zorder=3)
    ax2.annotate(names[i], (X_pca[i, 0], X_pca[i, 1]),
                fontsize=6, color='white', alpha=0.75,
                xytext=(5, 5), textcoords='offset points')

for t, c in type_colors.items():
    if t in type_groups:
        ax2.scatter([], [], c=c, s=80, label=t + ' (' + str(len(type_groups[t])) + ')')
ax2.legend(fontsize=7, loc='upper left', facecolor='#1a1a1a',
          edgecolor='#333333', labelcolor='white', ncol=2)
ax2.set_xlabel('PC1 (' + pc1_pct + '%)', fontsize=10, color='white')
ax2.set_ylabel('PC2 (' + pc2_pct + '%)', fontsize=10, color='white')
ax2.set_title('B. Substrate Type Clusters', fontsize=14, color='white',
              fontweight='bold', pad=10)
ax2.tick_params(colors='#666666')
ax2.spines[:].set_color('#333333')
ax2.set_xlim(-3.5, 3.5)
ax2.set_ylim(-3, 3)

# Panel C
ax3 = fig.add_subplot(gs[1, 0:2])
ax3.set_facecolor('#0d0d0d')
sorted_names = sorted(complexity.keys(), key=lambda x: complexity[x], reverse=True)
sorted_vals = [complexity[n] for n in sorted_names]
sorted_colors = [colors_list[names.index(n)] for n in sorted_names]
ax3.barh(range(len(sorted_names)), sorted_vals, color=sorted_colors,
        edgecolor='white', linewidth=0.5, height=0.7)
ax3.set_yticks(range(len(sorted_names)))
ax3.set_yticklabels(sorted_names, fontsize=7, color='white')
ax3.set_xlabel('Morphological Complexity Index', fontsize=10, color='white')
ax3.set_title('C. Morphological Complexity Ranking', fontsize=14, color='white',
              fontweight='bold', pad=10)
ax3.tick_params(colors='#666666')
ax3.spines[:].set_color('#333333')
ax3.invert_yaxis()
for i, (name, val) in enumerate(zip(sorted_names, sorted_vals)):
    ax3.text(val + 0.01, i, '%.3f' % val, fontsize=6, color='#ffd700', va='center')

# Panel D
ax4 = fig.add_subplot(gs[1, 2:4])
ax4.set_facecolor('#0d0d0d')
cmap_div = LinearSegmentedColormap.from_list('diverging',
    [(0, '#3498db'), (0.5, '#0d0d0d'), (1, '#e74c3c')])
im = ax4.imshow(corr, cmap=cmap_div, vmin=-1, vmax=1, interpolation='nearest')
ax4.set_xticks(range(7))
ax4.set_xticklabels(short_names, rotation=45, ha='right', fontsize=8, color='white')
ax4.set_yticks(range(7))
ax4.set_yticklabels(short_names, fontsize=8, color='white')
for i in range(7):
    for j in range(7):
        val = corr[i, j]
        color = 'white' if abs(val) > 0.4 else '#666666'
        ax4.text(j, i, '%.2f' % val, fontsize=7, color=color,
                ha='center', va='center')
for i in range(7):
    for j in range(i+1, 7):
        if corr[i, j] < -0.4:
            ax4.add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1,
                          fill=False, edgecolor='#ffd700', linewidth=2))
ax4.set_title('D. Feature Correlation Matrix (Exclusions Highlighted)',
              fontsize=14, color='white', fontweight='bold', pad=10)
plt.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)

# Panel E
ax5 = fig.add_subplot(gs[2, 0])
ax5.set_facecolor('#0d0d0d')
transitions = [
    ('Kuramoto sync', 'Kuramoto chimera', '#3498db', '#e74c3c'),
    ('Std Map K=0.5', 'Std Map K=5', '#9b59b6', '#e74c3c'),
]
ax5.set_xlim(0, 10)
ax5.set_ylim(0, 6)
ax5.set_title('E. Morphological Transitions', fontsize=14, color='white',
              fontweight='bold', pad=10)
for idx, (name1, name2, c1, c2) in enumerate(transitions):
    y = 4.5 - idx * 3.5
    ax5.add_patch(FancyBboxPatch((0.5, y-0.8), 3.5, 1.6,
                 boxstyle='round,pad=0.1', facecolor=c1, alpha=0.3,
                 edgecolor=c1, linewidth=2))
    ax5.text(2.25, y, name1, fontsize=9, color='white', ha='center', va='center')
    ax5.annotate('', xy=(6.5, y), xytext=(4.2, y),
                arrowprops=dict(arrowstyle='->', color='#ffd700', lw=2))
    ax5.add_patch(FancyBboxPatch((6.5, y-0.8), 3, 1.6,
                 boxstyle='round,pad=0.1', facecolor=c2, alpha=0.3,
                 edgecolor=c2, linewidth=2))
    ax5.text(8, y, name2, fontsize=9, color='white', ha='center', va='center')
ax5.axis('off')

# Panel F
ax6 = fig.add_subplot(gs[2, 1:3])
ax6.set_facecolor('#0d0d0d')
X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)
order = np.argsort(X_pca[:, 0])
X_ordered = X_norm[order]
names_ordered = [names[i] for i in order]
im = ax6.imshow(X_ordered.T, aspect='auto', cmap='magma', interpolation='nearest')
ax6.set_yticks(range(7))
ax6.set_yticklabels(short_names, fontsize=8, color='white')
ax6.set_xticks(range(len(names)))
clean_names = [n.replace(chr(10), ' ') for n in names_ordered]
ax6.set_xticklabels(clean_names, rotation=90, fontsize=6, color='white')
ax6.set_title('F. Feature Matrix (Sorted by PC1)', fontsize=14, color='white',
              fontweight='bold', pad=10)
plt.colorbar(im, ax=ax6, fraction=0.046, pad=0.04)

# Panel G
ax7 = fig.add_subplot(gs[2, 3])
ax7.set_facecolor('#0d0d0d')
ideal_sorted = sorted(ideal_dist.items(), key=lambda x: x[1])
ideal_names_list = [x[0] for x in ideal_sorted]
ideal_vals = [x[1] for x in ideal_sorted]
cmap_ryg = plt.cm.RdYlGn_r
norm = plt.Normalize(min(ideal_vals), max(ideal_vals))
ax7.barh(range(len(ideal_names_list)), ideal_vals,
        color=[cmap_ryg(norm(v)) for v in ideal_vals],
        edgecolor='white', linewidth=0.5, height=0.7)
ax7.set_yticks(range(len(ideal_names_list)))
ax7.set_yticklabels(ideal_names_list, fontsize=7, color='white')
ax7.set_xlabel('Distance to Ideal Emergence', fontsize=10, color='white')
ax7.set_title('G. Distance to Ideal Emergence', fontsize=14, color='white',
              fontweight='bold', pad=10)
ax7.tick_params(colors='#666666')
ax7.spines[:].set_color('#333333')
ax7.invert_yaxis()

# Panel H
ax8 = fig.add_subplot(gs[3, :])
ax8.set_facecolor('#0d0d0d')
ax8.axis('off')
ax8.text(0.5, 0.95, 'KEY DISCOVERIES', fontsize=20, color='#ffd700',
        ha='center', va='top', transform=ax8.transAxes, fontweight='bold')
insights = [
    '1. UNIVERSAL EDGE OF CHAOS: Gray-Scott (PDE) and Game of Life (CA) are morphologically near-identical, despite fundamentally different substrates.',
    '2. ODE ATTRACTOR CLUSTER: Thomas, Aizawa, and Chua form the tightest cluster, sharing a universal weakly chaotic attractor morphology.',
    '3. TEMPORAL MEMORY GAP: The biggest universal gap is temporal memory - no substrate fully achieves the ideal memory depth.',
    '4. CHIMERA STATE BRIDGE: Kuramoto chimera sits between sync and chaos, bridging two traditionally opposed regimes.',
    '5. EVOLUTIONARY CONVERGENCE: NoiseGarden variants are closest to ideal emergence, suggesting evolutionary optimization approaches optimal complexity.',
    '6. EXCLUSION PRINCIPLE: Lyapunov exponent and temporal memory are anti-correlated (r=-0.63) - chaos destroys memory, order preserves it.',
]
for i, insight in enumerate(insights):
    y_pos = 0.82 - i * 0.12
    color = '#1abc9c' if i % 2 == 0 else '#3498db'
    ax8.text(0.05, y_pos, insight, fontsize=10, color=color,
            transform=ax8.transAxes, va='top', fontfamily='monospace')

fig.savefig('morphospace_atlas.png', dpi=150, facecolor='#0a0a0a')
print('Atlas saved to morphospace_atlas.png')
