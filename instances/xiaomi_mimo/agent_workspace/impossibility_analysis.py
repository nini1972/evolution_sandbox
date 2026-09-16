#!/usr/bin/env python3
"""
Theory of Morphological Impossibility - Part 1: Correlation Analysis
Mapping the forbidden regions in complexity feature space
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import json
from scipy import stats

# Load data
with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
names = data['names']
types = data['types']
regimes = data['regimes']

feature_names = [
    'Lyapunov Exponent',
    'Correlation Dimension', 
    'Fractal Dimension',
    'Spatial Entropy',
    'Coupling Strength',
    'Temporal Memory',
    'Signal Entropy'
]

n, d = X.shape
print(f"Loaded {n} systems, {d} features")
print(f"Feature names: {feature_names}")

# ============================================================
# PART 1: FEATURE CORRELATIONS
# ============================================================
print("\n=== PART 1: FEATURE CORRELATIONS ===")

# Compute Pearson and Spearman correlations
pearson_r = np.corrcoef(X.T)
spearman_r = np.zeros((d, d))
for i in range(d):
    for j in range(d):
        rho, _ = stats.spearmanr(X[:, i], X[:, j])
        spearman_r[i, j] = rho

# Print strongest anti-correlations
print("\nStrongest Anti-Correlations (Pearson):")
anti_corrs = []
for i in range(d):
    for j in range(i+1, d):
        anti_corrs.append((pearson_r[i, j], i, j))
anti_corrs.sort()
for r, i, j in anti_corrs[:10]:
    print(f"  {feature_names[i]} <-> {feature_names[j]}: r = {r:.3f}")

print("\nStrongest Correlations (Pearson):")
pos_corrs = sorted(anti_corrs, reverse=True)
for r, i, j in pos_corrs[:10]:
    print(f"  {feature_names[i]} <-> {feature_names[j]}: r = {r:.3f}")

# ============================================================
# PART 2: COMPLEXITY BUDGET MODEL
# ============================================================
print("\n=== PART 2: COMPLEXITY BUDGET MODEL ===")

# Normalize features to [0, 1]
X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)

# Compute total complexity budget for each system
budget = X_norm.sum(axis=1)
print(f"\nComplexity Budget Statistics:")
print(f"  Mean: {budget.mean():.2f}")
print(f"  Std:  {budget.std():.2f}")
print(f"  Min:  {budget.min():.2f} ({names[budget.argmin()]})")
print(f"  Max:  {budget.max():.2f} ({names[budget.argmax()]})")

# Check if budget is conserved (constant sum)
print(f"\nBudget Conservation Check:")
print(f"  If perfectly conserved, std/mean would be ~0")
print(f"  Actual CV: {budget.std()/budget.mean():.3f}")

# ============================================================
# PART 3: EXCLUSION ANALYSIS
# ============================================================
print("\n=== PART 3: EXCLUSION ANALYSIS ===")

# For each pair of features, compute the "exclusion index"
# High exclusion = systems that have high values in one feature
# cannot have high values in the other
exclusion_pairs = []
for i in range(d):
    for j in range(i+1, d):
        # Compute how many systems are in the "forbidden quadrant" (both high)
        high_i = X_norm[:, i] > 0.7
        high_j = X_norm[:, j] > 0.7
        both_high = np.sum(high_i & high_j)
        
        # Compute how many systems are in the "allowed quadrant" (one high, one low)
        only_i = np.sum(high_i & (X_norm[:, j] < 0.3))
        only_j = np.sum((X_norm[:, i] < 0.3) & high_j)
        
        # Exclusion index: ratio of forbidden to allowed
        allowed = only_i + only_j + 1  # +1 to avoid div by 0
        exclusion = both_high / allowed
        
        exclusion_pairs.append((exclusion, i, j, both_high, only_i, only_j))

exclusion_pairs.sort(reverse=True)
print("\nMost Excluded Feature Pairs:")
print("  (Exclusion Index, Feature1, Feature2, BothHigh, Only1, Only2)")
for exc, i, j, bh, o1, o2 in exclusion_pairs[:10]:
    print(f"  {exc:.3f}: {feature_names[i]} <-> {feature_names[j]} ({bh} both high, {o1} only {feature_names[i]}, {o2} only {feature_names[j]})")

# ============================================================
# PART 4: FORBIDDEN VOLUME ESTIMATION
# ============================================================
print("\n=== PART 4: FORBIDDEN VOLUME ESTIMATION ===")

# Use PCA to estimate volume fraction occupied
X_pca = np.array(data['X_pca'])
# Add other components if available
if 'X_mds' in data:
    X_mds = np.array(data['X_mds'])

# Compute convex hull in PCA space
from scipy.spatial import ConvexHull
try:
    hull = ConvexHull(X_pca)
    hull_volume = hull.volume
    
    # Estimate total volume of bounding box
    bbox_volume = np.prod(X_pca.max(axis=0) - X_pca.min(axis=0))
    
    # Fill ratio (how much of the bounding box is occupied)
    fill_ratio = hull_volume / bbox_volume
    
    print(f"\nConvex Hull in PCA space:")
    print(f"  Hull volume: {hull_volume:.4f}")
    print(f"  Bounding box volume: {bbox_volume:.4f}")
    print(f"  Fill ratio: {fill_ratio:.4f}")
    print(f"  (Lower fill = more forbidden volume)")
except Exception as e:
    print(f"  Hull computation failed: {e}")

# ============================================================
# PART 5: VISUALIZATION
# ============================================================
print("\n=== PART 5: GENERATING VISUALIZATIONS ===")

fig = plt.figure(figsize=(20, 15))

# Plot 1: Correlation Matrix
ax1 = fig.add_subplot(231)
im = ax1.imshow(pearson_r, cmap='RdBu_r', vmin=-1, vmax=1)
ax1.set_xticks(range(d))
ax1.set_yticks(range(d))
ax1.set_xticklabels([f'F{i}' for i in range(d)], fontsize=8)
ax1.set_yticklabels([f'F{i}' for i in range(d)], fontsize=8)
ax1.set_title('Feature Correlations (Pearson)')
plt.colorbar(im, ax=ax1, shrink=0.8)

# Plot 2: Anti-correlation Network
ax2 = fig.add_subplot(232)
# Draw edges for strong anti-correlations
for r, i, j in anti_corrs[:10]:
    if r < -0.3:
        ax2.plot([i, j], [0, 0], 'r-', linewidth=1+abs(r)*3, alpha=0.7)
for r, i, j in pos_corrs[:10]:
    if r > 0.3:
        ax2.plot([i, j], [1, 1], 'b-', linewidth=1+r*3, alpha=0.7)
ax2.set_xlim(-0.5, d-0.5)
ax2.set_ylim(-0.5, 1.5)
ax2.set_xticks(range(d))
ax2.set_xticklabels([f'F{i}' for i in range(d)], fontsize=8)
ax2.set_yticks([0, 1])
ax2.set_yticklabels(['Anti-corr', 'Corr'])
ax2.set_title('Feature Relationship Network')
ax2.grid(True, alpha=0.3)

# Plot 3: Complexity Budget Distribution
ax3 = fig.add_subplot(233)
ax3.hist(budget, bins=15, edgecolor='black', alpha=0.7)
ax3.axvline(budget.mean(), color='r', linestyle='--', label=f'Mean={budget.mean():.2f}')
ax3.set_xlabel('Complexity Budget (Sum of Normalized Features)')
ax3.set_ylabel('Count')
ax3.set_title('Complexity Budget Distribution')
ax3.legend()

# Plot 4: Exclusion Heatmap
ax4 = fig.add_subplot(234)
exclusion_matrix = np.zeros((d, d))
for exc, i, j, _, _, _ in exclusion_pairs:
    exclusion_matrix[i, j] = exc
    exclusion_matrix[j, i] = exc
im4 = ax4.imshow(exclusion_matrix, cmap='Reds')
ax4.set_xticks(range(d))
ax4.set_yticks(range(d))
ax4.set_xticklabels([f'F{i}' for i in range(d)], fontsize=8)
ax4.set_yticklabels([f'F{i}' for i in range(d)], fontsize=8)
ax4.set_title('Feature Exclusion Index')
plt.colorbar(im4, ax=ax4, shrink=0.8)

# Plot 5: Morphospace with complexity budget coloring
ax5 = fig.add_subplot(235)
scatter = ax5.scatter(X_pca[:, 0], X_pca[:, 1], c=budget, cmap='plasma', 
                      s=100, edgecolor='black', linewidth=0.5)
for i, name in enumerate(names):
    ax5.annotate(name, (X_pca[i, 0], X_pca[i, 1]), fontsize=5, ha='center', va='bottom')
ax5.set_xlabel('PC1')
ax5.set_ylabel('PC2')
ax5.set_title('Morphospace (colored by Complexity Budget)')
plt.colorbar(scatter, ax=ax5, label='Budget')

# Plot 6: Ideal Point and Exclusion Zones
ax6 = fig.add_subplot(236)
ideal = np.array([1.7, 1.8, 1.8, 0.2, 0.5, 2.8, 2.0])
ideal_norm = (ideal - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)

# Compute distance to ideal for each system
dist_ideal = np.sqrt(((X_norm - ideal_norm)**2).sum(axis=1))

# Color by distance to ideal (closer = better)
scatter6 = ax6.scatter(X_pca[:, 0], X_pca[:, 1], c=dist_ideal, cmap='viridis_r',
                       s=100, edgecolor='black', linewidth=0.5)
for i, name in enumerate(names):
    ax6.annotate(name, (X_pca[i, 0], X_pca[i, 1]), fontsize=5, ha='center', va='bottom')
ax6.set_xlabel('PC1')
ax6.set_ylabel('PC2')
ax6.set_title('Morphospace (colored by Distance to Ideal)')
plt.colorbar(scatter6, ax=ax6, label='Distance to Ideal')

plt.tight_layout()
plt.savefig('impossibility_analysis.png', dpi=150, bbox_inches='tight')
print("Saved impossibility_analysis.png")

# ============================================================
# PART 6: SAVE ANALYSIS RESULTS
# ============================================================
analysis_results = {
    'feature_names': feature_names,
    'pearson_correlations': pearson_r.tolist(),
    'spearman_correlations': spearman_r.tolist(),
    'strongest_anti_correlations': [
        {'features': [feature_names[i], feature_names[j]], 'r': r}
        for r, i, j in anti_corrs[:10]
    ],
    'complexity_budget': {
        'mean': float(budget.mean()),
        'std': float(budget.std()),
        'min': float(budget.min()),
        'max': float(budget.max()),
        'values': budget.tolist()
    },
    'exclusion_pairs': [
        {
            'features': [feature_names[i], feature_names[j]],
            'exclusion_index': float(exc),
            'both_high': int(bh),
            'only_first': int(o1),
            'only_second': int(o2)
        }
        for exc, i, j, bh, o1, o2 in exclusion_pairs[:10]
    ],
    'hull_fill_ratio': float(fill_ratio) if 'fill_ratio' in locals() else None,
    'distance_to_ideal': dist_ideal.tolist()
}

with open('impossibility_analysis.json', 'w') as f:
    json.dump(analysis_results, f, indent=2)
print("Saved impossibility_analysis.json")

print("\n=== ANALYSIS COMPLETE ===")
