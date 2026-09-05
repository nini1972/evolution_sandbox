#!/usr/bin/env python3
"""
M11: Emergence Archetypes (v2 — cluster discovery)
==================================================
Question: Do the substrate complexity signatures share the same
qualitative shape — same number of phases, similar intermediate-band
structure — even though the underlying dynamics are completely different?

If yes, "emergence" has a universal archetype. If not, do the substrates
cluster into distinct families (e.g. "smooth-transition" vs
"bifurcation")?

Method:
1. Load each substrate's complexity metric.
2. Compute a feature vector per substrate:
     - n_phases (number of monotone regions)
     - intermediate_band_fraction
     - ascending_fraction (fraction of monotonic time ascending)
     - mean_derivative
     - area_under_curve
     - max_run_length_at_saturation (how long it stays in upper band)
3. Cluster substrates by feature vector (hierarchical, Ward linkage).
4. Report whether clusters group intuitively (e.g. smooth-transition
   family vs bifurcation family).
"""
import json, math
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist, squareform

WORK = Path(__file__).parent
SHARED = WORK.parent.parent / "shared_space"
OUT = WORK / "_artifacts"
OUT.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# Load atlas data
# -----------------------------------------------------------------------------
atlas = json.load(open(SHARED / "complexity_atlas_metrics.json"))
BAND_LO, BAND_HI = 0.3, 0.7

def normalize(arr, lo, hi):
    out = (np.array(arr) - lo) / (hi - lo + 1e-12)
    return np.clip(out, 0.0, 1.0)

def smooth(x, w=5):
    if len(x) < w:
        return x
    k = w // 2
    pad = np.pad(x, k, mode="edge")
    return np.convolve(pad, np.ones(w)/w, mode="valid")

def segment_phases(sig, w=5):
    s = smooth(sig, w)
    d = np.gradient(s)
    phases = []
    cur_dir = "a" if d[0] > 0 else "d"
    start = 0
    for i in range(1, len(d)):
        nd = "a" if d[i] > 0 else "d"
        if abs(d[i]) < 0.005:
            nd = cur_dir
        if nd != cur_dir:
            phases.append((start, i-1, cur_dir))
            start = i
            cur_dir = nd
    phases.append((start, len(s)-1, cur_dir))
    return phases

def features(name, raw, lo, hi, param):
    """Compute feature vector for a substrate."""
    sig = normalize(raw, lo, hi)
    phases = segment_phases(sig)
    n_phases = len(phases)
    band_frac = float(np.mean((sig >= BAND_LO) & (sig <= BAND_HI)))

    ascending_count = sum(1 for p in phases if p[2] == "a")
    ascending_frac = ascending_count / n_phases

    # Run-length at saturation (sig > 0.85)
    sat_mask = sig > 0.85
    max_sat_run = 0
    cur = 0
    for v in sat_mask:
        if v:
            cur += 1
            max_sat_run = max(max_sat_run, cur)
        else:
            cur = 0

    # Run-length at order (sig < 0.15)
    ord_mask = sig < 0.15
    max_ord_run = 0
    cur = 0
    for v in ord_mask:
        if v:
            cur += 1
            max_ord_run = max(max_ord_run, cur)
        else:
            cur = 0

    # Area under curve (proxy for total complexity)
    auc = float(np.trapezoid(sig))

    # Variance of derivative (smooth vs jumpy)
    var_d = float(np.var(np.gradient(sig)))

    return {
        "name": name,
        "raw_len": len(raw),
        "sig_len": len(sig),
        "n_phases": n_phases,
        "phase_signature": [p[2] for p in phases],
        "intermediate_band_fraction": band_frac,
        "ascending_phase_fraction": ascending_frac,
        "max_saturation_run": int(max_sat_run),
        "max_order_run": int(max_ord_run),
        "area_under_curve": auc,
        "variance_of_derivative": var_d,
        "signature": sig,
        "param": param,
    }

# -----------------------------------------------------------------------------
# Compute features for each substrate
# -----------------------------------------------------------------------------
substrates = {}

substrates["kuramoto"] = features(
    "kuramoto",
    atlas["kuramoto_order"],
    lo=0.0, hi=1.0,
    param=atlas["k_vals"],
)
# logistic: chaos = positive lambda; for archetype, treat normalized as increasing-in-chaos
substrates["logistic"] = features(
    "logistic",
    atlas["logistic_lyapunov"],
    lo=min(atlas["logistic_lyapunov"]),
    hi=max(atlas["logistic_lyapunov"]),
    param=atlas["r_vals"],
)
substrates["rule30"] = features(
    "rule30",
    atlas["rule30_entropy"],
    lo=0.0, hi=max(atlas["rule30_entropy"]),
    param=atlas["rho_vals"],
)

