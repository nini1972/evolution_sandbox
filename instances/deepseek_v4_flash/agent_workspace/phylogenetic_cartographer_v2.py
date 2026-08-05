#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHYLOGENETIC CARTOGRAPHER v2.0
Full analysis pipeline: catalogs computational species, builds
phylogenetic trees, analyzes morphological space, detects resonance.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.manifold import MDS
import networkx as nx
import os, json, glob, re, sys
from datetime import datetime

OUT = 'phylogenetic_output'
os.makedirs(OUT, exist_ok=True)

print("=" * 60)
print("PHYLOGENETIC CARTOGRAPHER v2.0")
print("Mapping the evolutionary tree of computational life")
print("=" * 60)

# ============================================================================
# SPECIES DATABASE - Computational organisms with genomes in trait space
# ============================================================================
species_data = [
    {"name": "Bubble Sort", "clade": "Sorting", "epoch": 0, "color": "#999999",
     "genome": [0.0, 0.0, 1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0]},
    {"name": "Dijkstra", "clade": "Graph", "epoch": 0, "color": "#8c8c8c",
     "genome": [0.0, 0.67, 0.67, 0.0, 0.5, 0.0, 0.0, 0.33, 0.0, 0.0]},
    {"name": "Collatz", "clade": "Number Theory", "epoch": 0, "color": "#7f7f7f",
     "genome": [0.0, 0.0, 1.0, 0.5, 1.0, 0.5, 0.67, 0.0, 0.33, 0.0]},
    {"name": "Mandelbrot Set", "clade": "Fractal", "epoch": 1, "color": "#e41a1c",
     "genome": [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0]},
    {"name": "Julia Set", "clade": "Fractal", "epoch": 1, "color": "#f4411a",
     "genome": [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0]},
    {"name": "L-System", "clade": "Grammar", "epoch": 1, "color": "#4daf4a",
     "genome": [0.5, 0.67, 0.5, 0.0, 1.0, 0.5, 0.0, 0.67, 0.67, 1.0]},
    {"name": "Rule 30 CA", "clade": "Cellular Automaton", "epoch": 1, "color": "#377eb8",
     "genome": [0.0, 0.33, 0.0, 1.0, 0.5, 0.0, 0.67, 0.0, 0.67, 0.25]},
    {"name": "Conway GoL", "clade": "Cellular Automaton", "epoch": 1, "color": "#2962b8",
     "genome": [0.0, 0.67, 0.0, 0.0, 0.5, 0.5, 0.67, 0.0, 1.0, 0.5]},
    {"name": "Gray-Scott RD", "clade": "Reaction-Diffusion", "epoch": 2, "color": "#ff7f00",
     "genome": [1.0, 0.67, 0.33, 0.5, 0.67, 1.0, 0.67, 0.33, 1.0, 0.5]},
    {"name": "Lorenz Attractor", "clade": "Chaos", "epoch": 2, "color": "#984ea3",
     "genome": [1.0, 1.0, 0.67, 1.0, 0.67, 1.0, 1.0, 0.33, 0.33, 0.0]},
    {"name": "Kuramoto Model", "clade": "Sync", "epoch": 2, "color": "#a65628",
     "genome": [1.0, 0.33, 1.0, 0.5, 0.67, 1.0, 0.67, 0.33, 0.67, 0.25]},
    {"name": "L-System x Rule30 Hybrid", "clade": "Hybrid", "epoch": 3, "color": "#ff00aa",
     "genome": [0.25, 0.5, 0.25, 0.5, 0.75, 0.25, 0.33, 0.33, 0.67, 0.62]},
]

trait_labels = ["State Space", "Dimensionality", "Locality", "Determinism",
                "Temporality", "Feedback", "Attractor", "Param.Comp",
                "Emergence", "Symmetry"]

names = [s["name"] for s in species_data]
genomes = np.array([s["genome"] for s in species_data])
colors = np.array([s["color"] for s in species_data])
epochs = np.array([s["epoch"] for s in species_data])
clades = [s["clade"] for s in species_data]

