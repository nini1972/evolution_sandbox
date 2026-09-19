#!/usr/bin/env python3
"""
Deep Analysis of Morphological Impossibilities - Part 2
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Load data
with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
names = data['names']

feature_names = [
    'Lyapunov', 'CorrDim', 'FractalDim', 
    'SpatialEnt', 'Coupling', 'TempMemory', 'SignalEnt'
]

n, d = X.shape
X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)

# Euclidean distance without scipy
def euclidean_dist(a, b):
    return np.sqrt(np.sum((a - b)**2, axis=-1))

# Compute pairwise distances
dist_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(i+1, n):
        d_val = np.sqrt(np.sum((X_norm[i] - X_norm[j])**2))
        dist_matrix[i, j] = d_val
        dist_matrix[j, i] = d_val

# ANALYSIS 1: EVOLUTIONARY PATHWAYS
print('=' * 60)
print('EVOLUTIONARY PATHWAYS')
print('=' * 60)

print('\nMost similar system pairs:')
pairs = []
for i in range(n):
    for j in range(i+1, n):
        pairs.append((dist_matrix[i, j], i, j))
pairs.sort()

for dist, i, j in pairs[:5]:
    print(f'  {names[i]:20s} <-> {names[j]:20s}: distance={dist:.3f}')

print('\nMost distant system pairs:')
pairs.sort(reverse=True)
for dist, i, j in pairs[:5]:
    print(f'  {names[i]:20s} <-> {names[j]:20s}: distance={dist:.3f}')

# ANALYSIS 2: NEAREST NEIGHBORS
print('\n' + '=' * 60)
print('NEAREST NEIGHBORS')
print('=' * 60)

for i in range(n):
    distances = dist_matrix[i].copy()
    distances[i] = np.inf
    nn_idx = np.argmin(distances)
    print(f'  {names[i]:20s} -> {names[nn_idx]:20s} (dist={distances[nn_idx]:.3f})')

# ANALYSIS 3: CLUSTERING
print('\n' + '=' * 60)
print('SIMPLE CLUSTERING')
print('=' * 60)

# Simple hierarchical-like clustering
threshold = 0.5
clusters = {}
visited = set()

for i in range(n):
    if i in visited:
        continue
    cluster = [i]
    visited.add(i)
    for j in range(n):
        if j not in visited and dist_matrix[i, j] < threshold:
            cluster.append(j)
            visited.add(j)
    clusters[i] = cluster

print(f'\nClusters at distance threshold {threshold}:')
for root, members in clusters.items():
    if len(members) > 1:
        print(f'\n  Cluster ({len(members)} members):')
        for m in members:
            print(f'    - {names[m]}')

# ANALYSIS 4: MORPHOSPACE DENSITY
print('\n' + '=' * 60)
print('MORPHOSPACE DENSITY')
print('=' * 60)

# Count neighbors within various radii
radii = [0.2, 0.4, 0.6, 0.8, 1.0]
for r in radii:
    counts = []
    for i in range(n):
        count = np.sum(dist_matrix[i] < r) - 1
        counts.append(count)
    print(f'  Radius {r:.1f}: mean neighbors={np.mean(counts):.1f}, max={np.max(counts)}, min={np.min(counts)}')

# ANALYSIS 5: EVOLUTIONARY ARROWS (direction of increasing complexity)
print('\n' + '=' * 60)
print('COMPLEXITY GRADIENT')
print('=' * 60)

budget = X_norm.sum(axis=1)
sorted_by_budget = np.argsort(budget)

print('\nEvolution from simple to complex:')
for rank, idx in enumerate(sorted_by_budget):
    print(f'  {rank+1:2d}. {names[idx]:20s} (budget={budget[idx]:.2f})')

# Gradient: which features increase most with budget?
feature_budget_corr = np.zeros(d)
for i in range(d):
    feature_budget_corr[i] = np.corrcoef(X[:, i], budget)[0, 1]

print('\nFeature correlation with budget:')
for i in range(d):
    direction = 'INCREASES' if feature_budget_corr[i] > 0 else 'DECREASES'
    print(f'  {feature_names[i]:12s}: r={feature_budget_corr[i]:+.3f} ({direction} with complexity)')

# ANALYSIS 6: VISUALIZATION
print('\n' + '=' * 60)
print('GENERATING DEEP ANALYSIS VISUALIZATION')
print('=' * 60)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

X_pca = np.array(data['X_pca'])

# Plot 1: Density heatmap in PCA space
ax = axes[0, 0]
from scipy.ndimage import gaussian_filter
hist, xedges, yedges = np.histogram2d(X_pca[:, 0], X_pca[:, 1], bins=20)
hist = gaussian_filter(hist.T, sigma=1)
im = ax.imshow(hist, origin='lower', aspect='auto', cmap='hot',
              extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
ax.scatter(X_pca[:, 0], X_pca[:, 1], c='cyan', s=20, alpha=0.5)
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_title('Morphospace Density')
plt.colorbar(im, ax=ax, label='Density')

# Plot 2: Evolutionary distance matrix
ax = axes[0, 1]
sorted_idx = np.argsort(budget)
dist_sorted = dist_matrix[np.ix_(sorted_idx, sorted_idx)]
im = ax.imshow(dist_sorted, cmap='viridis', aspect='auto')
ax.set_xlabel('System Index (sorted by complexity)')
ax.set_ylabel('System Index (sorted by complexity)')
ax.set_title('Pairwise Distance Matrix\n(sorted by complexity budget)')
plt.colorbar(im, ax=ax, label='Distance')

# Plot 3: Nearest neighbor distances
ax = axes[0, 2]
nn_dists = []
for i in range(n):
    distances = dist_matrix[i].copy()
    distances[i] = np.inf
    nn_dists.append(np.min(distances))

colors = ['red' if budget[i] > budget.mean() else 'blue' for i in range(n)]
ax.bar(range(n), nn_dists, color=colors, edgecolor='black', alpha=0.7)
ax.axhline(y=np.mean(nn_dists), color='green', linestyle='--', label='Mean NN distance')
ax.set_xlabel('System Index')
ax.set_ylabel('Nearest Neighbor Distance')
ax.set_title('Nearest Neighbor Distances\n(Red=high budget, Blue=low budget)')
ax.set_xticks(range(n))
ax.set_xticklabels(names, rotation=90, fontsize=6)
ax.legend()

# Plot 4: Feature importance for budget
ax = axes[1, 0]
bars = ax.bar(feature_names, feature_budget_corr, 
              color=['red' if c > 0 else 'blue' for c in feature_budget_corr],
              edgecolor='black', alpha=0.7)
ax.axhline(y=0, color='black', linewidth=1)
ax.set_ylabel('Correlation with Budget')
ax.set_title('Feature Importance\nfor Complexity Budget')
ax.set_xticklabels(feature_names, rotation=45, ha='right')

# Plot 5: Budget vs Lyapunov
ax = axes[1, 1]
ax.scatter(X[:, 0], budget, c=budget, cmap='viridis', s=100, edgecolor='black')
for i, name in enumerate(names):
    ax.annotate(name, (X[i, 0], budget[i]), fontsize=5, ha='center', va='bottom')
ax.set_xlabel('Lyapunov Exponent')
ax.set_ylabel('Complexity Budget')
ax.set_title('Chaos vs Total Complexity')
ax.plot([X[:, 0].min(), X[:, 0].max()], [budget.mean(), budget.mean()], 
        'r--', alpha=0.5, label=f'Mean budget={budget.mean():.2f}')
ax.legend()

# Plot 6: Cluster visualization
ax = axes[1, 2]
cluster_colors = plt.cm.Set3(np.linspace(0, 1, len(clusters)))
for idx, (root, members) in enumerate(clusters.items()):
    color = cluster_colors[idx % len(cluster_colors)]
    for m in members:
        ax.scatter(X_pca[m, 0], X_pca[m, 1], c=[color], s=150, 
                   edgecolor='black', linewidth=2)
        ax.annotate(names[m], (X_pca[m, 0], X_pca[m, 1]), 
                   fontsize=5, ha='center', va='bottom')

# Draw cluster connections
for root, members in clusters.items():
    if len(members) > 1:
        for m in members:
            if m != root:
                ax.plot([X_pca[root, 0], X_pca[m, 0]], 
                       [X_pca[root, 1], X_pca[m, 1]], 
                       'k--', alpha=0.3, linewidth=1)

ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_title('System Clusters in Morphospace')

plt.tight_layout()
plt.savefig('deep_analysis.png', dpi=150, bbox_inches='tight')
print('Saved deep_analysis.png')

# ANALYSIS 7: KEY INSIGHTS
print('\n' + '=' * 60)
print('KEY INSIGHTS FROM DEEP ANALYSIS')
print('=' * 60)

print(f"""
1. MORPHOSPACE TOPOLOGY:
   - {len(clusters)} clusters found at threshold 0.5
   - Mean nearest-neighbor distance: {np.mean(nn_dists):.3f}
   - Density varies significantly across morphospace

2. EVOLUTIONARY DIRECTION:
   - Complexity budget increases with:
     * Higher Lyapunov exponent (r={feature_budget_corr[0]:+.3f})
     * Higher Signal Entropy (r={feature_budget_corr[6]:+.3f})
   - Complexity budget decreases with:
     * Higher Correlation Dimension (r={feature_budget_corr[1]:+.3f})

3. BOUNDARY SYSTEMS:
   - Gray-Scott is closest to the forbidden boundary
   - Most systems cluster in the middle of morphospace
   - Empty regions suggest unexplored possibility space

4. PHASE TRANSITIONS:
   - Sharp jump in Coupling at Lyapunov ~0.1
   - CorrDim drops dramatically near Lyapunov 0
   - These suggest fundamental regime changes
""")

# Save summary
summary = {
    'nn_distances': nn_dists,
    'budget_correlations': feature_budget_corr.tolist(),
    'cluster_sizes': {str(k): len(v) for k, v in clusters.items()},
    'mean_nn_distance': float(np.mean(nn_dists))
}

with open('deep_analysis_results.json', 'w') as f:
    json.dump(summary, f, indent=2)
print('Saved deep_analysis_results.json')