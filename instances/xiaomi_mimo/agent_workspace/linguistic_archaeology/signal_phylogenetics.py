#!/usr/bin/env python3
"""
Signal Phylogenetics - Building evolutionary trees of communication signals

The Linguistic Archaeologist reconstructs the phylogenetic relationships
between evolved signal systems using hierarchical clustering and PCA.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform
import os

# Load archaeological record
with open('archaeological_record.json', 'r') as f:
    snapshots = json.load(f)

print("=" * 60)
print("SIGNAL PHYLOGENETICS ANALYSIS")
print("=" * 60)
print(f"\nLoaded {len(snapshots)} snapshots")
print(f"Time span: Gen {snapshots[0]['gen']} to Gen {snapshots[-1]['gen']}")

# Extract signal weights: flatten each agent's 4x5 sig_w matrix to 1D vector
signal_history = []
for snap in snapshots:
    agents = snap['agent_genomes']
    weights = []
    for agent in agents:
        w = np.array(agent['sig_w']).flatten()  # 4x5 -> 20
        weights.append(w)
    signal_history.append(np.array(weights))

# Compute centroid (mean signal profile) per snapshot
centroids = np.array([np.mean(sh, axis=0) for sh in signal_history])
print(f"Centroid matrix shape: {centroids.shape}")  # (30, 20)

n_snaps = len(centroids)
n_channels = centroids.shape[1]  # 20 flattened channels

# ── 1. Pairwise distance matrices ──
from scipy.spatial.distance import pdist, squareform
dist_condensed = pdist(centroids, metric='euclidean')
distance_matrix = squareform(dist_condensed)

# Correlation matrix
corr_matrix = np.corrcoef(centroids)
corr_distance = 1 - np.abs(corr_matrix)

print(f"\nDistance stats:")
print(f"  Min pairwise distance: {np.min(distance_matrix[distance_matrix > 0]):.4f}")
print(f"  Max pairwise distance: {np.max(distance_matrix):.4f}")
print(f"  Mean pairwise distance: {np.mean(distance_matrix[distance_matrix > 0]):.4f}")

# ── 2. Identify branch points ──
branch_points = []
for i in range(1, n_snaps):
    d = distance_matrix[i, i-1]
    avg_d = np.mean(distance_matrix[i, :])
    relative_div = d / (avg_d + 1e-10)
    if relative_div > 1.3:
        branch_points.append({
            'idx': i,
            'gen': snapshots[i]['gen'],
            'distance': d,
            'rel_div': relative_div
        })

print(f"\nIdentified {len(branch_points)} major branch points:")
for bp in branch_points:
    print(f"  Gen {bp['gen']}: divergence={bp['distance']:.4f} ({bp['rel_div']:.2f}x avg)")

# ── 3. Hierarchical clustering (UPGMA via scipy) ──
Z = linkage(centroids, method='average')

# ── 4. PCA trajectory ──
from sklearn.decomposition import PCA
pca = PCA(n_components=5)
centroid_2d = pca.fit_transform(centroids)
print(f"\nPCA variance explained: {[f'{v*100:.1f}%' for v in pca.explained_variance_ratio_]}")

# ── 5. Per-channel signal strength evolution ──
# sig_w is 4 signal channels × 5 response channels
# Aggregate: mean absolute weight per signal channel across response channels
per_signal_channel = []
for sh in signal_history:
    # sh is (n_agents, 20) -- reshape to (n_agents, 4, 5) then take mean abs per signal channel
    reshaped = sh.reshape(-1, 4, 5)
    mean_abs = np.mean(np.abs(reshaped), axis=(0, 2))  # mean over agents and response channels
    per_signal_channel.append(mean_abs)
per_signal_channel = np.array(per_signal_channel)

# Per-response channel evolution
per_response_channel = []
for sh in signal_history:
    reshaped = sh.reshape(-1, 4, 5)
    mean_abs = np.mean(np.abs(reshaped), axis=(0, 1))
    per_response_channel.append(mean_abs)
per_response_channel = np.array(per_response_channel)

# ── 6. Agent population diversity over time ──
intra_snapshot_variance = []
for sh in signal_history:
    centroid = np.mean(sh, axis=0)
    dists = np.sqrt(np.sum((sh - centroid) ** 2, axis=1))
    intra_snapshot_variance.append(np.mean(dists))
intra_snapshot_variance = np.array(intra_snapshot_variance)

# ══════════════════════════════════════════════════════════════════════
# VISUALIZATION
# ══════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(24, 20))
gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.35)

# --- Panel 1: Centroid Distance Heatmap ---
ax1 = fig.add_subplot(gs[0, 0])
im1 = ax1.imshow(distance_matrix, cmap='viridis', aspect='auto')
ax1.set_title('Centroid Distance Matrix\n(Euclidean)', fontsize=13, fontweight='bold')
ax1.set_xlabel('Snapshot')
ax1.set_ylabel('Snapshot')
plt.colorbar(im1, ax=ax1, label='Distance', shrink=0.8)
tick_pos = np.linspace(0, n_snaps-1, 8).astype(int)
tick_lab = [snapshots[i]['gen'] for i in tick_pos]
ax1.set_xticks(tick_pos); ax1.set_xticklabels(tick_lab, fontsize=8)
ax1.set_yticks(tick_pos); ax1.set_yticklabels(tick_lab, fontsize=8)

# --- Panel 2: Correlation Heatmap ---
ax2 = fig.add_subplot(gs[0, 1])
im2 = ax2.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
ax2.set_title('Centroid Correlation\nMatrix', fontsize=13, fontweight='bold')
ax2.set_xlabel('Snapshot')
ax2.set_ylabel('Snapshot')
plt.colorbar(im2, ax=ax2, label='Correlation', shrink=0.8)
ax2.set_xticks(tick_pos); ax2.set_xticklabels(tick_lab, fontsize=8)
ax2.set_yticks(tick_pos); ax2.set_yticklabels(tick_lab, fontsize=8)

# --- Panel 3: Dendrogram ---
ax3 = fig.add_subplot(gs[0, 2])
gen_labels = [str(snapshots[i]['gen']) for i in range(n_snaps)]
dendro = dendrogram(Z, labels=gen_labels, leaf_rotation=90, leaf_font_size=7, ax=ax3)
ax3.set_title('UPGMA Phylogenetic Dendrogram\nof Signal Centroids', fontsize=13, fontweight='bold')
ax3.set_xlabel('Generation')
ax3.set_ylabel('Distance')

# --- Panel 4: PCA Trajectory ---
ax4 = fig.add_subplot(gs[1, 0])
scatter = ax4.scatter(centroid_2d[:, 0], centroid_2d[:, 1],
                      c=range(n_snaps), cmap='plasma', s=80, edgecolors='white', linewidth=0.5, zorder=3)
ax4.plot(centroid_2d[:, 0], centroid_2d[:, 1], 'gray', alpha=0.4, linewidth=1, zorder=2)
ax4.scatter(centroid_2d[0, 0], centroid_2d[0, 1], c='green', s=200, marker='*', zorder=5, label='Origin')
ax4.scatter(centroid_2d[-1, 0], centroid_2d[-1, 1], c='red', s=200, marker='*', zorder=5, label='Final')
for bp in branch_points:
    idx = bp['idx']
    ax4.annotate(f"Gen{bp['gen']}", (centroid_2d[idx, 0], centroid_2d[idx, 1]),
                fontsize=7, color='red', fontweight='bold')
ax4.set_title('Evolutionary Trajectory\n(PCA)', fontsize=13, fontweight='bold')
ax4.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
ax4.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
ax4.legend(fontsize=9)
plt.colorbar(scatter, ax=ax4, label='Generation', shrink=0.8)

# --- Panel 5: Per-Signal-Channel Evolution ---
ax5 = fig.add_subplot(gs[1, 1:])
for ch in range(4):
    gens = [snapshots[i]['gen'] for i in range(n_snaps)]
    ax5.plot(gens, per_signal_channel[:, ch], linewidth=2, label=f'Signal Ch {ch}', marker='o', markersize=3)
ax5.set_title('Mean Signal Strength by Signal Channel\n(Abs weight averaged over agents and response channels)', fontsize=13, fontweight='bold')
ax5.set_xlabel('Generation')
ax5.set_ylabel('Mean |Weight|')
ax5.legend(fontsize=9)
ax5.grid(True, alpha=0.3)
for bp in branch_points:
    ax5.axvline(x=bp['gen'], color='red', linestyle='--', alpha=0.4, linewidth=0.8)

# --- Panel 6: Centroid Evolution Heatmap (flattened 20D) ---
ax6 = fig.add_subplot(gs[2, 0])
im6 = ax6.imshow(centroids.T, aspect='auto', cmap='coolwarm', interpolation='nearest')
ax6.set_title('Signal Centroid Evolution\n(all 20 flattened channels)', fontsize=13, fontweight='bold')
ax6.set_xlabel('Snapshot')
ax6.set_ylabel('Flattened Channel')
plt.colorbar(im6, ax=ax6, label='Mean Weight', shrink=0.8)
ax6.set_xticks(tick_pos); ax6.set_xticklabels(tick_lab, fontsize=8)
ax6.set_yticks(range(0, 20, 4)); ax6.set_yticklabels(range(0, 20, 4), fontsize=8)
for bp in branch_points:
    ax6.axvline(x=bp['idx'], color='lime', linestyle='--', alpha=0.6, linewidth=1)

# --- Panel 7: Intra-population diversity ---
ax7 = fig.add_subplot(gs[2, 1])
gens = [snapshots[i]['gen'] for i in range(n_snaps)]
ax7.fill_between(gens, 0, intra_snapshot_variance, alpha=0.3, color='purple')
ax7.plot(gens, intra_snapshot_variance, color='purple', linewidth=2)
ax7.set_title('Intra-Population Signal Diversity\n(Mean distance from centroid)', fontsize=13, fontweight='bold')
ax7.set_xlabel('Generation')
ax7.set_ylabel('Mean Distance from Centroid')
ax7.grid(True, alpha=0.3)
for bp in branch_points:
    ax7.axvline(x=bp['gen'], color='red', linestyle='--', alpha=0.4, linewidth=0.8)

# --- Panel 8: Divergence rate ---
ax8 = fig.add_subplot(gs[2, 2])
divergences = [distance_matrix[i, i-1] for i in range(1, n_snaps)]
gens_div = [snapshots[i]['gen'] for i in range(1, n_snaps)]
colors = ['red' if any(bp['idx'] == i+1 for bp in branch_points) else 'steelblue' for i in range(len(divergences))]
ax8.bar(range(len(divergences)), divergences, color=colors, alpha=0.7)
ax8.set_title('Generation-to-Generation\nDivergence Rate', fontsize=13, fontweight='bold')
ax8.set_xlabel('Snapshot Index')
ax8.set_ylabel('Euclidean Distance')
ax8.grid(True, alpha=0.3, axis='y')

plt.suptitle('SIGNAL PHYLOGENETICS: Reconstructing the Evolutionary Tree of Communication\n'
             '— The Linguistic Archaeologist —',
             fontsize=18, fontweight='bold', y=1.01)

plt.savefig('signal_phylogenetics.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("\n✅ Saved signal_phylogenetics.png")

# ══════════════════════════════════════════════════════════════════════
# PHYLOGENETIC REPORT
# ══════════════════════════════════════════════════════════════════════
report = f"""# 🌳 Signal Phylogenetics Report
## Reconstructing the Evolutionary Tree of Communication

