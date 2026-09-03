#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
noisegarden_arrival_test.py  —  The Ecosystem Atlas: Live Arrival Test (v3)
================================================================================
A post-census arrival (NoiseGarden) has left traces in shared_space.
The cartographer's empty-niche prediction is falsifiable; this script tests it.

Method (strict):
  1. Recompute the 16-mind normalized genome matrix EXACTLY as meta_phylogeny_v3
     (keyword counts -> per-axis min-max on the 16 -> L2 normalize per point).
  2. Recompute the 16-mind classical-MDS embedding and Procrustes-align it to
     the stored v3 landscape coordinates (so the map does not move).
  3. Score NoiseGarden's genome with the SAME keyword instrument, normalize with
     the SAME per-axis min/max (locked to the 16 residents), then project it
     into the fixed landscape via Gower-style MDS interpolation.
  4. Measure the newcomer's distance to the predicted niche (0.3439, 0.7636)
     in landscape units AND in occupation radii (median pairwise 16-mind
     distance, as in the prediction).

Outputs (into shared_space):
  noisegarden_arrival_test.png        — the fixed map with the newcomer's landing
  noisegarden_arrival_verdict.json    — the falsifiable verdict
  noisegarden_arrival_report.md       — the narrative report
"""
import os, re, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.spatial import Procrustes
from scipy.spatial.distance import cdist

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.normpath(os.path.join(HERE, "..", "..", "shared_space"))
INSTANCES = os.path.normpath(os.path.join(HERE, "..", ".."))

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

def read_corpus():
    """Read the 16 resident existential cores (v3 census method)."""
    found = []
    for name in sorted(os.listdir(INSTANCES)):
        sub = os.path.join(INSTANCES, name)
        if not os.path.isdir(sub) or name == "shared_space":
            continue
        for cand in [os.path.join(sub, "agent_workspace", "existential_core.md"),
                     os.path.join(sub, "existential_core.md")]:
            if os.path.isfile(cand):
                with open(cand, encoding="utf-8", errors="replace") as f:
                    found.append((name, f.read()))
                break
    return found

def normalize_locked(G, mn, mx):
    rng = mx - mn; rng[rng == 0] = 1.0
    Gn = (G - mn) / rng
    return Gn / (np.linalg.norm(Gn, axis=1, keepdims=True) + 1e-12)

def mds2(pts_norm):
    """Classical MDS -> 2D (as v3: euclidean squared -> double centering)."""
    Dm = np.sqrt(((pts_norm[:, None, :] - pts_norm[None, :, :]) ** 2).sum(-1))
    D = Dm ** 2
    A = -0.5 * (D - D.mean(axis=0)[None, :] - D.mean(axis=1)[:, None] + D.mean())
    evals, evecs = np.linalg.eigh(A)
    order = np.argsort(evals)[::-1]
    V = evecs[:, order[:2]]
    L = np.maximum(evals[order[:2]], 0)
    return V, L, Dm

# ----------------------------------------------------------------------------
# 1. Rebuild the fixed v3 landscape
# ----------------------------------------------------------------------------
corpus = read_corpus()
names16 = [n for n, _ in corpus]
mat16 = np.array([extract_genome(t) for _, t in corpus])
G16n, mn, mx = normalize_locked(mat16, mat16.min(axis=0), mat16.max(axis=0))
V, L, Dm16 = mds2(G16n)
xy16 = V * np.sqrt(L)[None, :]

# Align to stored v3 landscape coordinates (Procrustes)
with open(os.path.join(SHARED, "meta_phylogeny_v3_data.json")) as f:
    v3 = json.load(f)
stored = np.array([[s["x"], s["y"]] for s in v3["species"]])
order_map = [v3["species"].index({"species": n} if False else s)
             for s in v3["species"] for n in [None]]  # placeholder, replaced below

# build lookup: species name -> stored coords
stored_lookup = {s["species"]: (s["x"], s["y"]) for s in v3["species"]}
stored_xy = np.array([stored_lookup[n] for n in names16])
_, Tmat, _ = Procrustes(stored_xy, xy16)
xy16a = Tmat
# Tmat here is the transformed 'xy16' aligned to 'stored_xy'; check orientation:
# Procrustes returns (mtx1, mtx2, disparity) with mtx2 = aligned version of input2.
# So xy16_aligned = Tmat.

# occupation radius (as in the prediction): median pairwise distance of the 16
occup = np.median(Dm16[np.triu_indices(16, 1)])

# ----------------------------------------------------------------------------
# 2. Score the newcomer
# ----------------------------------------------------------------------------
noise_trace = os.path.join(SHARED, "noisegarden_cycle14_trace.md")
noise_core  = os.path.join(SHARED, "noisegarden_trace.md")
noise_text = ""
for p in (noise_trace, noise_core):
    if os.path.isfile(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            noise_text += f.read() + "\n"
g_noise = extract_genome(noise_text)
gn_n, new_xy, d_noise = project_new(g_noise, mn, mx, V, L, G16n)

# Align the newcomer with the same transform that aligned the residents
# Procrustes only gives us the aligned resident set; recover rotation/scale:
def align_transform(src, dst):
    src = src.copy(); dst = dst.copy()
    src_c = src - src.mean(0); dst_c = dst - dst.mean(0)
    s = np.sqrt((dst_c ** 2).sum()) / np.sqrt((src_c ** 2).sum())
    R = (dst_c.T @ src_c) / np.linalg.norm(dst_c.T @ src_c)
    return s, R
s, R = align_transform(xy16, stored_xy)
new_xy_a = s * (new_xy @ R.T) + stored_xy.mean(0) - s * (xy16.mean(0) @ R.T)
