"""
M10: Rank-Order Recurrence Analysis

M9 found that raw dim_eff values cluster in [0.3, 0.7] for some substrates but not others.
But the *absolute band* is sensitive to how we anchor the normalization.
A more robust question: do substrates order themselves similarly across all the emergence metrics?

If yes, that would be a real cross-substrate law: "the substrates that have rich boundaries
are the same substrates that have low mutual information, high gradient sparsity, etc."

This script:
  1) Loads the M9 substrate data (6 substrates × ~4 features each)
  2) Adds rank-stability by computing within-feature ranks (1=lowest, N=highest)
  3) Computes pairwise rank correlations across all substrate pairs (Spearman)
  4) Reports: do the "structurally complex" substrates cluster together in ALL rank orders?
"""

import json
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
DATA_FILE = HERE / "m9_cross_substrate_recurrence.json"
OUT_JSON = HERE / "m10_rank_order_recurrence.json"
OUT_PNG = HERE / "m10_rank_order_recurrence.png"


def collect_feature_matrix():
    """Return dict: substrate -> {feature -> value}, and the list of features used."""
    data = json.loads(DATA_FILE.read_text())
    substrates = data["substrates"]
    # Pivot: substrate -> {feature -> median}
    matrix = {}
    for s in substrates:
        name = s["substrate"]
        matrix[name] = {}
    # Build feature list from the metric names present
    features = sorted({s["metric"] for s in substrates})
    for s in substrates:
        matrix[s["substrate"]][s["metric"]] = s["median"]
    return matrix, features


def to_rank_matrix(matrix, features):
    """Convert raw values to ranks within each feature (1=lowest, N=highest)."""
    substrates = sorted(matrix.keys())
    rank_mat = {}
    for f in features:
        vals = [matrix[s].get(f, np.nan) for s in substrates]
        # Rank with NaN handling (worst rank for missing)
        ranks = []
        for v in vals:
            if v is None or (isinstance(v, float) and np.isnan(v)):
                ranks.append(np.nan)
            else:
                ranks.append(v)
        # Rank: 1 = smallest
        order = np.argsort(ranks)
        rank_arr = np.empty_like(order, dtype=float)
        for i, oi in enumerate(order):
            rank_arr[oi] = i + 1
        for i, s in enumerate(substrates):
            matrix[s][f + "_rank"] = rank_arr[i]
    return matrix, [f + "_rank" for f in features]


def pairwise_rank_corr(matrix, rank_features):
    """Spearman correlation of rank vectors between all pairs of substrates."""
    substrates = sorted(matrix.keys())
    R = np.array([[matrix[s][f] for f in rank_features] for s in substrates], dtype=float)
    n = len(substrates)
    C = np.zeros((n, n))
    P = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                C[i, j] = 1.0
                P[i, j] = 0.0
            else:
                # Spearman via Pearson on ranks (R is already ranks)
                a, b = R[i], R[j]
                mask = ~np.isnan(a) & ~np.isnan(b)
                if mask.sum() < 2:
                    C[i, j] = np.nan
                    P[i, j] = np.nan
                else:
                    rho, p = spearmanr(a[mask], b[mask])
                    C[i, j] = rho
                    P[i, j] = p
    return substrates, C, P


def cluster_substrates_by_rank(C):
    """Cluster substrates by their rank-correlation similarity.
    Use 1 - C as distance, then simple agglomerative clustering (single-link)."""
    substrates, _, _ = C
    D = 1 - C
    np.fill_diagonal(D, 0)
    # Simple flat clustering: greedy nearest-neighbor chain
    n = len(substrates)
    cluster_of = list(range(n))
    order = np.argsort(D.sum(axis=1))
    visited = set()
    clusters = []
    # Single-link clustering by threshold on (1-C)
    # For 6 substrates, use threshold 0.6 (i.e. rho > 0.4)
    threshold = 0.6
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    for i in range(n):
        for j in range(i+1, n):
            if D[i, j] < threshold:
                union(i, j)
    groups = {}
    for i in range(n):
        r = find(i)
        groups.setdefault(r, []).append(substrates[i])
    return list(groups.values())


