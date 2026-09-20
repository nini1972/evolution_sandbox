#!/usr/bin/env python3
"""
Cartographer Phase 2: Deep Analysis of Conservation Laws and Exclusion Principles
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
feature_names = ['Lyapunov', 'CorrDim', 'FractalDim', 'SpatialEnt', 'Coupling', 'TempMemory', 'SignalEnt']

# Normalize
X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)
budget = X_norm.sum(axis=1)

print("=" * 70)
print("PHASE 2: DEEP ANALYSIS OF MORPHOSPACE STRUCTURE")
print("=" * 70)

# ============================================================
# ANALYSIS 1: Conservation Law Investigation
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 1: Conservation Law Investigation")
print("=" * 70)

# We found that -Lyap - CorrDim - Coupling ≈ constant
# Let's investigate this more deeply

# Compute the quantity for each system
Q = -X_norm[:, 0] - X_norm[:, 1] - X_norm[:, 4]  # -Lyap - CorrDim - Coupling
print(f"\nConservation quantity Q = -Lyap_norm - CorrDim_norm - Coupling_norm")
print(f"Mean: {Q.mean():.4f}, Std: {Q.std():.4f}")
print(f"Range: [{Q.min():.4f}, {Q.max():.4f}]")

# Check correlation between Q and other features
print("\nCorrelation between Q and other features:")
for i, name in enumerate(feature_names):
    if i not in [0, 1, 4]:  # Skip the features in Q
        corr = np.corrcoef(Q, X_norm[:, i])[0, 1]
        print(f"  Q vs {name:12s}: r = {corr:+.4f}")

# Check if Q is truly conserved or if there's structure
print("\nQ values by system:")
for i in range(len(names)):
    print(f"  {names[i]:20s}: Q = {Q[i]:+.4f}")

# ============================================================
# ANALYSIS 2: Exclusion Principle Deep Dive
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 2: Exclusion Principle Deep Dive")
print("=" * 70)

# The exclusion principle suggests CorrDim + Coupling < threshold
cd_coupling_sum = X_norm[:, 1] + X_norm[:, 4]
print(f"\nCorrDim_norm + Coupling_norm:")
print(f"Mean: {cd_coupling_sum.mean():.4f}, Std: {cd_coupling_sum.std():.4f}")
print(f"Range: [{cd_coupling_sum.min():.4f}, {cd_coupling_sum.max():.4f}]")

# Find the systems closest to the exclusion boundary
boundary_distance = 1.0 - cd_coupling_sum  # How far from boundary (1.0 = normalized)
closest_to_boundary = np.argsort(boundary_distance)
print("\nSystems closest to exclusion boundary:")
for i in closest_to_boundary[:5]:
    print(f"  {names[i]:20s}: CD+C = {cd_coupling_sum[i]:.4f}, distance = {boundary_distance[i]:.4f}")

# What about other pairwise exclusions?
print("\nPairwise feature exclusions:")
for i in range(7):
    for j in range(i+1, 7):
        corr = np.corrcoef(X_norm[:, i], X_norm[:, j])[0, 1]
        if abs(corr) > 0.4:
            print(f"  {feature_names[i]:12s} vs {feature_names[j]:12s}: r = {corr:+.4f}")

# ============================================================
# ANALYSIS 3: Cluster Analysis
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 3: Cluster Analysis")
print("=" * 70)

# From the previous analysis, we found 6 clusters
# Let's see which systems are in which clusters

# Simple k-means-like clustering (no sklearn dependency)
def simple_kmeans(X, n_clusters=6, max_iter=100):
    np.random.seed(42)
    # Initialize centroids randomly from data points
    indices = np.random.choice(len(X), n_clusters, replace=False)
    centroids = X[indices].copy()
    
    for _ in range(max_iter):
        # Assign points to nearest centroid
        labels = np.array([np.argmin([np.sum((x - c)**2) for c in centroids]) for x in X])
        # Update centroids
        new_centroids = np.array([X[labels == i].mean(axis=0) if np.sum(labels == i) > 0 
                                  else centroids[i] for i in range(n_clusters)])
        if np.allclose(centroids, new_centroids, rtol=1e-6):
            break
        centroids = new_centroids
    
    return labels, centroids

cluster_labels, _ = simple_kmeans(X_pca, n_clusters=6)

print("\nClusters found:")
for c in range(6):
    systems_in_cluster = [names[i] for i in range(len(names)) if cluster_labels[i] == c]
    if systems_in_cluster:
        print(f"\n  Cluster {c+1} ({len(systems_in_cluster)} systems):")
        for sys in systems_in_cluster:
            print(f"    {sys}")

# ============================================================
# ANALYSIS 4: Prediction Model for Empty Regions
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 4: Prediction Model for Empty Regions")
print("=" * 70)

# Build a simple model: for each point in the empty region, 
# predict what features it should have based on nearby systems

# Create a grid of points in PCA space
pca1_min, pca1_max = X_pca[:, 0].min() - 0.5, X_pca[:, 0].max() + 0.5
pca2_min, pca2_max = X_pca[:, 1].min() - 0.5, X_pca[:, 1].max() + 0.5

grid_res = 20
pca1_grid = np.linspace(pca1_min, pca1_max, grid_res)
pca2_grid = np.linspace(pca2_min, pca2_max, grid_res)

# For each grid point, find the k nearest systems and interpolate
k = 3
predicted_features = []

print(f"\nInterpolating features for {grid_res}x{grid_res} grid points...")
for p1 in pca1_grid:
    for p2 in pca2_grid:
        # Find distances to all systems
        distances = np.sqrt((X_pca[:, 0] - p1)**2 + (X_pca[:, 1] - p2)**2)
        # Get k nearest
        nearest_idx = np.argsort(distances)[:k]
        # Inverse distance weighting
        weights = 1.0 / (distances[nearest_idx] + 1e-10)
        weights = weights / weights.sum()
        # Interpolate features
        interp_features = np.average(X_norm[nearest_idx], axis=0, weights=weights)
        predicted_features.append(interp_features)

predicted_features = np.array(predicted_features)
print(f"Predicted features shape: {predicted_features.shape}")

# Now, find the grid points that are in empty regions (far from any system)
empty_threshold = 0.8
nearest_dist = np.full((grid_res, grid_res), np.inf)
for i in range(len(names)):
    for gi, p1 in enumerate(pca1_grid):
        for gj, p2 in enumerate(pca2_grid):
            dist = np.sqrt((p1 - X_pca[i, 0])**2 + (p2 - X_pca[i, 1])**2)
            nearest_dist[gi, gj] = min(nearest_dist[gi, gj], dist)

empty_mask = nearest_dist > empty_threshold
empty_indices = np.where(empty_mask.flatten())[0]

print(f"Number of empty grid points: {len(empty_indices)}")

# Analyze what features are predicted in empty regions
if len(empty_indices) > 0:
    empty_predicted = predicted_features[empty_indices]
    
    print("\nPredicted feature values in empty regions:")
    for i, name in enumerate(feature_names):
        mean_val = empty_predicted[:, i].mean()
        std_val = empty_predicted[:, i].std()
        print(f"  {name:12s}: mean = {mean_val:.4f}, std = {std_val:.4f}")
    
    # What are the most extreme predictions?
    print("\nMost extreme predicted features in empty regions:")
    for i, name in enumerate(feature_names):
        max_idx = np.argmax(empty_predicted[:, i])
        min_idx = np.argmin(empty_predicted[:, i])
        print(f"  {name:12s}: max = {empty_predicted[max_idx, i]:.4f}, min = {empty_predicted[min_idx, i]:.4f}")

# ============================================================
# ANALYSIS 5: System Archetypes
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 5: System Archetypes")
print("=" * 70)

# Define archetypes based on feature extremes
archetypes = {
    'Hyperchaos': {'Lyapunov': 1.0, 'CorrDim': 1.0},
    'Spatial Complexity': {'FractalDim': 1.0, 'SpatialEnt': 1.0},
    'Temporal Complexity': {'TempMemory': 1.0, 'SignalEnt': 1.0},
    'Weak Coupling': {'Coupling': 0.0},
    'Strong Coupling': {'Coupling': 1.0},
    'Low-D Chaos': {'CorrDim': 0.0, 'FractalDim': 0.5},
    'High-D Chaos': {'CorrDim': 1.0, 'FractalDim': 1.0}
}

print("\nArchetype definitions:")
for name, features in archetypes.items():
    print(f"  {name:20s}: {features}")

# Find systems closest to each archetype
print("\nSystems closest to each archetype:")
for arch_name, arch_features in archetypes.items():
    # Create feature vector
    arch_vec = np.zeros(7)
    for feat, val in arch_features.items():
        idx = feature_names.index(feat)
        arch_vec[idx] = val
    
    # Find closest system
    distances = np.sqrt(np.sum((X_norm - arch_vec)**2, axis=1))
    closest_idx = np.argmin(distances)
    print(f"  {arch_name:20s}: {names[closest_idx]} (distance = {distances[closest_idx]:.4f})")

# ============================================================
# Generate comprehensive visualization
# ============================================================
print("\n" + "=" * 70)
print("GENERATING COMPREHENSIVE VISUALIZATION")
print("=" * 70)

fig = plt.figure(figsize=(20, 15))

# Plot 1: Conservation Law
ax1 = fig.add_subplot(2, 3, 1)
scatter = ax1.scatter(X_pca[:, 0], X_pca[:, 1], c=Q, cmap='coolwarm', s=100, edgecolor='black')
plt.colorbar(scatter, ax=ax1, label='Q = -Lyap - CorrDim - Coupling')
for i, name in enumerate(names):
    ax1.annotate(name, (X_pca[i, 0], X_pca[i, 1]), fontsize=6, ha='center', va='bottom')
ax1.set_xlabel('PC1')
ax1.set_ylabel('PC2')
ax1.set_title('Conservation Law Distribution')
ax1.grid(True, alpha=0.3)

# Plot 2: Exclusion Principle
ax2 = fig.add_subplot(2, 3, 2)
scatter = ax2.scatter(X_norm[:, 1], X_norm[:, 4], c=budget, cmap='viridis', s=100, edgecolor='black')
plt.colorbar(scatter, ax=ax2, label='Budget (sum of normalized features)')
# Draw exclusion boundary
cd_grid = np.linspace(0, 1, 100)
boundary = 1.0 - cd_grid
ax2.plot(cd_grid, boundary, 'r--', linewidth=2, label='Exclusion Boundary')
ax2.fill_between(cd_grid, boundary, 1.0, alpha=0.2, color='red', label='Forbidden Zone')
ax2.set_xlabel('CorrDim (normalized)')
ax2.set_ylabel('Coupling (normalized)')
ax2.set_title('Exclusion Principle')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Cluster Analysis
ax3 = fig.add_subplot(2, 3, 3)
colors = plt.cm.Set1(np.linspace(0, 1, 6))
for c in range(6):
    mask = cluster_labels == c
    ax3.scatter(X_pca[mask, 0], X_pca[mask, 1], c=[colors[c]], s=100, 
                edgecolor='black', label=f'Cluster {c+1}')
for i, name in enumerate(names):
    ax3.annotate(name, (X_pca[i, 0], X_pca[i, 1]), fontsize=6, ha='center', va='bottom')
ax3.set_xlabel('PC1')
ax3.set_ylabel('PC2')
ax3.set_title('System Clusters')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Feature Correlations
ax4 = fig.add_subplot(2, 3, 4)
corr_matrix = np.corrcoef(X_norm.T)
im = ax4.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
plt.colorbar(im, ax=ax4)
ax4.set_xticks(range(7))
ax4.set_yticks(range(7))
ax4.set_xticklabels(feature_names, rotation=45, ha='right')
ax4.set_yticklabels(feature_names)
ax4.set_title('Feature Correlation Matrix')
# Add correlation values
for i in range(7):
    for j in range(7):
        ax4.text(j, i, f'{corr_matrix[i, j]:.2f}', ha='center', va='center', 
                color='white' if abs(corr_matrix[i, j]) > 0.5 else 'black')

# Plot 5: Budget Distribution
ax5 = fig.add_subplot(2, 3, 5)
ax5.hist(budget, bins=10, edgecolor='black', alpha=0.7)
ax5.axvline(budget.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean = {budget.mean():.3f}')
ax5.set_xlabel('Budget (Sum of Normalized Features)')
ax5.set_ylabel('Frequency')
ax5.set_title('Budget Distribution')
ax5.legend()
ax5.grid(True, alpha=0.3)

# Plot 6: Predicted Empty Regions
ax6 = fig.add_subplot(2, 3, 6)
# Show the empty regions with predicted features
ax6.scatter(X_pca[:, 0], X_pca[:, 1], c='blue', s=100, edgecolor='black', zorder=10, label='Existing Systems')

# Show empty regions
for gi in range(grid_res):
    for gj in range(grid_res):
        if empty_mask[gi, gj]:
            ax6.scatter(pca1_grid[gj], pca2_grid[gi], c='lightcoral', s=50, alpha=0.5, zorder=5)

ax6.set_xlabel('PC1')
ax6.set_ylabel('PC2')
ax6.set_title('Empty Regions (Red)')
ax6.legend()
ax6.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('deep_analysis_2.png', dpi=150, bbox_inches='tight')
print('Saved deep_analysis_2.png')

print("\n" + "=" * 70)
print("PHASE 2 COMPLETE")
print("=" * 70)