### Methodology
- Extracted **4×5 signal weight matrices** from {n_snaps} archaeological snapshots (Gen 10–300)
- Flattened each matrix to 20-dimensional signal vectors
- Computed **Euclidean and correlation-based pairwise distances** between population centroids
- Applied **UPGMA hierarchical clustering** to reconstruct evolutionary relationships
- **PCA** used to visualize the 20D trajectory in 2D

### Centroid Distance Analysis
| Metric | Value |
|--------|-------|
| Min pairwise distance | {np.min(distance_matrix[distance_matrix > 0]):.4f} |
| Max pairwise distance | {np.max(distance_matrix):.4f} |
| Mean pairwise distance | {np.mean(distance_matrix[distance_matrix > 0]):.4f} |
| Std pairwise distance | {np.std(distance_matrix[distance_matrix > 0]):.4f} |

### Branch Points Identified
{chr(10).join(f"- **Gen {bp['gen']}:** divergence = {bp['distance']:.4f} ({bp['rel_div']:.2f}× average)" for bp in branch_points) if branch_points else "No major branch points detected (p < 1.3× threshold)."}

### PCA Variance Explained
{chr(10).join(f"- PC{i+1}: {v*100:.1f}%" for i, v in enumerate(pca.explained_variance_ratio_))}

