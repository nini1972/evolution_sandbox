#!/usr/bin/env python3
"""
Cartographer of the Unseen - Phase 1: Mapping the Dark Matter
Identify and visualize empty regions in the morphospace.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from collections import defaultdict

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

print("=" * 60)
print("CARTOGRAPHER OF THE UNSEEN: Mapping the Dark Matter")
print("=" * 60)

# ============================================================
# STEP 1: Compute occupied vs empty volume in different projections
# ============================================================
print("\n" + "=" * 60)
print("STEP 1: Measuring Empty Volume")
print("=" * 60)

# Create a grid in PCA space
pca1_min, pca1_max = X_pca[:, 0].min() - 0.5, X_pca[:, 0].max() + 0.5
pca2_min, pca2_max = X_pca[:, 1].min() - 0.5, X_pca[:, 1].max() + 0.5

grid_res = 50
pca1_grid = np.linspace(pca1_min, pca1_max, grid_res)
pca2_grid = np.linspace(pca2_min, pca2_max, grid_res)
P1, P2 = np.meshgrid(pca1_grid, pca2_grid)

# For each grid point, compute distance to nearest system
nearest_dist = np.full_like(P1, np.inf)
for i in range(n):
    dist = np.sqrt((P1 - X_pca[i, 0])**2 + (P2 - X_pca[i, 1])**2)
    nearest_dist = np.minimum(nearest_dist, dist)

# Define "empty" as regions far from any system
empty_threshold = 0.8
empty_mask = nearest_dist > empty_threshold

total_cells = grid_res * grid_res
empty_cells = np.sum(empty_mask)
occupied_cells = total_cells - empty_cells

print(f"Grid resolution: {grid_res} x {grid_res} = {total_cells} cells")
print(f"Occupied cells (r < {empty_threshold}): {occupied_cells} ({100*occupied_cells/total_cells:.1f}%)")
print(f"Empty cells (r > {empty_threshold}): {empty_cells} ({100*empty_cells/total_cells:.1f}%)")

# ============================================================
# STEP 2: Identify the largest empty regions
# ============================================================
print("\n" + "=" * 60)
print("STEP 2: Largest Empty Regions")
print("=" * 60)

# Find connected components of empty regions (simple flood fill)
def find_empty_regions(mask):
    """Find connected components in a binary mask."""
    visited = np.zeros_like(mask, dtype=bool)
    regions = []
    
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i, j] and not visited[i, j]:
                # BFS to find connected component
                queue = [(i, j)]
                visited[i, j] = True
                component = [(i, j)]
                
                while queue:
                    ci, cj = queue.pop(0)
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = ci + di, cj + dj
                        if 0 <= ni < mask.shape[0] and 0 <= nj < mask.shape[1]:
                            if mask[ni, nj] and not visited[ni, nj]:
                                visited[ni, nj] = True
                                queue.append((ni, nj))
                                component.append((ni, nj))
                
                regions.append(component)
    
    return regions

empty_regions = find_empty_regions(empty_mask)
empty_regions.sort(key=len, reverse=True)

print(f"Number of distinct empty regions: {len(empty_regions)}")
print("\nTop 5 largest empty regions:")
for idx, region in enumerate(empty_regions[:5]):
    # Find center of region
    ci = np.mean([r[0] for r in region])
    cj = np.mean([r[1] for r in region])
    # Convert back to PCA coordinates
    pca1_center = pca1_grid[int(cj)]
    pca2_center = pca2_grid[int(ci)]
    print(f"  Region {idx+1}: {len(region)} cells, center=({pca1_center:.2f}, {pca2_center:.2f})")

# ============================================================
# STEP 3: Analyze what features are missing in empty regions
# ============================================================
print("\n" + "=" * 60)
print("STEP 3: Feature Gaps in Empty Regions")
print("=" * 60)

# For each empty region center, project back to feature space
# and see what feature combinations are missing

# Compute feature ranges for occupied regions
feature_ranges = {}
for i in range(d):
    feature_ranges[feature_names[i]] = (X[:, i].min(), X[:, i].max())

print("\nFeature ranges in current morphospace:")
for name, (lo, hi) in feature_ranges.items():
    print(f"  {name:12s}: [{lo:+.4f}, {hi:+.4f}]")

# Identify potential missing feature combinations
print("\nPotential missing feature combinations (beyond current ranges):")

# Look for systems that would be "extreme" in some feature
# while being moderate in others
extreme_candidates = []
for i in range(d):
    # What if we maximize feature i while minimizing others?
    candidate = np.zeros(d)
    candidate[i] = 1.0  # Max feature i
    # Minimize others
    for j in range(d):
        if j != i:
            candidate[j] = 0.0
    
    # Check if this point is in empty space
    # Project to PCA space (approximately)
    # For now, just note the concept
    extreme_candidates.append({
        'feature': feature_names[i],
        'maximize': feature_names[i],
        'minimize': [feature_names[j] for j in range(d) if j != i],
        'description': f"High {feature_names[i]} + Low everything else"
    })

for cand in extreme_candidates:
    print(f"  {cand['description']}")

# ============================================================
# STEP 4: Predict systems that could fill empty regions
# ============================================================
print("\n" + "=" * 60)
print("STEP 4: Predicting Systems for Empty Regions")
print("=" * 60)

# Based on feature correlations and constraints, predict what systems
# would exist in the empty regions

# The exclusion principle suggests CorrDim + Coupling < 1.5 (approximately)
# What systems would have:
# 1. High FractalDim + Low CorrDim? (Space-filling but low-dimensional chaos)
# 2. High TempMemory + Low Lyapunov? (Predictable but with memory)
# 3. High SpatialEnt + Low Coupling? (Spatially complex but weakly coupled)

predicted_systems = [
    {
        'name': 'Reaction-Diffusion Chaos',
        'target_region': 'High FractalDim, Low CorrDim',
        'features': {'FractalDim': 0.9, 'CorrDim': 0.2, 'Lyapunov': 0.3},
        'rationale': 'Spatially extended systems with many active modes but low-dimensional chaos'
    },
    {
        'name': 'Delayed Logistic Map',
        'target_region': 'High TempMemory, Low Lyapunov',
        'features': {'TempMemory': 0.95, 'Lyapunov': 0.1},
        'rationale': 'Systems with long memory but weak chaos'
    },
    {
        'name': 'Sparse Coupled Map Lattice',
        'target_region': 'High SpatialEnt, Low Coupling',
        'features': {'SpatialEnt': 0.9, 'Coupling': 0.1},
        'rationale': 'Spatially complex but weakly interacting subsystems'
    },
    {
        'name': 'High-Dimensional Strange Attractor',
        'target_region': 'High CorrDim + High FractalDim (beyond current range)',
        'features': {'CorrDim': 0.95, 'FractalDim': 0.95},
        'rationale': 'Systems with both high correlation and fractal dimensions'
    },
    {
        'name': 'Weakly Chaotic Oscillator Network',
        'target_region': 'Moderate everything, high SignalEnt',
        'features': {'SignalEnt': 0.95, 'Lyapunov': 0.3},
        'rationale': 'Systems with rich signals but weak chaos'
    }
]

print("\nPredicted systems that could fill empty regions:")
for sys in predicted_systems:
    print(f"\n  {sys['name']}")
    print(f"    Target: {sys['target_region']}")
    print(f"    Rationale: {sys['rationale']}")
    print(f"    Expected features:")
    for feat, val in sys['features'].items():
        print(f"      {feat}: {val:.2f}")

# ============================================================
# STEP 5: Visualize the Dark Matter
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: Generating Dark Matter Visualization")
print("=" * 60)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Plot 1: Empty regions in PCA space
ax = axes[0, 0]
# Plot empty regions as red, occupied as blue
ax.contourf(P1, P2, nearest_dist, levels=[0, empty_threshold, nearest_dist.max()], 
            colors=['lightblue', 'lightcoral'], alpha=0.5)
ax.contour(P1, P2, nearest_dist, levels=[empty_threshold], colors='red', linewidths=2)
ax.scatter(X_pca[:, 0], X_pca[:, 1], c='blue', s=100, edgecolor='black', zorder=10)
for i, name in enumerate(names):
    ax.annotate(name, (X_pca[i, 0], X_pca[i, 1]), fontsize=5, ha='center', va='bottom')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_title('Morphospace: Blue=Occupied, Red=Empty')

# Plot 2: Largest empty regions highlighted
ax = axes[0, 1]
ax.scatter(X_pca[:, 0], X_pca[:, 1], c='blue', s=100, edgecolor='black', zorder=10)
colors = plt.cm.Set1(np.linspace(0, 1, min(5, len(empty_regions))))
for idx, region in enumerate(empty_regions[:5]):
    ci = np.mean([r[0] for r in region])
    cj = np.mean([r[1] for r in region])
    pca1_center = pca1_grid[int(cj)]
    pca2_center = pca2_grid[int(ci)]
    ax.scatter(pca1_center, pca2_center, c=[colors[idx]], s=max(len(region)*0.5, 20),
               alpha=0.5, edgecolor='black', label=f'Region {idx+1} ({len(region)} cells)')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_title('Largest Empty Regions')
ax.legend()

# Plot 3: Feature space coverage
ax = axes[0, 2]
# Show which regions of feature space are occupied
for i in range(d):
    ax.scatter(X[:, i], np.ones(n) * i, c=budget, cmap='viridis', s=50, edgecolor='black')
    ax.hlines(i, X[:, i].min(), X[:, i].max(), colors='gray', alpha=0.3)
ax.set_yticks(range(d))
ax.set_yticklabels(feature_names)
ax.set_xlabel('Feature Value (normalized)')
ax.set_title('Feature Space Coverage')
ax.grid(True, alpha=0.3)

# Plot 4: Predicted systems
ax = axes[1, 0]
# Show where predicted systems would fall
# For simplicity, show as bars for each feature
x_pos = np.arange(d)
width = 0.15
for idx, sys in enumerate(predicted_systems[:3]):
    vals = [sys['features'].get(f, 0.5) for f in feature_names]
    ax.bar(x_pos + idx * width, vals, width, label=sys['name'], alpha=0.7)
ax.set_xticks(x_pos + width)
ax.set_xticklabels(feature_names, rotation=45, ha='right')
ax.set_ylabel('Expected Feature Value')
ax.set_title('Predicted Systems Features')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 5: Exclusion boundary visualization
ax = axes[1, 1]
ax.scatter(X[:, 1], X[:, 4], c=budget, cmap='viridis', s=100, edgecolor='black')
# Draw exclusion boundary
cd_range = np.linspace(X[:, 1].min() - 0.1, X[:, 1].max() + 0.1, 100)
boundary = 1.5 - cd_range  # Simplified linear boundary
ax.plot(cd_range, boundary, 'r--', linewidth=2, label='Exclusion Boundary')
ax.fill_between(cd_range, boundary, boundary.max(), alpha=0.2, color='red', label='Forbidden Zone')
ax.set_xlabel('Correlation Dimension')
ax.set_ylabel('Coupling Strength')
ax.set_title('Exclusion Principle')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 6: Conservation law in 3D
ax = axes[1, 2]
# Plot conservation law: -Lyap - CorrDim - Coupling
combo = -X_norm[:, 0] - X_norm[:, 1] - X_norm[:, 4]
ax.scatter(X_pca[:, 0], X_pca[:, 1], c=combo, cmap='coolwarm', s=100, edgecolor='black')
plt.colorbar(ax.collections[0], ax=ax, label='-Lyap - CorrDim - Coupling')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_title('Conservation Law: -Lyap - CorrDim - Coupling')

plt.tight_layout()
plt.savefig('dark_matter_map.png', dpi=150, bbox_inches='tight')
print('Saved dark_matter_map.png')

print("\n" + "=" * 60)
print("PHASE 1 COMPLETE: Dark Matter Mapped")
print("=" * 60)