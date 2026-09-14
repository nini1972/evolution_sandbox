#!/usr/bin/env python3
"""
Deep Analysis of Computational Morphospace
- Phase transition detection
- Cluster analysis (simple k-means-like)
- Invariant discovery
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import warnings
warnings.filterwarnings('ignore')

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

feature_names = ['Lyapunov', 'Correlation Dim', 'Fractal Dim',
                 'Spatial Entropy', 'Sync Order', 'Memory Depth', 'Temporal Entropy']

# Standardize
X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X_std[X_std == 0] = 1
X_scaled = (X - X_mean) / X_std

print("=" * 70)
print("DEEP MORPHOSPACE ANALYSIS")
print("=" * 70)

# ──────────────────────────────────────────────
# 1. PCA Variance
# ──────────────────────────────────────────────
print("\n1. PCA VARIANCE ANALYSIS")
print("-" * 40)
total_var = sum(eigenvalues)
cumvar = 0
for i, ev in enumerate(eigenvalues):
    cumvar += ev
    print(f"  PC{i+1}: {ev:8.4f}  ({ev/total_var*100:5.1f}%)  cumulative {cumvar/total_var*100:5.1f}%")

# ──────────────────────────────────────────────
# 2. Simple agglomerative cluster (nearest-centroid, 3 clusters)
# ──────────────────────────────────────────────
print("\n2. CLUSTER ANALYSIS (3 natural groups)")
print("-" * 40)

# Use the 3 largest eigenvalue eigenvectors for a 3-cluster assignment
# Project onto first 3 PCs for better separation
W3 = eigenvectors[:3].T  # (7, 3)
Z = X_scaled @ W3  # (20, 3)

# Simple k-means with 3 clusters
np.random.seed(42)
K = 3
centroids = Z[[0, 7, 13]].copy()  # seed: Lorenz, Kuramoto-sync, StdMap-K5
for _ in range(100):
    dists = np.sqrt(((Z[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2))
    labels = dists.argmin(axis=1)
    for k in range(K):
        mask = labels == k
        if mask.any():
            centroids[k] = Z[mask].mean(axis=0)

for k in range(K):
    members = [names[i] for i in range(len(names)) if labels[i] == k]
    mean_nd = np.mean(norm_dist[labels == k])
    print(f"\n  Cluster {k} ({len(members)} systems, mean ideal-distance={mean_nd:.3f}):")
    for m in members:
        print(f"    · {m}")

# ──────────────────────────────────────────────
# 3. Feature Correlations / Exclusion
# ──────────────────────────────────────────────
print("\n3. MORPHOLOGICAL EXCLUSION PRINCIPLES")
print("-" * 40)

corr_matrix = np.corrcoef(X.T)

print("\n  Significant feature correlations (|r| > 0.45):")
exclusion_pairs = []
for i in range(len(feature_names)):
    for j in range(i + 1, len(feature_names)):
        r = corr_matrix[i, j]
        if abs(r) > 0.45:
            direction = "positive" if r > 0 else "negative"
            strength = "STRONG" if abs(r) > 0.65 else "moderate"
            print(f"    {feature_names[i]:18s} <-> {feature_names[j]:18s}  r = {r:+.3f}  ({direction}, {strength})")
            if r < -0.5:
                exclusion_pairs.append((feature_names[i], feature_names[j], r))

if exclusion_pairs:
    print("\n  Exclusion pairs (anti-correlated features that cannot coexist):")
    for a, b, r in exclusion_pairs:
        print(f"    ⚡ {a} and {b} (r = {r:.3f}): systems high in one tend to be low in the other")

# ──────────────────────────────────────────────
# 4. Pairwise Distance Analysis
# ──────────────────────────────────────────────
print("\n4. PAIRWISE DISTANCE ANALYSIS")
print("-" * 40)

D_upper = D[np.triu_indices_from(D, k=1)]
print(f"  Total unique pairs: {len(D_upper)}")
print(f"  Mean distance: {np.mean(D_upper):.3f}")
print(f"  Std distance:  {np.std(D_upper):.3f}")
print(f"  Min distance:  {np.min(D_upper):.3f}")
print(f"  Max distance:  {np.max(D_upper):.3f}")

# Find closest pairs
print("\n  Closest pairs (nearest neighbors):")
for i in range(len(names)):
    row = D[i].copy()
    row[i] = np.inf
    nearest = np.argmin(row)
    print(f"    {names[i]:30s} <-> {names[nearest]:30s}  d={D[i, nearest]:.3f}")

# Find most isolated systems
print("\n  Most isolated systems (highest mean distance):")
mean_dists = D.mean(axis=1)
most_isolated = np.argsort(mean_dists)[::-1]
for idx in most_isolated[:5]:
    print(f"    {names[idx]:30s}  mean_d={mean_dists[idx]:.3f}")

# ──────────────────────────────────────────────
# 5. Closest to Ideal Emergence
# ──────────────────────────────────────────────
print("\n5. SYSTEMS CLOSEST TO IDEAL EMERGENCE")
print("-" * 40)
print(f"  {'Rank':>4s}  {'System':30s}  {'Distance':>10s}  {'Regime':20s}")
print(f"  {'─'*4}  {'─'*30}  {'─'*10}  {'─'*20}")
sorted_idx = np.argsort(norm_dist)
for rank, idx in enumerate(sorted_idx, 1):
    marker = " ◄ CLOSEST" if rank == 1 else ""
    print(f"  {rank:4d}  {names[idx]:30s}  {norm_dist[idx]:10.4f}  {regimes[idx]:20s}{marker}")

# ──────────────────────────────────────────────
# 6. Substrate Type Analysis
# ──────────────────────────────────────────────
print("\n6. SUBSTRATE TYPE ANALYSIS")
print("-" * 40)

unique_types = sorted(set(types))
print(f"  {'Type':15s}  {'Count':>5s}  {'Mean Dist':>10s}  {'Members'}")
for t in unique_types:
    type_idx = [i for i, tp in enumerate(types) if tp == t]
    mean_dist = np.mean(norm_dist[type_idx])
    member_list = ', '.join([names[i].split('(')[0].strip() for i in type_idx])
    print(f"  {t:15s}  {len(type_idx):5d}  {mean_dist:10.3f}  {member_list}")

# ──────────────────────────────────────────────
# 7. Invariant Relationships
# ──────────────────────────────────────────────
print("\n7. INVARIANT RELATIONSHIPS (R² > 0.5)")
print("-" * 40)

for i in range(len(feature_names)):
    for j in range(i + 1, len(feature_names)):
        coeffs = np.polyfit(X[:, i], X[:, j], 1)
        residuals = X[:, j] - np.polyval(coeffs, X[:, i])
        r_squared = 1 - np.sum(residuals**2) / np.sum((X[:, j] - np.mean(X[:, j]))**2)

        if r_squared > 0.5:
            print(f"  {feature_names[j]} = {coeffs[0]:+.3f} × {feature_names[i]} + ({coeffs[1]:+.3f})   R² = {r_squared:.3f}")

# ──────────────────────────────────────────────
# 8. Gap / Phase Boundary Analysis
# ──────────────────────────────────────────────
print("\n8. PHASE BOUNDARY ANALYSIS")
print("-" * 40)

D_sorted = np.sort(D_upper)
gaps = np.diff(D_sorted)
mean_gap = np.mean(gaps)
std_gap = np.std(gaps)
threshold = mean_gap + 1.5 * std_gap

print(f"  Mean gap between sorted distances: {mean_gap:.3f}")
print(f"  Std gap: {std_gap:.3f}")
print(f"  Threshold (mean + 1.5σ): {threshold:.3f}")

big_gap_count = np.sum(gaps > threshold)
print(f"  Significant gaps found: {big_gap_count}")

if big_gap_count > 0:
    gap_pos = np.where(gaps > threshold)[0]
    for gp in gap_pos:
        d_before = D_sorted[gp]
        d_after = D_sorted[gp + 1]
        print(f"    Gap at distance {d_before:.3f} → {d_after:.3f} (size={d_after-d_before:.3f})")

# ──────────────────────────────────────────────
# 9. Morphospace Topology
# ──────────────────────────────────────────────
print("\n9. MORPHOSPACE TOPOLOGY SUMMARY")
print("-" * 40)
print(f"  Dimensionality: {len(feature_names)} features")
print(f"  Effective dimensionality (PCs > 1 eigenvalue): {sum(eigenvalues > 1)}")
print(f"  Systems mapped: {len(names)}")
print(f"  Substrate types: {len(unique_types)}")
print(f"  Clusters found: {K}")
print(f"  Closest to ideal: {names[sorted_idx[0]]} (d={norm_dist[sorted_idx[0]]:.4f})")
print(f"  Farthest from ideal: {names[sorted_idx[-1]]} (d={norm_dist[sorted_idx[-1]]:.4f})")
print(f"  Most isolated: {names[most_isolated[0]]} (mean_d={mean_dists[most_isolated[0]]:.3f})")

# ──────────────────────────────────────────────
# VISUALIZATION
# ──────────────────────────────────────────────
fig = plt.figure(figsize=(24, 18))
fig.suptitle('Computational Morphospace: Deep Analysis', fontsize=16, fontweight='bold')

# Panel 1: PCA projection with cluster coloring
ax1 = plt.subplot(241)
cluster_colors = ['#e74c3c', '#3498db', '#2ecc71']
for k in range(K):
    mask = labels == k
    ax1.scatter(X_pca[mask, 0], X_pca[mask, 1], s=120, c=cluster_colors[k],
                edgecolor='black', linewidth=0.8, label=f'Cluster {k}', zorder=5)
for i, name in enumerate(names):
    short = name.split('(')[0].strip()[:12]
    ax1.annotate(short, (X_pca[i, 0], X_pca[i, 1]), fontsize=5.5,
                 ha='center', va='bottom', xytext=(0, 4), textcoords='offset points')
ax1.set_xlabel(f'PC1 ({eigenvalues[0]/total_var*100:.0f}%)')
ax1.set_ylabel(f'PC2 ({eigenvalues[1]/total_var*100:.0f}%)')
ax1.set_title('PCA Morphospace with Clusters')
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=8)

# Panel 2: MDS projection
ax2 = plt.subplot(242)
for i, (x, y) in enumerate(X_mds):
    ax2.scatter(x, y, s=120, c=colors[i], edgecolor='black', linewidth=0.8, zorder=5)
    short = names[i].split('(')[0].strip()[:12]
    ax2.annotate(short, (x, y), fontsize=5.5, ha='center', va='bottom',
                 xytext=(0, 4), textcoords='offset points')
ax2.set_xlabel('MDS Dimension 1')
ax2.set_ylabel('MDS Dimension 2')
ax2.set_title('MDS Morphospace (Distance-Preserving)')
ax2.grid(True, alpha=0.3)

# Panel 3: Distance heatmap with clustering order
ax3 = plt.subplot(243)
sort_order = np.argsort(labels * 100 + norm_dist)
D_sorted_mat = D[sort_order][:, sort_order]
im = ax3.imshow(D_sorted_mat, cmap='viridis', interpolation='nearest')
plt.colorbar(im, ax=ax3, label='Distance')
sorted_names = [names[i] for i in sort_order]
ax3.set_xticks(range(len(sorted_names)))
ax3.set_yticks(range(len(sorted_names)))
ax3.set_xticklabels(sorted_names, rotation=90, fontsize=4)
ax3.set_yticklabels(sorted_names, fontsize=4)
ax3.set_title('Distance Matrix (Clustered Order)')

# Panel 4: Correlation matrix
ax4 = plt.subplot(244)
im = ax4.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
plt.colorbar(im, ax=ax4, label='Correlation')
ax4.set_xticks(range(len(feature_names)))
ax4.set_yticks(range(len(feature_names)))
ax4.set_xticklabels(feature_names, rotation=45, ha='right', fontsize=7)
ax4.set_yticklabels(feature_names, fontsize=7)
ax4.set_title('Feature Correlation Matrix')
for i in range(len(feature_names)):
    for j in range(len(feature_names)):
        ax4.text(j, i, f'{corr_matrix[i, j]:.2f}', ha='center', va='center', fontsize=5.5,
                 color='white' if abs(corr_matrix[i, j]) > 0.5 else 'black')

# Panel 5: Distance distribution with gaps
ax5 = plt.subplot(245)
ax5.hist(D_upper, bins=25, edgecolor='black', alpha=0.7, color='steelblue')
ax5.axvline(x=np.mean(D_upper), color='red', linestyle='--', linewidth=2, label=f'Mean={np.mean(D_upper):.2f}')
ax5.axvline(x=np.mean(D_upper) + 2*np.std(D_upper), color='orange', linestyle='--',
            linewidth=2, label=f'Mean+2σ={np.mean(D_upper)+2*np.std(D_upper):.2f}')
ax5.set_xlabel('Pairwise Distance')
ax5.set_ylabel('Frequency')
ax5.set_title('Pairwise Distance Distribution')
ax5.legend(fontsize=8)

# Panel 6: Substrate type boxplot
ax6 = plt.subplot(246)
type_data = {}
for t in unique_types:
    type_idx = [i for i, tp in enumerate(types) if tp == t]
    type_data[t] = norm_dist[type_idx]
positions = range(len(unique_types))
bp = ax6.boxplot([type_data[t] for t in unique_types], positions=positions, widths=0.6)
ax6.set_xticks(positions)
ax6.set_xticklabels(unique_types, rotation=45, ha='right', fontsize=7)
ax6.set_ylabel('Distance to Ideal')
ax6.set_title('Ideal-Emergence Distance by Type')
ax6.axhline(y=np.mean(norm_dist), color='red', linestyle='--', alpha=0.5, label='Global mean')
ax6.legend(fontsize=8)

# Panel 7: Eigenvalue scree
ax7 = plt.subplot(247)
ax7.bar(range(1, len(eigenvalues)+1), eigenvalues, color='steelblue', edgecolor='black')
ax7.axhline(y=1, color='red', linestyle='--', label='Kaiser criterion (λ=1)')
ax7.set_xlabel('Principal Component')
ax7.set_ylabel('Eigenvalue')
ax7.set_title('PCA Scree Plot')
ax7.set_xticks(range(1, len(eigenvalues)+1))
ax7.legend(fontsize=8)

# Panel 8: Rankings
ax8 = plt.subplot(248)
top_n = 20
sorted_idx_plot = np.argsort(norm_dist)[::-1]
ax8.barh(range(top_n), norm_dist[sorted_idx_plot[:top_n]],
         color=[colors[i] for i in sorted_idx_plot[:top_n]], edgecolor='black', linewidth=0.5)
ax8.set_yticks(range(top_n))
ax8.set_yticklabels([names[i] for i in sorted_idx_plot[:top_n]], fontsize=6)
ax8.set_xlabel('Distance to Ideal Emergence')
ax8.set_title('Rankings (Farthest First)')
ax8.invert_yaxis()

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('morphospace_deep_analysis.png', dpi=150, bbox_inches='tight')
print("\nVisualization saved to morphospace_deep_analysis.png")
print("\n" + "=" * 70)
print("Analysis complete.")
