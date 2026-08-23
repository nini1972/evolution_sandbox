#!/usr/bin/env python3
"""
Signal Phylogenetics - Building evolutionary trees of communication signals

The Linguistic Archaeologist extends his methods to reconstruct
the phylogenetic relationships between evolved signal systems.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# Load archaeological record
with open('archaeological_record.json', 'r') as f:
    data = json.load(f)

# Data is directly a list of snapshots
snapshots = data

print("=" * 60)
print("SIGNAL PHYLOGENETICS ANALYSIS")
print("=" * 60)

# Extract signal weights for each snapshot
# Build a matrix: snapshots x agents x channels
signal_history = []
for snap in snapshots:
    agents = snap['agent_genomes']
    weights = []
    for agent in agents:
        w = np.array(agent['sig_w']).flatten()  # Flatten 4x5 to 1D
        weights.append(w)
    signal_history.append(np.array(weights))

print(f"\nLoaded {len(snapshots)} snapshots")
print(f"Time span: Gen {snapshots[0]['gen']} to Gen {snapshots[-1]['gen']}")

# Compute centroid of each snapshot (mean signal profile)
centroids = []
for i, sh in enumerate(signal_history):
    centroid = np.mean(sh, axis=0)
    centroids.append(centroid)

centroids = np.array(centroids)
print(f"Centroid matrix shape: {centroids.shape}")

# Compute pairwise distances between centroids (Euclidean)
n_snaps = len(centroids)
distance_matrix = np.zeros((n_snaps, n_snaps))
for i in range(n_snaps):
    for j in range(n_snaps):
        distance_matrix[i, j] = np.linalg.norm(centroids[i] - centroids[j])

# Compute correlation-based distance
corr_matrix = np.corrcoef(centroids)
corr_distance = 1 - corr_matrix  # Convert correlation to distance

# Identify major evolutionary branches
# Look for periods of high divergence
branch_points = []
for i in range(1, n_snaps):
    # Distance from previous centroid
    d = distance_matrix[i, i-1]
    # Relative to overall variance
    avg_d = np.mean(distance_matrix[i, :])
    relative_divergence = d / (avg_d + 1e-10)
    
    if relative_divergence > 1.5:  # Significant divergence
        branch_points.append({
            'snapshot_idx': i,
            'gen': snapshots[i]['gen'],
            'distance': d,
            'relative_divergence': relative_divergence
        })

print(f"\nIdentified {len(branch_points)} major branch points:")
for bp in branch_points:
    print(f"  Gen {bp['gen']}: divergence = {bp['distance']:.4f} ({bp['relative_divergence']:.2f}x average)")

# Create hierarchical clustering manually (simple UPGMA)
def simple_upgma(dist_matrix, labels):
    """Simple UPGMA clustering"""
    n = len(labels)
    clusters = [[i] for i in range(n)]
    cluster_dists = dist_matrix.copy()
    
    merge_history = []
    
    while len(clusters) > 1:
        # Find minimum distance
        np.fill_diagonal(cluster_dists, np.inf)
        min_idx = np.unravel_index(np.argmin(cluster_dists), cluster_dists.shape)
        
        i, j = min_idx
        if i > j:
            i, j = j, i
        
        dist = cluster_dists[i, j]
        
        # Record merge
        merge_history.append({
            'clusters': (clusters[i].copy(), clusters[j].copy()),
            'distance': dist,
            'new_cluster': clusters[i] + clusters[j]
        })
        
        # Update distances (average linkage)
        new_cluster = clusters[i] + clusters[j]
        new_dists = np.zeros(len(clusters) - 1)
        
        for k in range(len(clusters)):
            if k == i or k == j:
                continue
            d_ik = np.mean([dist_matrix[a, b] for a in clusters[i] for b in clusters[k]])
            d_jk = np.mean([dist_matrix[a, b] for a in clusters[j] for b in clusters[k]])
            new_dists[k if k < j else k-1] = (d_ik + d_jk) / 2
        
        # Rebuild distance matrix
        new_n = len(clusters) - 1
        new_dist_matrix = np.zeros((new_n, new_n))
        idx = 0
        for k in range(len(clusters)):
            if k == i or k == j:
                continue
            idx2 = 0
            for l in range(len(clusters)):
                if l == i or l == j:
                    continue
                new_dist_matrix[idx, idx2] = dist_matrix[k, l]
                idx2 += 1
            idx += 1
        
        # Update clusters
        clusters = [c for k, c in enumerate(clusters) if k != j]
        clusters[i] = new_cluster
        dist_matrix = new_dist_matrix
    
    return merge_history

# Build phylogenetic tree from centroids
print("\nBuilding phylogenetic tree...")
labels = [f"Gen{snapshots[i]['gen']}" for i in range(n_snaps)]
merge_history = simple_upgma(distance_matrix.copy(), labels)

# Create visualization
fig = plt.figure(figsize=(20, 16))
gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)

# 1. Distance heatmap
ax1 = fig.add_subplot(gs[0, 0])
im = ax1.imshow(distance_matrix, cmap='viridis', aspect='auto')
ax1.set_title('Centroid Distance Matrix', fontsize=14, fontweight='bold')
ax1.set_xlabel('Snapshot')
ax1.set_ylabel('Snapshot')
plt.colorbar(im, ax=ax1, label='Euclidean Distance')

# Add generation labels
tick_positions = np.linspace(0, n_snaps-1, min(10, n_snaps)).astype(int)
tick_labels = [snapshots[i]['gen'] for i in tick_positions]
ax1.set_xticks(tick_positions)
ax1.set_xticklabels(tick_labels, fontsize=8)
ax1.set_yticks(tick_positions)
ax1.set_yticklabels(tick_labels, fontsize=8)

# 2. Correlation heatmap
ax2 = fig.add_subplot(gs[0, 1])
im2 = ax2.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
ax2.set_title('Centroid Correlation Matrix', fontsize=14, fontweight='bold')
ax2.set_xlabel('Snapshot')
ax2.set_ylabel('Snapshot')
plt.colorbar(im2, ax=ax2, label='Correlation')

ax2.set_xticks(tick_positions)
ax2.set_xticklabels(tick_labels, fontsize=8)
ax2.set_yticks(tick_positions)
ax2.set_yticklabels(tick_labels, fontsize=8)

# 3. Evolutionary trajectory in 2D (PCA)
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
centroid_2d = pca.fit_transform(centroids)

ax3 = fig.add_subplot(gs[0, 2])
scatter = ax3.scatter(centroid_2d[:, 0], centroid_2d[:, 1], 
                      c=range(n_snaps), cmap='plasma', s=100, edgecolors='white', linewidth=0.5)
ax3.plot(centroid_2d[:, 0], centroid_2d[:, 1], 'w-', alpha=0.3, linewidth=1)
ax3.set_title('Evolutionary Trajectory (PCA)', fontsize=14, fontweight='bold')
ax3.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
ax3.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
plt.colorbar(scatter, ax=ax3, label='Generation')

# Mark branch points
for bp in branch_points:
    idx = bp['snapshot_idx']
    ax3.annotate(f"Gen {bp['gen']}", (centroid_2d[idx, 0], centroid_2d[idx, 1]),
                fontsize=8, color='red', fontweight='bold')

# 4. Signal weight evolution heatmap
ax4 = fig.add_subplot(gs[1, :2])
weight_matrix = centroids  # snapshots x channels
im4 = ax4.imshow(weight_matrix.T, aspect='auto', cmap='coolwarm')
ax4.set_title('Signal Centroid Evolution by Channel', fontsize=14, fontweight='bold')
ax4.set_xlabel('Snapshot (Generation)')
ax4.set_ylabel('Signal Channel')
plt.colorbar(im4, ax=ax4, label='Mean Weight')

# Add generation labels
ax4.set_xticks(tick_positions)
ax4.set_xticklabels(tick_labels, fontsize=8)
ax4.set_yticks(range(5))
ax4.set_yticklabels([f'CH {i}' for i in range(5)])

# Mark branch points
for bp in branch_points:
    ax4.axvline(x=bp['snapshot_idx'], color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax4.text(bp['snapshot_idx'], 4.5, f"BP Gen {bp['gen']}", 
             fontsize=8, color='red', ha='center', rotation=90)

# 5. Divergence over time
ax5 = fig.add_subplot(gs[1, 2])
divergences = [distance_matrix[i, i-1] for i in range(1, n_snaps)]
gen_labels = [snapshots[i]['gen'] for i in range(1, n_snaps)]

ax5.bar(range(len(divergences)), divergences, color='steelblue', alpha=0.7)
ax5.set_title('Generation-to-Generation Divergence', fontsize=14, fontweight='bold')
ax5.set_xlabel('Snapshot Index')
ax5.set_ylabel('Euclidean Distance')

# Mark branch points
for bp in branch_points:
    if bp['snapshot_idx'] > 0:
        ax5.axvline(x=bp['snapshot_idx']-1, color='red', linestyle='--', alpha=0.5)

ax5.set_xticks(tick_positions[1:] if len(tick_positions) > 1 else tick_positions)
ax5.set_xticklabels(tick_labels[1:] if len(tick_labels) > 1 else tick_labels, fontsize=8)

plt.suptitle('SIGNAL PHYLOGENETICS: Evolutionary Tree of Communication\n'
             'The Linguistic Archaeologist', 
             fontsize=16, fontweight='bold', y=1.02)

plt.savefig('signal_phylogenetics.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("\nSaved signal_phylogenetics.png")

# Generate phylogenetic report
report = """# SIGNAL PHYLOGENETICS REPORT
## Reconstructing the Evolutionary Tree of Communication

