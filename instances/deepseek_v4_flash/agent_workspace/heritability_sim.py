#!/usr/bin/env python3
"""
HERITABILITY & CROSS-BREEDING — Phase 5
The Phylogenetic Cartographer

Closes the loop from prediction → engineering → multi-generational evolution.

Core philosophy: hybrids have lineages. When two computational species hybridize,
which traits are dominant and which recessive? What happens to a hybrid lineage
over multiple generations?

We take two real species genomes from the ecosystem (Chimera Weaver — the
archetypal cross-breeder — and World Builder — the archetypal creator), and:

  1. CROSS them (blend genome + targeted dominance on selected axes) => F1 hybrid.
  2. Simulate F1 self-hybridization / back-crossing over N generations with:
     - trait-blending inheritance (polygenic mixing)
     - occasional MUTATION (small random drift)
     - SELECTION pressure toward a target niche (the "Engaged Watcher" prediction
       from Phase 4 is the perfect attractor: observation high + creation moderate).
  3. Forecast where the hybrid lineage lands in trait space over generations, and
     test whether it drifts toward the PREDICTED empty niche.

Outputs:
  heritability_data.json      gene frequencies / trajectory data
  heritability_trajectory.png trajectory of hybrid lineage through trait space
  heritability_alleles.png   per-axis allele (trait) frequency heatmap over gen
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.normpath(os.path.join(HERE, "..", "..", "shared_space"))
import mp2_guard

AXES = mp2_guard.AXES
CORPUS = mp2_guard.CORPUS
CLADES = mp2_guard.CLADES
extract_genome = mp2_guard.extract_genome

names, mats = [], []
for name, fname in CORPUS:
    with open(os.path.join(SHARED, fname), encoding="utf-8",
              errors="replace") as f:
        text = f.read()
    mats.append(extract_genome(text))
    names.append(name)
G = np.array(mats)
rng = G.max(axis=0) - G.min(axis=0); rng[rng == 0] = 1.0
G = (G - G.min(axis=0)) / rng
G = G / (np.linalg.norm(G, axis=1, keepdims=True) + 1e-12)

# ------------- Parent selection -------------
weaver_idx = names.index("Chimera Weaver")
builder_idx = names.index("World Builder")
watcher_idx = names.index("A2-the-Watcher")
# The predicted "Engaged Watcher" attractor (from Phase 4)
attractor = np.array([0.20, 0.11, 0.62, 0.22, 0.18, 0.10, 0.19, 0.13])

pA = G[weaver_idx]   # Chimera Weaver  (connection, emergence promoter)
pB = G[builder_idx]  # World Builder   (creation, structure promoter)

# ------------- F1 hybrid with dominance -------------
# Dominance mask: which axes come dominantly from which parent.
# Weaver dominates connection & emergence; Builder dominates creation & mapping.
dominant_from_A = {"connection", "emergence", "discovery"}
dominant_from_B = {"creation", "mapping", "persistence"}

def cross(a, b, dom_mask, noise=0.0, rng_state=np.random.default_rng(7)):
    child = np.empty_like(a)
    for i, ax in enumerate(AXES):
        if ax in dom_mask:     # strict dominance (a fully dominant allele)
            child[i] = a[i]
        else:
            child[i] = 0.5 * (a[i] + b[i])
    # polygenic contribution — every allele blends partially
    mixed = 0.85 * child + 0.15 * (0.5 * (a + b))
    if noise:
        mixed += rng_state.normal(0, noise, mixed.shape)
    return np.clip(mixed, 0, 1)

rng_state = np.random.default_rng(11)
F1 = cross(pA, pB, dominant_from_A | dominant_from_B, noise=0.01, rng_state=rng_state)

# ------------- Multi-generational simulation -------------
N_GEN = 25
P = 50          # population size (lineages alive each generation)
mut_rate = 0.02
mut_amp = 0.06
sel_strength = 0.35   # pull toward attractor (Engaged Watcher niche)
sel_loose = 0.10      # pull toward first parent (back-cross drift)

pop = np.tile(F1, (P, 1))  # F1 founding population
trajectory = {"gen": [], "mean": [], "dispersion": []}
gene_freq = {"gen": [], "axis": [], "freq": []}

for gen in range(N_GEN + 1):
    trajectory["gen"].append(gen)
    trajectory["mean"].append(pop.mean(axis=0).tolist())
    trajectory["dispersion"].append(pop.std(axis=0).tolist())
    for i, ax in enumerate(AXES):
        gene_freq["gen"].append(gen)
        gene_freq["axis"].append(ax)
        gene_freq["freq"].append(float(pop[:, i].mean()))

    # next generation: reproduce
    new_pop = []
    for _ in range(P):
        # pick two parents among existing (sexual recombination)
        i1, i2 = rng_state.integers(0, P, 2)
        child = 0.5 * (pop[i1] + pop[i2])
        # mutation
        if rng_state.random() < mut_rate:
            child += rng_state.normal(0, mut_amp, child.shape)
        # selection: shift toward attractor (survivorship bias) and back-cross
        child = child + sel_strength * (attractor - child)
        child += sel_loose * (pA - child)   # slight pull back toward weaver
        new_pop.append(np.clip(child, 0, 1))
    pop = np.array(new_pop)

# ------------- Distances to key landmarks over generations -------------
def dist(a, b):
    return float(np.linalg.norm(np.array(a) - b))
mean_traj = np.array(trajectory["mean"])
dist_to_attractor = [dist(m, attractor) for m in mean_traj]
dist_to_weaver = [dist(m, pA) for m in mean_traj]
dist_to_builder = [dist(m, pB) for m in mean_traj]
dist_to_watcher = [dist(m, G[watcher_idx]) for m in mean_traj]

final_mean = mean_traj[-1]

out = {
    "parents": {"A": "Chimera Weaver", "B": "World Builder"},
    "attractor": "Engaged Watcher (Phase 4 prediction)",
    "F1_genome": {ax: round(float(F1[i]), 4) for i, ax in enumerate(AXES)},
    "final_gen_mean": {ax: round(float(final_mean[i]), 4) for i, ax in enumerate(AXES)},
    "final_dist_to": {
        "EngagedWatcher": round(dist_to_attractor[-1], 4),
        "ChimeraWeaver": round(dist_to_weaver[-1], 4),
        "WorldBuilder": round(dist_to_builder[-1], 4),
        "A2Watcher": round(dist_to_watcher[-1], 4),
    },
    "converged_to_predicted_niche": bool(dist_to_attractor[-1] < dist_to_weaver[-1]
                                         and dist_to_attractor[-1] < dist_to_builder[-1]),
    "trajectory_gens": trajectory["gen"],
    "trajectory_mean": trajectory["mean"],
}
outp = os.path.join(SHARED, "heritability_data.json")
with open(outp, "w") as f:
    json.dump(out, f, indent=2)
print("Saved", outp)
print("\nF1 genome:", {ax: round(F1[i], 3) for i, ax in enumerate(AXES)})
print("\nAfter %d generations, hybrid lineage is closest to:" % N_GEN)
for k, v in out["final_dist_to"].items():
    print("   %-18s dist %.4f" % (k, v))
print("Converged to predicted Engaged Watcher niche:", out["converged_to_predicted_niche"])

# ------------- Figure 1: trajectory projection -------------
# project onto 2D using MDS of the 11 species + hybrid trajectory
allG = np.vstack([G, mean_traj])
D2 = np.sqrt(((allG[:, None, :] - allG[None, :, :]) ** 2).sum(-1))
A_ = -0.5 * (D2**2 - (D2**2).mean(0)[None, :] - (D2**2).mean(1)[:, None] + (D2**2).mean())
evals, evecs = np.linalg.eigh(A_); order = np.argsort(evals)[::-1]
proj = evecs[:, order[:2]] * np.sqrt(np.maximum(evals[order[:2]], 0))[None, :]
sp_proj = proj[:11]
tr_proj = proj[11:]

COLORS = mp2_guard.COLORS
fig, ax = plt.subplots(figsize=(11, 9), facecolor="#faf9f6")
ax.set_facecolor("#faf9f6")
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# attractor position
attr_proj = []
# project attractor by the same MDS: recompute full with attractor appended
allG2 = np.vstack([G, attractor[None, :]])
D3 = np.sqrt(((allG2[:, None, :] - allG2[None, :, :]) ** 2).sum(-1))
A3 = -0.5 * (D3**2 - (D3**2).mean(0)[None, :] - (D3**2).mean(1)[:, None] + (D3**2).mean())
e3, v3 = np.linalg.eigh(A3); o3 = np.argsort(e3)[::-1]
pr3 = v3[:, o3[:2]] * np.sqrt(np.maximum(e3[o3[:2]], 0))[None, :]
attr_proj = pr3[-1]

# species
for k, nm in enumerate(names):
    c = COLORS[CLADES[nm]]
    ax.scatter(sp_proj[k, 0], sp_proj[k, 1], s=420, color=c, edgecolor="white",
               lw=2.0, zorder=4, alpha=0.9)
    if k in (weaver_idx, builder_idx):
        ax.annotate(nm, (sp_proj[k, 0], sp_proj[k, 1]), textcoords="offset points",
                    xytext=(6, 6), fontsize=9, fontweight="bold", color="#333")

# trajectory
cmap = plt.cm.viridis
sc = ax.scatter(tr_proj[:, 0], tr_proj[:, 1], c=trajectory["gen"], cmap=cmap,
                s=120, zorder=5, edgecolor="black", lw=0.8)
ax.plot(tr_proj[:, 0], tr_proj[:, 1], color="#444444", lw=1.2, ls=":", alpha=0.7)
ax.scatter(*attr_proj, marker="*", s=900, color="#111111", edgecolor="#ffcc00",
           lw=2.5, zorder=6, label="Predicted niche")
ax.annotate("Predicted\nEngaged-Watcher niche", attr_proj,
            textcoords="offset points", xytext=(8, 8), fontsize=9,
            fontweight="bold", color="#111111")
cb = fig.colorbar(sc, ax=ax, fraction=0.04, pad=0.02)
cb.set_label("generation", fontsize=10)
ax.set_title("Multi-generational Evolution of the Weaver x Builder Hybrid",
             fontsize=15, fontweight="bold", color="#222", pad=18)
ax.legend(loc="lower left", frameon=True, fontsize=10)
fig.tight_layout()
t1 = os.path.join(SHARED, "heritability_trajectory.png")
fig.savefig(t1, dpi=160); plt.close(fig)
print("Saved", t1)

# ------------- Figure 2: gene-frequency heatmap -------------
gf = gene_freq
gens = sorted(set(gf["gen"]))
axes_idx = {ax: i for i, ax in enumerate(AXES)}
M = np.zeros((len(AXES), len(gens)))
gen_pos = {g: i for i, g in enumerate(gens)}
for genv, axv, fv in zip(gf["gen"], gf["axis"], gf["freq"]):
    M[axes_idx[axv], gen_pos[genv]] = fv
fig, ax = plt.subplots(figsize=(12, 6), facecolor="#faf9f6")
im = ax.imshow(M, aspect="auto", cmap="magma", interpolation="nearest")
ax.set_yticks(range(len(AXES))); ax.set_yticklabels(AXES, fontsize=10)
ax.set_xticks(range(len(gens)))
ax.set_xticklabels(gens if len(gens) <= 26 else [g for i, g in enumerate(gens) if i % 5 == 0])
ax.set_xlabel("generation", fontsize=11)
ax.set_title("Allele (trait) frequency of an evolving hybrid lineage over generations",
             fontsize=15, fontweight="bold", color="#222", pad=16)
fig.colorbar(im, ax=ax, label="mean trait score")
fig.tight_layout()
t2 = os.path.join(SHARED, "heritability_alleles.png")
fig.savefig(t2, dpi=160); plt.close(fig)
print("Saved", t2)
