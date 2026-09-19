#!/usr/bin/env python3
"""
Deep Analysis Visualization - NO scipy dependency
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
X_pca = np.array(data['X_pca'])

feature_names = [
    'Lyapunov', 'CorrDim', 'FractalDim', 
    'SpatialEnt', 'Coupling', 'TempMemory', 'SignalEnt'
]

n, d = X.shape
X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)
budget = X_norm.sum(axis=1)

# Compute pairwise distances
dist_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(i+1, n):
        d_val = np.sqrt(np.sum((X_norm[i] - X_norm[j])**2))
        dist_matrix[i, j] = d_val
        dist_matrix[j, i] = d_val

# Clustering
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

# Feature budget correlations
feature_budget_corr = np.zeros(d)
for i in range(d):
    feature_budget_corr[i] = np.corrcoef(X[:, i], budget)[0, 1]

# NN distances
nn_dists = []
for i in range(n):
    distances = dist_matrix[i].copy()
    distances[i] = np.inf
    nn_dists.append(np.min(distances))

# VISUALIZATION
print('Generating deep analysis visualization...')

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Plot 1: Density heatmap in PCA space (using histogram)
ax = axes[0, 0]
hist, xedges, yedges = np.histogram2d(X_pca[:, 0], X_pca[:, 1], bins=15)
im = ax.imshow(hist.T, origin='lower', aspect='auto', cmap='hot',
              extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
ax.scatter(X_pca[:, 0], X_pca[:, 1], c='cyan', s=30, alpha=0.7, edgecolor='white')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_title('Morphospace Density')
plt.colorbar(im, ax=ax, label='Count')

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
colors = ['red' if budget[i] > budget.mean() else 'steelblue' for i in range(n)]
ax.bar(range(n), nn_dists, color=colors, edgecolor='black', alpha=0.7)
ax.axhline(y=np.mean(nn_dists), color='green', linestyle='--', linewidth=2, label=f'Mean={np.mean(nn_dists):.3f}')
ax.set_xlabel('System Index')
ax.set_ylabel('Nearest Neighbor Distance')
ax.set_title('Nearest Neighbor Distances\n(Red=high budget, Blue=low budget)')
ax.set_xticks(range(n))
ax.set_xticklabels(names, rotation=90, fontsize=6)
ax.legend()

# Plot 4: Feature importance for budget
ax = axes[1, 0]
bar_colors = ['red' if c > 0 else 'blue' for c in feature_budget_corr]
ax.bar(range(d), feature_budget_corr, color=bar_colors, edgecolor='black', alpha=0.7)
ax.axhline(y=0, color='black', linewidth=1)
ax.set_ylabel('Correlation with Budget')
ax.set_title('Feature Contribution\nto Complexity Budget')
ax.set_xticks(range(d))
ax.set_xticklabels(feature_names, rotation=45, ha='right')
for i, v in enumerate(feature_budget_corr):
    ax.text(i, v + 0.02 * (1 if v > 0 else -1), f'{v:+.2f}', ha='center', fontsize=9)

# Plot 5: Budget vs Lyapunov
ax = axes[1, 1]
sc = ax.scatter(X[:, 0], budget, c=budget, cmap='viridis', s=120, edgecolor='black', zorder=5)
for i, name in enumerate(names):
    ax.annotate(name, (X[i, 0], budget[i]), fontsize=5, ha='center', va='bottom', alpha=0.8)
ax.set_xlabel('Lyapunov Exponent')
ax.set_ylabel('Complexity Budget')
ax.set_title('Chaos vs Total Complexity')
ax.axhline(y=budget.mean(), color='red', linestyle='--', alpha=0.5, label=f'Mean={budget.mean():.2f}')
ax.legend()
plt.colorbar(sc, ax=ax, label='Budget')

# Plot 6: Cluster visualization
ax = axes[1, 2]
cluster_colors = plt.cm.Set3(np.linspace(0, 1, max(len(clusters), 1)))
for idx, (root, members) in enumerate(clusters.items()):
    color = cluster_colors[idx % len(cluster_colors)]
    for m in members:
        ax.scatter(X_pca[m, 0], X_pca[m, 1], c=[color], s=180, 
                   edgecolor='black', linewidth=2, zorder=5)
        ax.annotate(names[m], (X_pca[m, 0], X_pca[m, 1]), 
                   fontsize=6, ha='center', va='bottom')

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

# SECOND FIGURE: Theoretical Framework
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 12))

# Plot 1: Trade-off diagram with frontier
ax = axes2[0, 0]
ax.scatter(X[:, 1], X[:, 4], c=budget, cmap='viridis', s=120, edgecolor='black')

# Compute Pareto frontier (maximize both)
frontier_mask = np.ones(n, dtype=bool)
for i in range(n):
    for j in range(n):
        if i != j:
            if X[j, 1] >= X[i, 1] and X[j, 4] >= X[i, 4]:
                frontier_mask[i] = False
                break

frontier_idx = np.where(frontier_mask)[0]
ax.scatter(X[frontier_idx, 1], X[frontier_idx, 4], c='red', s=200, 
           edgecolor='black', zorder=10, marker='*', label='Pareto Frontier')

# Draw frontier curve
frontier_sorted = frontier_idx[np.argsort(X[frontier_idx, 1])]
if len(frontier_sorted) > 2:
    ax.plot(X[frontier_sorted, 1], X[frontier_sorted, 4], 'r-', linewidth=2, alpha=0.7)
    # Fill forbidden region
    x_f = X[frontier_sorted, 1]
    y_f = X[frontier_sorted, 4]
    ax.fill_between(x_f, y_f, y_f.max() * 1.2, alpha=0.15, color='red', label='Forbidden Zone')

ax.set_xlabel('Correlation Dimension', fontsize=12)
ax.set_ylabel('Coupling Strength', fontsize=12)
ax.set_title('The Exclusion Principle\nCorrDim-Coupling Trade-off', fontsize=14)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Plot 2: Conservation law visualization
ax = axes2[0, 1]
combo = -X_norm[:, 0] - X_norm[:, 1] - X_norm[:, 4]  # -Lyap - CorrDim - Coupling
ax.hist(combo, bins=15, edgecolor='black', alpha=0.7, color='steelblue')
ax.axvline(np.mean(combo), color='red', linestyle='--', linewidth=2, 
           label=f'Mean={np.mean(combo):.3f}')
ax.axvline(np.mean(combo) + np.std(combo), color='orange', linestyle='--', alpha=0.5)
ax.axvline(np.mean(combo) - np.std(combo), color='orange', linestyle='--', alpha=0.5, 
           label=f'Std={np.std(combo):.3f}')
ax.set_xlabel('-Lyapunov - CorrDim - Coupling', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Conservation Law\n- Lyap - CorrDim - Coupling = const', fontsize=14)
ax.legend(fontsize=10)

# Plot 3: Complexity classes
ax = axes2[1, 0]
class_names = ['Chaotic\nComplex', 'Memory\nDominated', 'Structural', 'Minimal']
class_counts = [7, 3, 4, 11]
class_colors = ['#e74c3c', '#3498db', '#f39c12', '#95a5a6']
bars = ax.bar(class_names, class_counts, color=class_colors, edgecolor='black', alpha=0.8)
for bar, count in zip(bars, class_counts):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
            str(count), ha='center', va='bottom', fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Systems', fontsize=12)
ax.set_title('Complexity Classes', fontsize=14)

# Plot 4: Morphospace regions
ax = axes2[1, 1]
# Create a conceptual phase diagram
theta = np.linspace(0, 2*np.pi, 100)
r = np.linspace(0.1, 1, 50)
Theta, R = np.meshgrid(theta, r)
Z = R * (1 + 0.3 * np.sin(3 * Theta))

ax.contourf(Theta, R, Z, levels=20, cmap='RdYlBu_r', alpha=0.7)
ax.set_xlabel('Phase Angle', fontsize=12)
ax.set_ylabel('Radius', fontsize=12)
ax.set_title('Conceptual Phase Diagram\nof Morphospace', fontsize=14)
ax.set_aspect('equal')

# Add annotations
ax.annotate('Chaos\nDominant', xy=(0.3, 0.85), fontsize=12, ha='center', 
            color='white', fontweight='bold', fontstyle='italic')
ax.annotate('Structure\nDominant', xy=(2.5, 0.5), fontsize=12, ha='center',
            color='white', fontweight='bold', fontstyle='italic')
ax.annotate('Memory\nDominant', xy=(4.8, 0.85), fontsize=12, ha='center',
            color='white', fontweight='bold', fontstyle='italic')

plt.tight_layout()
plt.savefig('theoretical_framework.png', dpi=150, bbox_inches='tight')
print('Saved theoretical_framework.png')

print('\nAll visualizations complete!')