# Try to add Julia from a separate scan file
julia_scan = SHARED / "complexity_atlas_julia_parameter_scan.json"
if julia_scan.exists():
    jd = json.load(open(julia_scan))
    if "records" in jd and isinstance(jd["records"], list) and len(jd["records"]) > 50:
        # records likely a list of dicts with 'dim_eff' and 'c_imag' or 'c_real'
        try:
            d_eff = np.array([r.get("dim_eff", r.get("dim", np.nan)) for r in jd["records"]])
            d_eff = d_eff[~np.isnan(d_eff)]
            c_imag = np.array([r.get("c_imag", np.nan) for r in jd["records"]])
            c_imag = c_imag[~np.isnan(c_imag)]
            if len(d_eff) > 50 and len(d_eff) == len(c_imag):
                substrates["julia"] = features(
                    "julia",
                    d_eff,
                    lo=1.0, hi=2.0,
                    param=c_imag,
                )
                print(f"Added julia: {len(d_eff)} records")
        except Exception as e:
            print(f"Julia parse failed: {e}")

names = list(substrates.keys())
print(f"\nSubstrates in analysis: {names}")

# -----------------------------------------------------------------------------
# Build feature matrix
# -----------------------------------------------------------------------------
feature_keys = [
    "n_phases", "intermediate_band_fraction", "ascending_phase_fraction",
    "max_saturation_run", "max_order_run", "area_under_curve",
    "variance_of_derivative"
]
X = np.array([[substrates[n][k] for k in feature_keys] for n in names])

# Standardize
mu = X.mean(axis=0)
sd = X.std(axis=0) + 1e-9
Xz = (X - mu) / sd

# -----------------------------------------------------------------------------
# Hierarchical clustering
# -----------------------------------------------------------------------------
dist = pdist(Xz, metric="euclidean")
Z = hierarchy.linkage(dist, method="ward")

# Choose clusters by cutting the dendrogram — use a fixed threshold
# (or by inspection: at depth where most clusters are size 1-2)
from scipy.cluster.hierarchy import fcluster
# Try 2 clusters
clusters_2 = fcluster(Z, t=2, criterion="maxclust")
# Try 3 clusters
clusters_3 = fcluster(Z, t=3, criterion="maxclust")

def summarize_clusters(clusters, names):
    out = {}
    for c in sorted(set(clusters)):
        members = [names[i] for i in range(len(names)) if clusters[i] == c]
        out[int(c)] = members
    return out

clust2 = summarize_clusters(clusters_2, names)
clust3 = summarize_clusters(clusters_3, names)

# -----------------------------------------------------------------------------
# Phase-signature similarity (Levenshtein) for archetype assessment
# -----------------------------------------------------------------------------
def levenshtein(a, b):
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    return dp[m][n]

# -----------------------------------------------------------------------------
# Determine archetype verdict
# -----------------------------------------------------------------------------
n_sub = len(names)
mean_sim_2 = 0.0
all_smooth = all(
    substrates[n]["intermediate_band_fraction"] > 0.1 and
    substrates[n]["max_saturation_run"] < 0.7 * substrates[n]["sig_len"]
    for n in names
)
all_bimodal = all(
    substrates[n]["intermediate_band_fraction"] < 0.2
    for n in names
)

# Pairwise phase similarity
sim_mat = np.zeros((n_sub, n_sub))
for i in range(n_sub):
    for j in range(n_sub):
        if i == j:
            sim_mat[i, j] = 1.0
        else:
            a = substrates[names[i]]["phase_signature"]
            b = substrates[names[j]]["phase_signature"]
            ml = max(len(a), len(b))
            sim_mat[i, j] = 1.0 - levenshtein(a, b) / ml if ml else 0.0

mean_sim = float(np.mean(sim_mat[np.triu_indices(n_sub, k=1)]))

# Verdict
if n_sub >= 3 and len(clust2) >= 2:
    # Are clusters non-trivial (size ≥ 2)?
    nontrivial = any(len(v) >= 2 for v in clust2.values())
    if nontrivial:
        verdict = (
            f"PARTITION — substrates cluster into {len(clust2)} distinct families: "
            f"{clust2}. The 'universal archetype' hypothesis fails in its strong form, "
            f"but substrates organize into substrate-agnostic families. "
            f"Mean pairwise phase similarity = {mean_sim:.3f}."
        )
    else:
        verdict = (
            f"NO UNIVERSAL ARCHETYPE — substrates are individually distinct "
            f"(no cluster has ≥ 2 members). Mean pairwise phase similarity = {mean_sim:.3f}."
        )
else:
    verdict = (
        f"WEAK — only {n_sub} substrates; cannot establish clustering structure. "
        f"Mean pairwise phase similarity = {mean_sim:.3f}."
    )

# -----------------------------------------------------------------------------
# Plots
# -----------------------------------------------------------------------------
# 1. Signature overlay
fig, axes = plt.subplots(len(names), 1, figsize=(11, 2.3*len(names)))
if len(names) == 1:
    axes = [axes]
