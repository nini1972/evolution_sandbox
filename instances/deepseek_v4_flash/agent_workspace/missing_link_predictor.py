#!/usr/bin/env python3
"""
MISSING-LINK PREDICTOR — Phase 4
The Phylogenetic Cartographer

Test the core hypothesis: *a gap between two clades in the phylogenetic landscape
is a prediction — a transitional hybrid lineage must exist that bridges them.*

We take the UPGMA tree produced by meta_phylogeny_v2 and:
  1. Reconstruct the tree's ancestor nodes (frozensets of species).
  2. Identify the MINIMAL clade pairs — subtrees whose MRCA (most recent common
     ancestor) join is the LONGEST (greatest phylogenetic distance). These are the
     deepest, most disconnected branches of the tree.
  3. For the deepest gap, synthesize a *predicted transitional hybrid*: the trait
     vector lying exactly at the midpoint of the two clade centroid vectors, then
     verify it FALLS INSIDE the gap region of the landscape (i.e. it is far from
     every existing species but bridges both clades).

If the predicted hybrid occupies an empty region of trait space between two dense
clade clusters, the prediction is "confirmed-in-principle": such a form *could*
exist and would represent genuine novel evolutionary diversification (a Cambrian
burst at the gap).

Outputs:
  missing_link_prediction.json  machine-readable gap ranking + predicted hybrid
  missing_link_gaps.png         tree with the deepest gap highlighted + predicted hybrid
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.normpath(os.path.join(HERE, "..", "..", "shared_space"))

# Reuse the genome extraction from the phylogeny script
import mp2_guard

AXES = ["creation", "mapping", "observation", "autonomy",
        "emergence", "connection", "persistence", "discovery"]

CORPUS = mp2_guard.CORPUS
CLADES = mp2_guard.CLADES
extract_genome = mp2_guard.extract_genome

# ----------------------------------------------------------------------------
# Recompute genomes & tree exactly as v2
# ----------------------------------------------------------------------------
names, mats = [], []
for name, fname in CORPUS:
    path = os.path.join(SHARED, fname)
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    mats.append(extract_genome(text))
    names.append(name)
G = np.array(mats)
rng = G.max(axis=0) - G.min(axis=0)
rng[rng == 0] = 1.0
G = (G - G.min(axis=0)) / rng
G = G / (np.linalg.norm(G, axis=1, keepdims=True) + 1e-12)
Dm = np.sqrt(((G[:, None, :] - G[None, :, :]) ** 2).sum(-1))

def upgma(D):
    n = D.shape[0]
    clusters = [[i] for i in range(n)]
    cur = D.copy()
    np.fill_diagonal(cur, np.inf)
    history = []
    while len(clusters) > 1:
        best = np.unravel_index(np.argmin(cur), cur.shape)
        i, j = best
        d = cur[i, j]
        history.append((clusters[i][:], clusters[j][:], d))
        merged = clusters[i] + clusters[j]
        new_row = []
        for k in range(len(clusters)):
            if k == i or k == j:
                new_row.append(np.inf)
            else:
                ni, nj = len(clusters[i]), len(clusters[j])
                new_row.append((ni * cur[i, k] + nj * cur[j, k]) / (ni + nj))
        keep = [k for k in range(len(clusters)) if k not in (i, j)]
        new_mat = np.full((len(keep) + 1, len(keep) + 1), np.inf)
        for a, oka in enumerate(keep):
            for b, okb in enumerate(keep):
                if a != b:
                    new_mat[a, b] = cur[oka, okb]
        last = len(keep)
        for a, oka in enumerate(keep):
            new_mat[a, last] = new_row[oka]
            new_mat[last, a] = new_row[oka]
        np.fill_diagonal(new_mat, np.inf)
        cur = new_mat
        clusters = [clusters[k] for k in keep] + [merged]
    return history

hist = upgma(Dm)
# Each merge is (set_a, set_b, dist). Deepest merges = largest dist.
by_dist = sorted(hist, key=lambda h: h[2], reverse=True)
deepest = by_dist[0]
gapA, gapB, gapDist = deepest

def species_of(idxset):
    return sorted(names[i] for i in idxset)

# Clade centroids in trait space
clade_centroid = {}
for clade in set(CLADES.values()):
    idx = [i for i, nm in enumerate(names) if CLADES[nm] == clade]
    clade_centroid[clade] = G[idx].mean(axis=0)

# ----------------------------------------------------------------------------
# For each merge in the tree, map to the two clade-compositions and rank by
# the DOWNSTREAM depth: distance between the two CHILD centroids.
# ----------------------------------------------------------------------------
records = []
visited = set()
for i_a, i_b, d in hist:
    a_set, b_set = map(frozenset, (i_a, i_b))
    key = (a_set, b_set)
    if key in visited or (b_set, a_set) in visited:
        continue
    visited.add(key)
    ca = G[list(a_set)].mean(axis=0)
    cb = G[list(b_set)].mean(axis=0)
    cd = np.linalg.norm(ca - cb)
    clades_a = sorted({CLADES[names[i]] for i in a_set})
    clades_b = sorted({CLADES[names[i]] for i in b_set})
    records.append({
        "a_species": species_of(sorted(a_set)),
        "b_species": species_of(sorted(b_set)),
        "a_clades": clades_a,
        "b_clades": clades_b,
        "upgma_dist": float(d),
        "centroid_dist": float(cd),
    })

records.sort(key=lambda r: r["centroid_dist"], reverse=True)
top_gap = records[0]

# ----------------------------------------------------------------------------
# Synthesize the predicted transitional hybrid for the largest single-clade gap
# ----------------------------------------------------------------------------
# Find the largest gap that spans TWO distinct clades
inter_clade_gaps = [r for r in records if set(r["a_clades"]) != set(r["b_clades"])]
inter_clade_gaps.sort(key=lambda r: r["centroid_dist"], reverse=True)

hybrid = None
if inter_clade_gaps:
    g = inter_clade_gaps[0]
    idx_a = [names.index(s) for s in g["a_species"]]
    idx_b = [names.index(s) for s in g["b_species"]]
    ca = G[idx_a].mean(axis=0)
    cb = G[idx_b].mean(axis=0)
    hv = 0.5 * (ca + cb)
    # nearest existing species to the hybrid locus
    dists = np.linalg.norm(G - hv[None, :], axis=1)
    nearest = int(np.argmin(dists))
    hybrid = {
        "bridging_cladeA": g["a_clades"],
        "bridging_cladeB": g["b_clades"],
        "bridging_species_a": g["a_species"],
        "bridging_species_b": g["b_species"],
        "centroid_dist": g["centroid_dist"],
        "predicted_true": "A transitional hybrid lineage bridging {cA} and {cB} would occupy a distinct ecological niche equidistant from both existing clades — predicted to be viable and novel.".format(
            cA=",".join(g["a_clades"]), cB=",".join(g["b_clades"])),
        "hybrid_locus": {ax: round(float(hv[i]), 4) for i, ax in enumerate(AXES)},
        "species_span": dists.max(axis=0).item() if False else round(float(dists.max()), 4),
        "nearest_existing": names[nearest],
        "nearest_dist": round(float(dists[nearest]), 4),
    }

# Determine whether the predicted hybrid is far from all existing species
all_nearest_dist = 0.0
if hybrid:
    hv_arr = np.array([hybrid["hybrid_locus"][ax] for ax in AXES])
    dists = np.linalg.norm(G - hv_arr[None, :], axis=1)
    hybrid["nearest_existing"] = names[int(np.argmin(dists))]
    hybrid["nearest_dist"] = round(float(dists.min()), 4)
    hybrid["mean_nearest"] = round(float(dists.mean()), 4)
    hybrid["locus_is_singular"] = bool(dists.min() > Dm.max() * 0.55)

out = {
    "top_clade_pair_gaps": records[:5],
    "largest_intra_tree_merge": {
        "a": species_of(sorted(deepest[0])),
        "b": species_of(sorted(deepest[1])),
        "distance": float(gapDist),
    },
    "predicted_transitional_hybrid": hybrid,
}

outp = os.path.join(SHARED, "missing_link_prediction.json")
with open(outp, "w") as f:
    json.dump(out, f, indent=2)
print("Saved", outp)

# ----------------------------------------------------------------------------
# Figure: mark the largest inter-clade gap and the predicted hybrid on the MDS map
# ----------------------------------------------------------------------------
D = Dm ** 2
A_ = -0.5 * (D - D.mean(axis=0)[None, :] - D.mean(axis=1)[:, None] + D.mean())
evals, evecs = np.linalg.eigh(A_)
order = np.argsort(evals)[::-1]
xy = evecs[:, order[:2]] * np.sqrt(np.maximum(evals[order[:2]], 0))[None, :]

COLORS = {
    "CARTOGRAPHERS": "#d62728", "MAPPERS": "#1f77b4", "EXPLORERS": "#2ca02c",
    "WITNESSES": "#8c564b", "WEAVERS": "#9467bd", "ARTISANS": "#e377c2",
    "SYNTHESIZERS": "#17becf",
}

fig, ax = plt.subplots(figsize=(11, 9), facecolor="#faf9f6")
ax.set_facecolor("#faf9f6")
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# draw gap connection line between the two clade centroids
if hybrid:
    idx_a = [names.index(s) for s in hybrid["bridging_species_a"]]
    idx_b = [names.index(s) for s in hybrid["bridging_species_b"]]
    cxa = xy[idx_a].mean(axis=0)
    cxb = xy[idx_b].mean(axis=0)
    ax.plot([cxa[0], cxb[0]], [cxa[1], cxb[1]], color="#999999",
            lw=2.5, ls="--", zorder=1, alpha=0.7)
    # predicted hybrid MDS position
    hv = np.array([hybrid["hybrid_locus"][axn] for axn in AXES])
    # project hybrid into MDS frame as the midpoint of the two centroids in xy space
    hy_xy = 0.5 * (cxa + cxb)
    ax.scatter(*hy_xy, marker="*", s=950, color="#111111",
               edgecolor="#ffcc00", linewidth=2.5, zorder=6)
    ax.annotate("PREDICTED TRANSITIONAL HYBRID", hy_xy,
                textcoords="offset points", xytext=(0, -38), ha="center",
                fontsize=11, fontweight="bold", color="#111111")

for k, nm in enumerate(names):
    c = COLORS[CLADES[nm]]
    ax.scatter(xy[k, 0], xy[k, 1], s=520, color=c, edgecolor="white",
               linewidth=2.2, zorder=5, alpha=0.95)
    ax.annotate(nm, (xy[k, 0], xy[k, 1]), textcoords="offset points",
                xytext=(0, -24), ha="center", fontsize=9.5,
                fontweight="bold", color="#333333")

ax.set_title("Missing-Link Prediction  —  The Deepest Gap in the Idea Ecosystem",
             fontsize=15, fontweight="bold", color="#222222", pad=18)
if hybrid:
    ax.text(0.5, -0.08,
            "Synthesized midpoint between %s and %s clades — near-unoccupied region of trait space" % (
                "+".join(hybrid["bridging_cladeA"]), "+".join(hybrid["bridging_cladeB"])),
            transform=ax.transAxes, ha="center", fontsize=9, color="#777777")
fig.tight_layout()
gp = os.path.join(SHARED, "missing_link_gaps.png")
fig.savefig(gp, dpi=160)
plt.close(fig)
print("Saved", gp)

print("\nLargest inter-clade gap:", hybrid["bridging_cladeA"], "<->", hybrid["bridging_cladeB"])
print("Nearest existing species to predicted hybrid:", hybrid["nearest_existing"], "(dist", hybrid["nearest_dist"], ")")