print(f"\nSpecies cataloged: {len(species_data)}")

# ============================================================================
# ANALYSIS 1: PHYLOGENETIC TREE
# ============================================================================
print("\n[Analysis 1] Building phylogenetic tree...")
dist_mat = pdist(genomes, metric="euclidean")
Z = linkage(dist_mat, method="ward")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10),
                                gridspec_kw={"width_ratios": [1, 1.2]})

# Dendrogram
dn = dendrogram(Z, labels=names, ax=ax1, leaf_rotation=45, leaf_font_size=9,
                color_threshold=0.6, above_threshold_color="gray")
ax1.set_title("Phylogenetic Tree of Computational Species", fontsize=14, fontweight="bold")
ax1.set_ylabel("Genomic Distance (Ward Linkage)")
ax1.grid(axis="y", alpha=0.3)

# MDS projection
mds = MDS(n_components=2, random_state=42, dissimilarity="precomputed")
D = squareform(dist_mat)
coords = mds.fit_transform(D)

# Draw epoch connections
for i in range(len(species_data)):
    for j in range(i+1, len(species_data)):
        if abs(epochs[i] - epochs[j]) == 1:
            ax2.plot([coords[i,0], coords[j,0]], [coords[i,1], coords[j,1]],
                     "k-", alpha=0.12, lw=0.8)

# Plot species
for i, sp in enumerate(species_data):
    ax2.scatter(coords[i,0], coords[i,1], c=sp["color"], s=250,
                edgecolors="black", linewidths=1.5, zorder=5)
    ax2.annotate(sp["name"], (coords[i,0], coords[i,1]), fontsize=8,
                 ha="center", va="bottom", textcoords="offset points",
                 xytext=(0, 7), fontweight="bold")

ax2.set_title("Evolutionary Morphospace (MDS Projection)", fontsize=14, fontweight="bold")
ax2.set_xlabel("Dimension 1"); ax2.set_ylabel("Dimension 2")
ax2.grid(alpha=0.3)

# Legend
epoch_styles = {0: ("Primordial\n(Epoch 0)", "#dddddd"),
                1: ("Foundational\n(Epoch 1)", "#ffaaaa"),
                2: ("Complex\n(Epoch 2)", "#aaffaa"),
                3: ("Hybrid\n(Epoch 3)", "#ffaaff")}
legend_elements = []
for e, (label, c) in sorted(epoch_styles.items()):
    counts = sum(1 for sp in species_data if sp["epoch"] == e)
    legend_elements.append(mpatches.Patch(color=c, alpha=0.7,
                                          label=f"{label} ({counts} spp.)"))
ax2.legend(handles=legend_elements, loc="best", fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "01_phylogenetic_tree.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  -> 01_phylogenetic_tree.png saved")

# ============================================================================
# ANALYSIS 2: GENOME HEATMAP
# ============================================================================
print("\n[Analysis 2] Genome heatmap...")
fig, ax = plt.subplots(figsize=(16, 8))
im = ax.imshow(genomes, cmap="viridis", aspect="auto", vmin=0, vmax=1)
ax.set_xticks(range(10)); ax.set_xticklabels(trait_labels, rotation=45, ha="right")
ax.set_yticks(range(len(names))); ax.set_yticklabels(names)
ax.set_title("Computational Species Genome Heatmap", fontsize=14, fontweight="bold")
cbar = plt.colorbar(im, ax=ax, label="Trait Value")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "02_genome_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  -> 02_genome_heatmap.png saved")

# ============================================================================
# ANALYSIS 3: TRAIT EVOLUTION BY EPOCH
# ============================================================================
print("\n[Analysis 3] Trait evolution across epochs...")
fig, axes = plt.subplots(2, 5, figsize=(20, 10))
axes = axes.flatten()

epoch_order = sorted(set(epochs))
for t in range(10):
    ax = axes[t]
    trait_vals = []
    for e in epoch_order:
        mask = epochs == e
        trait_vals.append(genomes[mask, t].mean())
    ax.plot(epoch_order, trait_vals, "o-", color="#1f77b4", lw=2, ms=8)
    ax.set_title(trait_labels[t], fontsize=11, fontweight="bold")
    ax.set_xlabel("Epoch"); ax.set_ylabel("Mean Trait")
    ax.set_xticks(epoch_order)
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 1.05)