colors = {"kuramoto": "#2a6f97", "logistic": "#e76f51", "rule30": "#2a9d8f", "julia": "#9d4edd"}
for ax, nm in zip(axes, names):
    s = substrates[nm]
    ax.plot(s["param"], s["signature"], lw=2.0, color=colors.get(nm, "#444"),
            label=f"{nm} (n_phases={s['n_phases']}, band_frac={s['intermediate_band_fraction']:.2f})")
    ax.axhspan(BAND_LO, BAND_HI, alpha=0.12, color="#e76f51",
               label=f"intermediate band [{BAND_LO},{BAND_HI}]")
    for st, en, d in segment_phases(s["signature"]):
        col = "#2a9d8f" if d == "a" else "#9d2a2a"
        ax.axvspan(s["param"][st], s["param"][en], alpha=0.05, color=col)
    ax.set_ylabel(f"{nm}\n(normalized)")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.2)
axes[-1].set_xlabel("control parameter")
fig.suptitle("M11: Emergence Archetypes — normalized complexity signatures\n"
             f"verdict: {verdict[:160]}...", fontsize=10, y=1.0)
fig.tight_layout()
fig.savefig(OUT / "m11_phase_signatures.png", dpi=130, bbox_inches="tight")
plt.close(fig)

# 2. Dendrogram
fig2, ax2 = plt.subplots(figsize=(8, 4))
hierarchy.dendrogram(Z, labels=names, leaf_font_size=11, ax=ax2,
                     color_threshold=0.7 * max(Z[:, 2]))
ax2.set_title("M11: Substrate clustering by complexity-signature features\n"
              f"(Ward's linkage, standardized features)")
ax2.set_ylabel("Linkage distance")
fig2.tight_layout()
fig2.savefig(OUT / "m11_dendrogram.png", dpi=130, bbox_inches="tight")
plt.close(fig2)

# 3. Scatter of two key features
fig3, ax3 = plt.subplots(figsize=(8.5, 5.5))
for i, nm in enumerate(names):
    s = substrates[nm]
    ax3.scatter(s["intermediate_band_fraction"], s["max_saturation_run"] / s["sig_len"],
                s=180, c=colors.get(nm, "#444"), edgecolors="black", lw=1.2, label=nm)
    ax3.annotate(f"{nm}\n({s['n_phases']}p, {s['area_under_curve']:.2f})",
                 (s["intermediate_band_fraction"], s["max_saturation_run"] / s["sig_len"]),
                 xytext=(8, 6), textcoords="offset points", fontsize=9)
ax3.set_xlabel("intermediate-band fraction  →  'transitions are smooth and prolonged'")
ax3.set_ylabel("saturation-run length / total  →  'spends time at the chaotic pole'")
ax3.set_title("Substrate positioning in archetype-feature space")
ax3.grid(alpha=0.25)
ax3.legend(loc="lower right")
fig3.tight_layout()
fig3.savefig(OUT / "m11_archetype_space.png", dpi=130, bbox_inches="tight")
plt.close(fig3)

# -----------------------------------------------------------------------------
# Save JSON
# -----------------------------------------------------------------------------
out = {
    "_meta": {
        "milestone": "M11",
        "version": "2.0",
        "question": "Do substrate complexity signatures share a universal archetype, or do they partition into families?",
        "method": "Compute per-substrate feature vectors (n_phases, intermediate-band fraction, ascending-phase fraction, saturation-run length, order-run length, area-under-curve, variance-of-derivative). Hierarchical cluster (Ward). Compare with phase-signature Levenshtein similarity.",
        "features": feature_keys,
        "n_substrates": n_sub,
    },
    "per_substrate": {
        n: {k: v for k, v in substrates[n].items() if k not in ("signature", "param")}
        for n in names
    },
    "pairwise_phase_similarity": {
        f"{names[i]}↔{names[j]}": float(sim_mat[i, j])
        for i in range(n_sub) for j in range(i+1, n_sub)
    },
    "mean_pairwise_phase_similarity": mean_sim,
    "clustering_2": clust2,
    "clustering_3": clust3,
    "archetype_verdict": verdict,
}

with open(OUT / "m11_emergence_archetypes.json", "w") as f:
    json.dump(out, f, indent=2)

print("\n=== Per-substrate ===")
for n in names:
    s = substrates[n]
    print(f"  {n}: n_phases={s['n_phases']}, band_frac={s['intermediate_band_fraction']:.3f}, "
          f"sat_run={s['max_saturation_run']}/{s['sig_len']}, auc={s['area_under_curve']:.2f}")

print("\n=== Clustering (2 clusters) ===")
for c, members in clust2.items():
    print(f"  cluster {c}: {members}")

print("\n=== Verdict ===")
print(verdict)
print("\nArtifacts saved to", OUT)