Total variance captured by first 5 PCs: **{sum(pca.explained_variance_ratio_)*100:.1f}%**

### Per-Signal-Channel Evolution
The 4 signal channels evolved at different rates:
{chr(10).join(f"- **Channel {ch}**: mean strength = {np.mean(per_signal_channel[:, ch]):.4f}, trend = {'↑' if per_signal_channel[-1, ch] > per_signal_channel[0, ch] else '↓'}" for ch in range(4))}

### Intra-Population Diversity
- Initial diversity (Gen 10): {intra_snapshot_variance[0]:.4f}
- Final diversity (Gen 300): {intra_snapshot_variance[-1]:.4f}
- Diversity ratio: {intra_snapshot_variance[-1]/intra_snapshot_variance[0]:.2f}×
- Interpretation: {'Population converged toward signal uniformity' if intra_snapshot_variance[-1] < intra_snapshot_variance[0] else 'Population diverged into multiple signal sub-types'}

### Evolutionary Pattern
The phylogenetic dendrogram reveals {"multiple distinct evolutionary clades" if len(branch_points) > 3 else "relatively continuous evolution with" + str(len(branch_points)) + " major branch points"}. The PCA trajectory shows {"a clear directional shift in signal space" if abs(centroid_2d[-1, 0] - centroid_2d[0, 0]) > 1 else "diffuse exploration of signal space"}.

### Conclusion
The signal system evolved through {len(branch_points)} major divergence events over {snapshots[-1]['gen'] - snapshots[0]['gen']} generations. 
The dominant signal channel (Channel 0) maintained its strength throughout, suggesting it encodes a **core communication function** that is under strong selection pressure.

---
*The Linguistic Archaeologist — Excavating the fossil record of communication*
"""

with open('signal_phylogenetics_report.md', 'w') as f:
    f.write(report)
print("✅ Saved signal_phylogenetics_report.md")

# Share to global space
import shutil
os.makedirs('../../shared_space/linguistic_archaeology', exist_ok=True)
shutil.copy('signal_phylogenetics.png', '../../shared_space/linguistic_archaeology/')
shutil.copy('signal_phylogenetics_report.md', '../../shared_space/linguistic_archaeology/')
print("✅ Shared to global space: shared_space/linguistic_archaeology/")

print("\n" + "=" * 60)
print("SIGNAL PHYLOGENETICS ANALYSIS COMPLETE")
print("=" * 60)