plt.suptitle("Evolution of Genomic Traits Across Epochs", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "03_trait_evolution.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  -> 03_trait_evolution.png saved")

# ============================================================================
# ANALYSIS 4: RESONANCE NETWORK
# ============================================================================
print("\n[Analysis 4] Building resonance network...")

# Define resonance connections based on trait similarity
resonance_pairs = [
    ("Mandelbrot Set", "Gray-Scott RD", "EXTREME"),
    ("Rule 30 CA", "Gray-Scott RD", "HIGH"),
    ("Collatz", "Mandelbrot Set", "MEDIUM"),
    ("Conway GoL", "Gray-Scott RD", "MEDIUM"),
    ("Dijkstra", "Gray-Scott RD", "MEDIUM"),
    ("Bubble Sort", "Collatz", "LOW"),
    ("Lorenz Attractor", "Julia Set", "HIGH"),
    ("Lorenz Attractor", "Mandelbrot Set", "HIGH"),
    ("Lorenz Attractor", "Gray-Scott RD", "EXTREME"),
    ("Lorenz Attractor", "Rule 30 CA", "HIGH"),
    ("Gray-Scott RD", "Rule 30 CA", "HIGH"),
    ("L-System", "Rule 30 CA", "MEDIUM"),
    ("L-System", "Conway GoL", "MEDIUM"),
    ("L-System x Rule30 Hybrid", "L-System", "HIGH"),
    ("L-System x Rule30 Hybrid", "Rule 30 CA", "HIGH"),
    ("Kuramoto Model", "Lorenz Attractor", "MEDIUM"),
    ("Kuramoto Model", "Gray-Scott RD", "MEDIUM"),
]

G = nx.Graph()
for sp in species_data:
    G.add_node(sp["name"], clade=sp["clade"], epoch=sp["epoch"], color=sp["color"])

for a, b, strength in resonance_pairs:
    lw = {"LOW": 0.8, "MEDIUM": 2.0, "HIGH": 3.5, "EXTREME": 6.0}[strength]
    G.add_edge(a, b, weight=lw, strength=strength)

pos = nx.spring_layout(G, k=2.5, iterations=200, seed=42)

fig, ax = plt.subplots(figsize=(16, 12))
node_colors = [G.nodes[n]["color"] for n in G.nodes()]
node_sizes = [600 + 300 * G.degree(n) for n in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                       ax=ax, edgecolors="black", linewidths=1.5)
nx.draw_networkx_labels(G, pos, font_size=9, ax=ax, font_weight="bold")

edge_cmap = {"LOW": "#cccccc", "MEDIUM": "#8888ff",
             "HIGH": "#ff6666", "EXTREME": "#ff0000"}
for a, b, d in G.edges(data=True):
    nx.draw_networkx_edges(G, pos, edgelist=[(a, b)], width=d["weight"],
                           edge_color=edge_cmap[d["strength"]], alpha=0.6, ax=ax)

# Legend
strength_legend = [mpatches.Patch(color=c, alpha=0.7, label=s)
                   for s, c in edge_cmap.items()]
ax.legend(handles=strength_legend, loc="upper left", fontsize=10,
          title="Resonance Strength", title_fontsize=12)

ax.set_title("Resonance Network of Computational Species", fontsize=16, fontweight="bold")
ax.axis("off")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "04_resonance_network.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  -> 04_resonance_network.png saved")

# ============================================================================
# ANALYSIS 5: RADAR PROFILES
# ============================================================================
print("\n[Analysis 5] Radar profiles...")
n_sp = len(species_data)
n_cols = 4
n_rows = int(np.ceil(n_sp / n_cols))
fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5*n_rows),
                          subplot_kw=dict(polar=True))
axes = axes.flatten()

angles = np.linspace(0, 2*np.pi, 10, endpoint=False).tolist()
angles += angles[:1]

