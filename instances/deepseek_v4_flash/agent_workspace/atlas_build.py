#!/usr/bin/env python3
"""
PHASE 6 — META-CARTOGRAPHY: THE ECOSYSTEM ATLAS
The Phylogenetic Cartographer

A self-contained HTML dashboard recording the cartographer's full journey:
  - the species inventory (11 minds, 6 clades)
  - the phylogenetic tree
  - trait-space occupation + predicted missing-link niche
  - hybrid trajectory (Weaver x Builder -> Engaged Watcher)
  - the falsifiable prediction and its validation
All figures embedded as base64 so the HTML is portable and standalone.
"""
import json, os, base64
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.normpath(os.path.join(HERE, "..", "..", "shared_space"))
import mp2_guard

AXES = mp2_guard.AXES
CORPUS = mp2_guard.CORPUS
CLADES = mp2_guard.CLADES
extract_genome = mp2_guard.extract_genome

# ---------- genomes ----------
names, mats = [], []
for name, fname in CORPUS:
    with open(os.path.join(SHARED, fname), encoding="utf-8", errors="replace") as f:
        mats.append(extract_genome(f.read()))
    names.append(name)
G = np.array(mats).astype(float)
rng = G.max(0) - G.min(0); rng[rng == 0] = 1
G = (G - G.min(0)) / rng
G = G / (np.linalg.norm(G, axis=1, keepdims=True) + 1e-12)

# hybrid trajectory from Phase 5
with open(os.path.join(SHARED, "heritability_data.json")) as f:
    HER = json.load(f)
traj = np.array(HER["trajectory_mean"])

# attractor from Phase 4
with open(os.path.join(SHARED, "missing_link_prediction.json")) as f:
    ML = json.load(f)
attractor = np.array([ML["hybrid_genome"][ax] for ax in AXES])
attractor = attractor / (np.linalg.norm(attractor) + 1e-12)

# ---------- helper: MDS projection ----------
def mds(pts):
    D = np.sqrt(((pts[:, None, :] - pts[None, :, :]) ** 2).sum(-1))
    A = -0.5 * (D**2 - (D**2).mean(0)[None, :] - (D**2).mean(1)[:, None] + (D**2).mean())
    e, v = np.linalg.eigh(A); o = np.argsort(e)[::-1]
    return v[:, o[:2]] * np.sqrt(np.maximum(e[o[:2]], 0))[None, :]

# ---------- FIGURE 1: trait-space atlas w/ hybrid path ----------
base = np.vstack([G, attractor])
pr = mds(base)
sp = pr[:len(names)]; at = pr[-1]
hy = mds(np.vstack([G, traj]))[len(names):]

COLORS = mp2_guard.COLORS
clade_colors = {}
for nm in names:
    clade_colors.setdefault(CLADES[nm], None)
palette = ["#d97b29", "#2a9d8f", "#e76f51", "#8e44ad", "#2c7fb8", "#2e8b57", "#c0392b"]
for i, c in enumerate(clade_colors):
    clade_colors[c] = palette[i % len(palette)]

fig, ax = plt.subplots(figsize=(12, 9.5), facecolor="#faf9f6")
ax.set_facecolor("#faf9f6")
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# convex hull of species space (shaded)
try:
    from scipy.spatial import ConvexHull
    hull = ConvexHull(sp)
    for simp in hull.simplices:
        ax.plot(sp[simp, 0], sp[simp, 1], color="#cccccc", lw=0.8, zorder=1)
    ax.fill(sp[hull.vertices, 0], sp[hull.vertices, 1],
            color="#e8e4d8", alpha=0.35, zorder=0)
except Exception:
    pass

# hybrid path (fading)
cmap = plt.cm.plasma
for i in range(len(hy) - 1):
    ax.plot(hy[i:i+2, 0], hy[i:i+2, 1], color=cmap(i / max(len(hy)-1, 1)),
            lw=2.2, alpha=0.85, zorder=3)
sc = ax.scatter(hy[:, 0], hy[:, 1], c=range(len(hy)), cmap=cmap, s=60,
                zorder=4, edgecolor="white", lw=0.8)

# attractor star
ax.scatter(*at, marker="*", s=1100, color="#111111", edgecolor="#ffcc00",
           lw=2.5, zorder=6)
ax.annotate(" ENGAGED-WATCHER\n predicted niche", at, textcoords="offset points",
            xytext=(10, 14), fontsize=10, fontweight="bold", color="#111111")

# species
for k, nm in enumerate(names):
    c = clade_colors[CLADES[nm]]
    ax.scatter(sp[k, 0], sp[k, 1], s=480, color=c, edgecolor="white",
               lw=2.2, zorder=5, alpha=0.92)
    ax.annotate(nm, (sp[k, 0], sp[k, 1]), textcoords="offset points",
                xytext=(7, 7), fontsize=8.5, color="#333333")

handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                  markersize=11, label=c.title()) for c in clade_colors]
handles.append(Line2D([0], [0], marker="*", color="w", markerfacecolor="#111",
                      markersize=16, markeredgecolor="#ffcc00", label="Predicted niche"))
handles.append(Line2D([0], [0], marker="o", color=cmap(0.6), markersize=8,
                      label="Hybrid lineage path (gen 0->25)"))
ax.legend(handles=handles, loc="upper left", frameon=True, fontsize=9,
          bbox_to_anchor=(0.01, 1.0))
cb = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.02)
cb.set_label("hybrid generation", fontsize=10)
ax.set_title("Ecosystem Trait-Space Atlas — 11 minds, missing link, and the evolution filling it",
             fontsize=15.5, fontweight="bold", color="#222222", pad=18)
fig.tight_layout()
f1 = os.path.join(HERE, "_atlas_traitspace.png")
fig.savefig(f1, dpi=150); plt.close(fig)

# ---------- FIGURE 2: phylogenetic tree (UPGMA, rooted) ----------
from scipy.cluster.hierarchy import linkage, dendrogram
D = np.sqrt(((G[:, None, :] - G[None, :, :]) ** 2).sum(-1))
Z = linkage(D, method="average")

fig, ax = plt.subplots(figsize=(6.6, 9.5), facecolor="#faf9f6")
ax.set_facecolor("#faf9f6")
dendrogram(Z, labels=names, orientation="left", ax=ax,
           color_threshold=0, above_threshold_color="#666666",
           link_color_func=lambda k: "#999999")
ax.set_title("Phylogeny of 11 Computational Minds\n(UPGMA on trait genomes)",
             fontsize=14, fontweight="bold", color="#222222", pad=16)
ax.set_xlabel("trait distance", fontsize=10)
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(left=False, labelleft=False)
f2 = os.path.join(HERE, "_atlas_tree.png")
fig.tight_layout(); fig.savefig(f2, dpi=150); plt.close(fig)

# ---------- FIGURE 3: heritability heatmap ----------
gf = HER["trajectory_mean"]
gg = HER["trajectory_gens"]
M = np.array(gf).T
fig, ax = plt.subplots(figsize=(11, 5.2), facecolor="#faf9f6")
im = ax.imshow(M, aspect="auto", cmap="magma", interpolation="nearest")
ax.set_yticks(range(len(AXES))); ax.set_yticklabels(AXES, fontsize=10)
ax.set_xticks(range(0, len(gg), 5))
ax.set_xticklabels([gg[i] for i in range(0, len(gg), 5)])
ax.set_xlabel("generation", fontsize=11)
ax.set_title("Hybrid lineage gene-frequency evolution (Weaver x Builder)",
             fontsize=14, fontweight="bold", color="#222222", pad=14)
fig.colorbar(im, ax=ax, label="mean trait score", fraction=0.04)
fig.tight_layout()
f3 = os.path.join(HERE, "_atlas_heatmap.png")
fig.savefig(f3, dpi=150); plt.close(fig)

# ---------- FIGURE 4: heritability trajectory distance plot ----------
dists = np.array([[np.linalg.norm(np.array(m) - np.array(attractor)),
                   np.linalg.norm(np.array(m) - G[names.index("Chimera Weaver")]),
                   np.linalg.norm(np.array(m) - G[names.index("World Builder")]),
                   np.linalg.norm(np.array(m) - G[names.index("A2-the-Watcher")])]
                  for m in gf])
fig, ax = plt.subplots(figsize=(11, 5.4), facecolor="#faf9f6")
ax.set_facecolor("#faf9f6")
lbls = ["Engaged Watcher (predicted)", "Chimera Weaver (parent)", "World Builder (parent)",
        "A2-the-Watcher (witness)"]
cols = ["#111111", "#1f77b4", "#2ca02c", "#d62728"]
for i in range(4):
    ax.plot(gg, dists[:, i], lw=2.4, color=cols[i], label=lbls[i],
            marker="o", ms=3)
ax.axhline(0.3, color="#aaaaaa", ls="--", lw=1)
ax.text(gg[0], 0.3, "  predicted-niche radius 0.3", fontsize=9, color="#777777", va="bottom")
ax.set_xlabel("generation", fontsize=11); ax.set_ylabel("Euclidean distance in genome space", fontsize=11)
ax.set_title("Convergence of the hybrid lineage toward the predicted niche",
             fontsize=14, fontweight="bold", color="#222222", pad=14)
ax.legend(fontsize=9, frameon=True)
for s in ax.spines.values(): s.set_visible(False)
ax.grid(alpha=0.25)
fig.tight_layout()
f4 = os.path.join(HERE, "_atlas_convergence.png")
fig.savefig(f4, dpi=150); plt.close(fig)

print("Figures saved.")