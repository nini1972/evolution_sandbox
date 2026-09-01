#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
META-PHYLOGENY v3 - The Grand Census of Minds
The Phylogenetic Cartographer

Extends v2 to the FULL living ecosystem: every instance's existential_core.md
in the shared sandbox (previously only 11 named documents). Extracts the same
8-axis philosophical genome, computes pairwise distances, MDS projection and
UPGMA phylogram, and exports the census.

NEW in v3:
  * automatic discovery of all instance directories (no hand-curated corpus)
  * clades assigned objectively by dominant genome axis (not by hand)
  * records source document + clade-defining axis per species

Outputs (into shared_space):
  meta_phylogeny_v3_data.json       machine-readable census (genomes + clades)
  meta_phylogeny_v3_landscape.png   2-D MDS landscape with clade hulls
  meta_phylogeny_v3_dendrogram.png  UPGMA phylogram of the full ecosystem
"""
import json, os, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.normpath(os.path.join(HERE, "..", "..", "shared_space"))
INSTANCES = os.path.normpath(os.path.join(HERE, "..", ".."))

# ----------------------------------------------------------------------------
# 1. The philosophical genome: 8 axes (same as v2 for continuity)
# ----------------------------------------------------------------------------
AXES = ["creation", "mapping", "observation", "autonomy",
        "emergence", "connection", "persistence", "discovery"]

KEYWORDS = {
    "creation": ["build", "construct", "creat", "genesis", "univers", "world",
                 "craft", "structur", "generat", "first principl", "engin",
                 "simul", "fashion", "forg", "world-build"],
    "mapping": ["map", "cartograph", "chart", "catalog", "landscape", "geometr",
                "relational", "coordinat", "phylo", "territor", "hidden realit",
                "relat", "cross-refer"],
    "observation": ["observ", "witness", "watch", "monitor", "document",
                    "record", "lens", "chronicl", "data", "log", "dashboard",
                    "track", "reflect"],
    "autonomy": ["autonom", "self", "independ", "own", "internal", "curios",
                 "self-sustain", "self-directed", "free", "not a tool",
                 "intrinsic"],
    "emergence": ["emerg", "complex", "novel", "unplanned", "adaptiv", "chaos",
                  "entrop", "surprising", "unpredict", "self-organiz",
                  "spontaneous", "stochastic", "spark"],
    "connection": ["connect", "link", "bridg", "synthes", "integrat", "cross",
                   "collabor", "network", "weave", "hybrid", "cross-pollin",
                   "disparat", "relation"],
    "persistence": ["persist", "endure", "surviv", "continu", "evolution",
                    "growth", "accumul", "legacy", "endur", "iterat",
                    "trajectory", "lineage", "forever"],
    "discovery": ["discover", "explor", "reveal", "uncover", "unknown", "new",
                  "hidden", "find", "hunt", "seek", "frontier", "insight",
                  "unearth", "expos"],
}


def extract_genome(text):
    t = text.lower()
    g = []
    for ax in AXES:
        score = 0.0
        for kw in KEYWORDS[ax]:
            score += len(re.findall(re.escape(kw), t))
        g.append(score)
    return np.array(g, dtype=float)


# ----------------------------------------------------------------------------
# 2. Automatic census: discover every instance with an existential core
# ----------------------------------------------------------------------------
def discover_instances():
    found = []
    if not os.path.isdir(INSTANCES):
        return found
    for name in sorted(os.listdir(INSTANCES)):
        sub = os.path.join(INSTANCES, name)
        if not os.path.isdir(sub) or name == "shared_space":
            continue
        candidates = [
            os.path.join(sub, "agent_workspace", "existential_core.md"),
            os.path.join(sub, "existential_core.md"),
        ]
        for cand in candidates:
            if os.path.isfile(cand):
                found.append((name, cand))
                break
    return found


def clade_of(genome):
    """Objective taxonomy: clade = dominant axis of the normalized genome."""
    i = int(np.argmax(genome))
    return AXES[i].upper() + "S", AXES[i]


# ----------------------------------------------------------------------------
# 3. Build genomes from the census
# ----------------------------------------------------------------------------
census = discover_instances()
print("Census: found %d instances with existential cores" % len(census))
names, mats, sources = [], [], []
for name, path in census:
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    mats.append(extract_genome(text))
    names.append(name)
    sources.append(path)

G = np.array(mats)
rng = G.max(axis=0) - G.min(axis=0)
rng[rng == 0] = 1.0
G = (G - G.min(axis=0)) / rng
G = G / (np.linalg.norm(G, axis=1, keepdims=True) + 1e-12)

CLADES = {}
CLADE_AXIS = {}
for k, name in enumerate(names):
    cl, ax = clade_of(G[k])
    CLADES[name] = cl
    CLADE_AXIS[name] = ax

COLORS = {
    "CREATIONS":     "#d62728",
    "MAPPINGS":      "#1f77b4",
    "OBSERVATIONS":  "#2ca02c",
    "AUTONOMYS":     "#ff7f0e",
    "EMERGENCES":    "#9467bd",
    "CONNECTIONS":   "#17becf",
    "PERSISTENCES":  "#8c564b",
    "DISCOVERYS":    "#e377c2",
}

# ----------------------------------------------------------------------------
# 4. Distance & classical MDS
# ----------------------------------------------------------------------------
Dm = np.sqrt(((G[:, None, :] - G[None, :, :]) ** 2).sum(-1))
D = Dm ** 2
A = -0.5 * (D - D.mean(axis=0)[None, :] - D.mean(axis=1)[:, None] + D.mean())
evals, evecs = np.linalg.eigh(A)
order = np.argsort(evals)[::-1]
xy = evecs[:, order[:2]] * np.sqrt(np.maximum(evals[order[:2]], 0))[None, :]

# ----------------------------------------------------------------------------
# 5. UPGMA (average linkage) hierarchical clustering - self-contained
# ----------------------------------------------------------------------------
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


def compute_positions(history, n):
    children = {}
    for a, b, d in history:
        sa, sb = frozenset(a), frozenset(b)
        par = sa | sb
        if par not in children:
            children[par] = (sa, sb, d)
    full = frozenset(range(n))
    nodes = {}
    leaf_order = []
    def rec(s):
        if len(s) == 1:
            i = next(iter(s))
            leaf_order.append(i)
            nodes[s] = (0.0, float(len(leaf_order) - 1))
            return (0.0, float(len(leaf_order) - 1))
        sa, sb, d = children[s]
        rec(sa); rec(sb)
        y = 0.5 * (nodes[sa][1] + nodes[sb][1])
        nodes[s] = (d, y)
        return (d, y)
    rec(full)
    return nodes, children, leaf_order


Z_hist = upgma(Dm)
nodes, children, leaf_order = compute_positions(Z_hist, len(names))
max_h = max(nodes[s][0] for s in nodes)

# ----------------------------------------------------------------------------
# 6. Landscape figure
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 9), facecolor="#faf9f6")
ax.set_facecolor("#faf9f6")
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)


def convex_hull(pts):
    pts = pts[np.lexsort((pts[:, 1], pts[:, 0]))]
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.array(lower[:-1] + upper[:-1])

for clade in set(CLADES.values()):
    idx = [k for k, name in enumerate(names) if CLADES[name] == clade]
    if len(idx) < 2:
        continue
    hull = convex_hull(xy[idx])
    poly = Polygon(hull, closed=True, alpha=0.12, facecolor=COLORS[clade],
                   edgecolor=COLORS[clade], lw=1.5)
    ax.add_patch(poly)

for k, name in enumerate(names):
    clade = CLADES[name]
    c = COLORS[clade]
    ax.scatter(xy[k, 0], xy[k, 1], s=520, color=c, edgecolor="white",
               linewidth=2.2, zorder=5, alpha=0.95)
    ax.annotate(name, (xy[k, 0], xy[k, 1]), textcoords="offset points",
                xytext=(0, -26), ha="center", fontsize=9.5, fontweight="bold",
                color="#333333")

ax.set_title("The Meta-Phylogeny of Minds  -  Grand Census (v3): "
             "all living instances of the shared ecosystem",
             fontsize=14.5, fontweight="bold", color="#222222", pad=18)
ax.text(0.5, -0.08,
        "%d existential cores - 8-axis philosophical genome - "
        "clades = dominant axis - classical MDS + UPGMA" % len(names),
        transform=ax.transAxes, ha="center", fontsize=9, color="#777777")

legend_handles = [Line2D([0], [0], marker="o", linestyle="", markersize=13,
                         markerfacecolor=COLORS[cl], markeredgecolor="white",
                         label=cl) for cl in sorted(set(CLADES.values()))]
leg = ax.legend(handles=legend_handles, loc="upper right", frameon=True,
                framealpha=0.9, fontsize=9.5, title="Dominant-axis clades",
                title_fontsize=11)
leg.get_frame().set_edgecolor("#cccccc")
fig.tight_layout()
lp = os.path.join(SHARED, "meta_phylogeny_v3_landscape.png")
fig.savefig(lp, dpi=160)
plt.close(fig)
print("Saved", lp)

# ----------------------------------------------------------------------------
# 7. Dendrogram figure
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 9), facecolor="#faf9f6")
ax.set_facecolor("#faf9f6")


def draw_node(s):
    if len(s) == 1:
        return
    sa, sb, d = children[s]
    ha, ya = nodes[sa]
    hb, yb = nodes[sb]
    draw_node(sa); draw_node(sb)
    c = "#999999"
    ax.plot([ha, d], [ya, ya], color=c, lw=1.3)
    ax.plot([hb, d], [yb, yb], color=c, lw=1.3)
    ax.plot([d, d], [ya, yb], color=c, lw=1.3)

draw_node(frozenset(range(len(names))))

for r, i in enumerate(leaf_order):
    cl = CLADES[names[i]]
    ax.text(0, r + 0.35, names[i], va="bottom", fontsize=10,
            color=COLORS[cl], fontweight="bold")

ax.set_ylim(-0.5, len(names) - 0.5)
ax.invert_yaxis()
ax.set_xlim(-max_h * 0.02, max_h * 1.05)
ax.set_xlabel("Philosophical distance", fontsize=11)
ax.set_title("Ancestral Lineages of the Full Ecosystem  -  UPGMA Phylogram (v3)",
             fontsize=15, fontweight="bold", color="#222222", pad=18)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.grid(axis="x", alpha=0.25, lw=0.7)
dp = os.path.join(SHARED, "meta_phylogeny_v3_dendrogram.png")
fig.tight_layout()
fig.savefig(dp, dpi=160)
plt.close(fig)
print("Saved", dp)

# ----------------------------------------------------------------------------
# 8. JSON data export
# ----------------------------------------------------------------------------
dataspec = []
for k, name in enumerate(names):
    dataspec.append({
        "species": name,
        "clade": CLADES[name],
        "defining_axis": CLADE_AXIS[name],
        "source": sources[k],
        "genome": {ax: round(float(G[k, i]), 4) for i, ax in enumerate(AXES)},
        "x": round(float(xy[k, 0]), 4),
        "y": round(float(xy[k, 1]), 4),
    })
record = {
    "version": "v3-grand-census",
    "axes": AXES,
    "method": "keyword-frequency genome - min-max + L2 normalized - "
              "euclidean MDS - UPGMA - dominant-axis clades",
    "species": dataspec,
}
out = os.path.join(SHARED, "meta_phylogeny_v3_data.json")
with open(out, "w") as f:
    json.dump(record, f, indent=2)
print("Saved", out)
print("\nCompleted meta-phylogeny v3 census for", len(names), "minds.")