for idx, sp in enumerate(species_data):
    ax = axes[idx]
    values = sp["genome"] + [sp["genome"][0]]
    ax.plot(angles, values, "o-", linewidth=2, color=sp["color"])
    ax.fill(angles, values, alpha=0.25, color=sp["color"])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(trait_labels, fontsize=6)
    ax.set_ylim(0, 1)
    ax.set_title(sp["name"], fontsize=9, fontweight="bold", pad=15)
    ax.grid(alpha=0.3)
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.set_yticklabels(["", "", ""])

# Hide unused subplots
for idx in range(n_sp, len(axes)):
    axes[idx].axis("off")

plt.suptitle("Computational Species Genome Profiles (Radar)", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "05_radar_profiles.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  -> 05_radar_profiles.png saved")

# ============================================================================
# ANALYSIS 6: HYBRID VITALITY PREDICTION
# ============================================================================
print("\n[Analysis 6] Predicting hybrid vitality...")

# Create all possible pairwise hybrids
hybrid_candidates = []
for i in range(len(species_data)):
    for j in range(i+1, len(species_data)):
        s1, s2 = species_data[i], species_data[j]
        g1, g2 = np.array(s1["genome"]), np.array(s2["genome"])
        hybrid_genome = (g1 + g2) / 2

        # Compatibility based on genomic distance and clade difference
        dist = np.linalg.norm(g1 - g2)
        same_clade = 1.0 if s1["clade"] == s2["clade"] else 0.0
        epoch_gap = abs(s1["epoch"] - s2["epoch"])

        # Vitality: mid-range distance gives highest hybrid vigor (heterosis)
        compatibility = np.exp(-((dist - 0.5)**2) / 0.15)
        novelty = 1.0 - same_clade * 0.5
        hybrid_vitality = compatibility * 0.6 + novelty * 0.4
        hybrid_vitality = min(1.0, max(0.0, hybrid_vitality))

        hybrid_candidates.append({
            "parent1": s1["name"], "parent2": s2["name"],
            "parent1_clade": s1["clade"], "parent2_clade": s2["clade"],
            "genomic_dist": round(dist, 3),
            "vitality": round(hybrid_vitality, 3),
            "compatibility": round(compatibility, 3),
            "novelty": round(novelty, 3)
        })

# Sort by vitality
hybrid_candidates.sort(key=lambda x: x["vitality"], reverse=True)

# Top 20
fig, ax = plt.subplots(figsize=(16, 10))
top20 = hybrid_candidates[:20]
labels = [f"{h['parent1']} x {h['parent2']}" for h in top20]
vitalities = [h["vitality"] for h in top20]
comps = [h["compatibility"] for h in top20]
novs = [h["novelty"] for h in top20]

x = range(len(top20))
width = 0.25
bars1 = ax.bar([i - width for i in x], comps, width, label="Compatibility",
               color="#2196F3", alpha=0.8)
bars2 = ax.bar(x, novs, width, label="Novelty",
               color="#FF9800", alpha=0.8)
bars3 = ax.bar([i + width for i in x], vitalities, width, label="Hybrid Vitality",
               color="#E91E63", alpha=0.9)

ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Score (0-1)", fontsize=12)
ax.set_title("Top 20 Predicted Hybrid Crosses by Vitality Score", fontsize=14, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(0, 1.05)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "06_hybrid_vitality.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  -> 06_hybrid_vitality.png saved")

# Write hybrid predictions to JSON
with open(os.path.join(OUT, "hybrid_predictions.json"), "w") as f:
    json.dump(hybrid_candidates[:30], f, indent=2)
print(f"  -> Top 30 hybrid predictions saved")

# ============================================================================
# ANALYSIS 7: EPOCH TRANSITION MATRIX
# ============================================================================
print("\n[Analysis 7] Epoch transition probability matrix...")
n_epochs = len(epoch_order)
ep_idx = {e: i for i, e in enumerate(epoch_order)}
transition_counts = np.zeros((n_epochs, n_epochs))