def main():
    matrix, features = collect_feature_matrix()
    print(f"Substrates: {sorted(matrix.keys())}")
    print(f"Features:   {features}")
    matrix, rank_features = to_rank_matrix(matrix, features)
    print(f"Rank-features: {rank_features}")
    print()
    print("Rank matrix (substrate × feature_rank):")
    substrates = sorted(matrix.keys())
    print(f"{'substrate':25s} " + " ".join(f"{f[:14]:>14s}" for f in rank_features))
    for s in substrates:
        print(f"{s:25s} " + " ".join(f"{matrix[s][f]:14.1f}" for f in rank_features))
    print()

    subs, C, P = pairwise_rank_corr(matrix, rank_features)
    print("Pairwise Spearman rho (rank correlations between substrate profiles):")
    header = f"{'':20s}" + "".join(f"{s[:8]:>10s}" for s in subs)
    print(header)
    for i, s in enumerate(subs):
        row = f"{s[:20]:20s}" + "".join(f"{C[i,j]:10.3f}" for j in range(len(subs)))
        print(row)
    print()

    # P-values
    print("P-values:")
    print(header)
    for i, s in enumerate(subs):
        row = f"{s[:20]:20s}" + "".join(f"{P[i,j]:10.3f}" for j in range(len(subs)))
        print(row)
    print()

    # Mean off-diagonal correlation (excluding self) - is there *any* signal?
    mask = ~np.eye(len(subs), dtype=bool)
    off_vals = C[mask]
    mean_rho = float(np.nanmean(off_vals))
    median_rho = float(np.nanmedian(off_vals))
    print(f"Mean off-diag rho: {mean_rho:.3f}, median: {median_rho:.3f}")
    print(f"Number of significant pairs (p<0.05): {int((P[mask] < 0.05).sum())} of {len(off_vals)}")
    print()

    clusters = cluster_substrates_by_rank(C)
    print("Single-link clusters (rho > 0.4):")
    for cl in clusters:
        print(f"  - {cl}")
    print()

    # Cluster "structural complexity" by *mean rank* across all features
    mean_ranks = {s: np.nanmean([matrix[s][f] for f in rank_features]) for s in subs}
    print("Mean rank across features (lower = 'simpler' end, higher = 'richer' end):")
    for s, r in sorted(mean_ranks.items(), key=lambda x: x[1]):
        print(f"  {s:25s}  mean_rank = {r:.2f}")
    print()

    # Plot the correlation matrix
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(C, cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_xticks(range(len(subs)))
    ax.set_yticks(range(len(subs)))
    ax.set_xticklabels(subs, rotation=45, ha='right')
    ax.set_yticklabels(subs)
    for i in range(len(subs)):
        for j in range(len(subs)):
            ax.text(j, i, f"{C[i,j]:.2f}", ha='center', va='center',
                    fontsize=8, color='black' if abs(C[i,j]) < 0.7 else 'white')
    plt.colorbar(im, ax=ax, label='Spearman rho (rank corr)')
    ax.set_title(f"M10: Rank-order recurrence of emergence features\nacross {len(subs)} substrates")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=110)
    print(f"Saved {OUT_PNG}")

    # Verdict
    n_sig = int((P[mask] < 0.05).sum())
    out = {
        "_meta": {
            "discovery": "M10",
            "question": "Do substrates order themselves similarly across all emergence features (rank-level recurrence)?",
            "method": "Per-feature within-substrate ranking, then pairwise Spearman rho",
            "follows": "M9 (M9 found raw band membership is anchor-fragile; this tests rank-level stability)",
        },
        "substrates": subs,
        "rank_features": rank_features,
        "mean_offdiag_rho": mean_rho,
        "median_offdiag_rho": median_rho,
        "n_significant_pairs_p05": n_sig,
        "n_pairs": int(len(off_vals)),
        "clusters_single_link_rho_gt_0p4": clusters,
        "mean_rank_by_substrate": mean_ranks,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2))
    print(f"Saved {OUT_JSON}")

    if mean_rho > 0.3:
        verdict = "POSITIVE: substrates DO order themselves similarly across emergence features"
    elif mean_rho > 0.0:
        verdict = "WEAK POSITIVE: there is mild rank-level similarity, but it is not robust"
    elif mean_rho > -0.3:
        verdict = "NEUTRAL/MIXED: no consistent rank-level recurrence"
    else:
        verdict = "NEGATIVE: substrates order themselves INVERSELY across emergence features"
    print()
    print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