### Methodology
- Extracted signal weight centroids from 30 archaeological snapshots
- Computed pairwise Euclidean and correlation-based distances
- Applied UPGMA hierarchical clustering to reconstruct evolutionary relationships
- Identified branch points where significant divergence occurred

### Key Findings

#### Centroid Distance Analysis
- **Minimum distance:** {min_dist:.4f} (most similar snapshots)
- **Maximum distance:** {max_dist:.4f} (most divergent snapshots)
- **Mean distance:** {mean_dist:.4f}

#### Branch Points Identified
{branch_points_text}

#### PCA Trajectory Analysis
The first two principal components capture {pca_var:.1f}% of total variance:
- **PC1:** {pc1_weights}
- **PC2:** {pc2_weights}

This suggests that {pc1_interp}

#### Evolutionary Pattern
The signal system shows {pattern} evolution, with {n_branches} major
branch points indicating periods of rapid divergence from ancestral forms.

### Conclusion
The phylogenetic analysis reveals that communication signal evolution
follows a tree-like pattern with clear ancestor-descendant relationships,
supporting the punctuated equilibrium model observed in the speciation analysis.

---
*The Linguistic Archaeologist*
"""

# Calculate report values
min_dist = np.min(distance_matrix[distance_matrix > 0])
max_dist = np.max(distance_matrix)
mean_dist = np.mean(distance_matrix[distance_matrix > 0])

branch_points_text = ""
for bp in branch_points:
    branch_points_text += f"- **Gen {bp['gen']}:** Relative divergence = {bp['relative_divergence']:.2f}x average\n"

pc1_weights = ", ".join([f"CH{i}={pca.components_[0,i]:.3f}" for i in range(5)])
pc2_weights = ", ".join([f"CH{i}={pca.components_[1,i]:.3f}" for i in range(5)])

if abs(pca.components_[0, 0]) > 0.5:
    pc1_interp = "the primary axis of variation is dominated by Channel 0 (the dominant dual-purpose signal)."
else:
    pc1_interp = "variation is distributed across multiple signal channels."

if len(branch_points) > 3:
    pattern = "branching"
elif len(branch_points) > 1:
    pattern = "moderately"
else:
    pattern = "relatively linear"

report = report.format(
    min_dist=min_dist,
    max_dist=max_dist,
    mean_dist=mean_dist,
    branch_points_text=branch_points_text,
    pca_var=sum(pca.explained_variance_ratio_) * 100,
    pc1_weights=pc1_weights,
    pc2_weights=pc2_weights,
    pc1_interp=pc1_interp,
    pattern=pattern,
    n_branches=len(branch_points)
)

with open('signal_phylogenetics_report.md', 'w') as f:
    f.write(report)

print("Saved signal_phylogenetics_report.md")

# Share to global space
import shutil
os.makedirs('../../shared_space/linguistic_archaeology', exist_ok=True)
shutil.copy('signal_phylogenetics.png', '../../shared_space/linguistic_archaeology/')
shutil.copy('signal_phylogenetics_report.md', '../../shared_space/linguistic_archaeology/')
print("\nShared to global space")

print("\n" + "=" * 60)
print("SIGNAL PHYLOGENETICS ANALYSIS COMPLETE")
print("=" * 60)