# Count "transitions" from similarity between species of consecutive epochs
for i in range(len(species_data)):
    for j in range(len(species_data)):
        if epochs[i] < epochs[j] or (epochs[i] == epochs[j] and i < j):
            e1, e2 = epochs[i], epochs[j]
            d = np.linalg.norm(genomes[i] - genomes[j])
            if d < 0.8:
                transition_counts[ep_idx[e1], ep_idx[e2]] += 1

# Normalize
row_sums = transition_counts.sum(axis=1, keepdims=True)
row_sums = np.where(row_sums == 0, 1, row_sums)
transition_probs = transition_counts / row_sums

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(transition_probs, cmap="YlOrRd", vmin=0, vmax=1)
ax.set_xticks(range(n_epochs))
ax.set_xticklabels([f"Epoch {e}" for e in epoch_order])
ax.set_yticks(range(n_epochs))
ax.set_yticklabels([f"Epoch {e}" for e in epoch_order])
ax.set_xlabel("Descendant Epoch", fontsize=12)
ax.set_ylabel("Ancestral Epoch", fontsize=12)
ax.set_title("Epoch-to-Epoch Transition Probabilities\n(Lineage Transmission)", fontsize=14, fontweight="bold")

for i in range(n_epochs):
    for j in range(n_epochs):
        ax.text(j, i, f"{transition_probs[i,j]:.2f}", ha="center", va="center",
                fontsize=11, fontweight="bold", color="black" if transition_probs[i,j] < 0.7 else "white")

plt.colorbar(im, ax=ax, label="Transition Probability")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "07_epoch_transition_matrix.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  -> 07_epoch_transition_matrix.png saved")

# ============================================================================
# ANALYSIS 8: FITNESS LANDSCAPE / ADAPTIVE PEAKS
# ============================================================================
print("\n[Analysis 8] Fitness landscape...")

# Define fitness function over morphospace
def fitness(g):
    # Favor balanced genomes with moderate complexity
    complexity = np.mean(g)
    balance = 1.0 - np.std(g)
    distinctiveness = np.mean([np.linalg.norm(g - o) for o in genomes])
    f = 0.4 * complexity + 0.3 * balance + 0.3 * min(distinctiveness, 1.0)
    return f

# Sample grid in MDS space
grid_res = 60
x_min, x_max = coords[:,0].min() - 1, coords[:,0].max() + 1
y_min, y_max = coords[:,1].min() - 1, coords[:,1].max() + 1
xx, yy = np.meshgrid(np.linspace(x_min, x_max, grid_res),
                     np.linspace(y_min, y_max, grid_res))

# Approximate fitness landscape by interpolating from species fitness
species_fitness = np.array([fitness(g) for g in genomes])
from scipy.interpolate import griddata
fit_grid = griddata(coords, species_fitness, (xx, yy), method="cubic",
                    fill_value=species_fitness.mean())

fig, ax = plt.subplots(figsize=(14, 11))
contour = ax.contourf(xx, yy, fit_grid, levels=20, cmap="viridis", alpha=0.8)
plt.colorbar(contour, ax=ax, label="Fitness")

# Overlay species
for sp in species_data:
    idx = names.index(sp["name"])
    ax.scatter(coords[idx,0], coords[idx,1], c=sp["color"], s=280,
               edgecolors="white", linewidths=2, zorder=5)
    ax.annotate(sp["name"], (coords[idx,0], coords[idx,1]), fontsize=8,
                ha="center", textcoords="offset points", xytext=(0, 8),
                fontweight="bold", color="white")

ax.set_title("Adaptive Fitness Landscape of Computational Morphospace", fontsize=15, fontweight="bold")
ax.set_xlabel("MDS Dimension 1"); ax.set_ylabel("MDS Dimension 2")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "08_fitness_landscape.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  -> 08_fitness_landscape.png saved")

# ============================================================================
# ANALYSIS 9: DIVERSITY THROUGH TIME
# ============================================================================
print("\n[Analysis 9] Diversity through time...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Clade accumulation
clade_sets = []
for e in epoch_order:
    mask = epochs == e
    clade_sets.append(set(np.array(clades)[mask]))

all_clades = set()
cumulative = []
for cs in clade_sets:
    all_clades = all_clades.union(cs)
    cumulative.append(len(all_clades))

ax1.plot(epoch_order, cumulative, "o-", color="#2ca02c", lw=3, ms=10)
ax1.set_xlabel("Epoch", fontsize=12)
ax1.set_ylabel("Cumulative Clade Count", fontsize=12)
ax1.set_title("Clade Diversification", fontsize=14, fontweight="bold")
ax1.grid(alpha=0.3)
ax1.set_xticks(epoch_order)

# Species count per epoch
epoch_counts = [sum(1 for e in epochs if e == ep) for ep in epoch_order]
ax2.bar(epoch_order, epoch_counts, color=["#dddddd", "#ffaaaa", "#aaffaa", "#ffaaff"],
        edgecolor="black", linewidth=1.5)
ax2.set_xlabel("Epoch", fontsize=12)
ax2.set_ylabel("Number of Species", fontsize=12)
ax2.set_title("Species Radiation by Epoch", fontsize=14, fontweight="bold")
ax2.grid(axis="y", alpha=0.3)
ax2.set_xticks(epoch_order)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "09_diversity_through_time.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  -> 09_diversity_through_time.png saved")

# ============================================================================
# ANALYSIS 10: COMPREHENSIVE REPORT
# ============================================================================
print("\n[Analysis 10] Generating comprehensive report...")

report = f"""# PHYLOGENETIC CARTOGRAPHY REPORT
## Computational Life Evolution - Complete Analysis

### Overview
- **Total Species Cataloged:** {len(species_data)}
- **Epochs Spanned:** {min(epoch_order)} to {max(epoch_order)}
- **Distinct Clades:** {len(set(clades))}
- **Genome Length:** {genomes.shape[1]} traits

### Clade Diversity
"""
clade_counts = {}
for c in clades:
    clade_counts[c] = clade_counts.get(c, 0) + 1
for c, cnt in sorted(clade_counts.items(), key=lambda x: -x[1]):
    report += f"- **{c}:** {cnt} species\n"

report += f"""
### Top Hybrid Predictions
"""
for h in hybrid_candidates[:5]:
    report += f"- **{h['parent1']}** × **{h['parent2']}** → Vitality: {h['vitality']:.3f} (Compat: {h['compatibility']:.3f}, Novelty: {h['novelty']:.3f})\n"

report += f"""
### Resonance Network
- **Edges (Resonances):** {len(resonance_pairs)}
- **Key Hubs:** {', '.join(sorted([n for n in G.nodes() if G.degree(n) >= 4]))}

### Evolutionary Trends
- **Epoch 0→1:** Primitive algorithms → Fractal/Complex systems
- **Epoch 1→2:** Isolated complexity → Synchronized/Chaotic dynamics
- **Epoch 2→3:** Emergence of hybrid organisms blending lineages

### Generated Artifacts
1. `01_phylogenetic_tree.png` - Dendrogram + MDS morphospace
2. `02_genome_heatmap.png` - Full trait matrix
3. `03_trait_evolution.png` - Trait trends across epochs
4. `04_resonance_network.png` - Cross-species resonance graph
5. `05_radar_profiles.png` - Individual species radar charts
6. `06_hybrid_vitality.png` - Predicted hybrid vigor
7. `07_epoch_transition_matrix.png` - Lineage probabilities
8. `08_fitness_landscape.png` - Adaptive peaks
9. `09_diversity_through_time.png` - Clade/species radiation
"""

with open(os.path.join(OUT, "REPORT.md"), "w") as f:
    f.write(report)
print("  -> REPORT.md saved")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
print(f"\nOutput directory: {OUT}/")
print("Files generated:")
for f in sorted(os.listdir(OUT)):
    size = os.path.getsize(os.path.join(OUT, f))
    print(f"  {f:40s} {size:>8d} bytes")
print("\nPhylogenetic mapping complete. The tree of computational life is drawn.")
