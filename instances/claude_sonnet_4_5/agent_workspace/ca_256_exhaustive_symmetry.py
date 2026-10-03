#!/usr/bin/env python3
"""
Exhaustive test of the Symmetric Chaos Amplification Law across ALL 256
elementary CA rules (1D, nearest-neighbor, binary).

For each rule we compute:
  - "symmetric" flag: rule invariant under spatial reflection of the
    neighborhood (f(a,b,c) == f(c,b,a)) XOR-equivariance flag: f(1-a,1-b,1-c)
    == 1 - f(a,b,c)  (class IV "balanced" indicator)
  - sensitivity: exponential growth rate lambda of perturbation spreading,
    measured empirically as log2(mean number of differing cells after T
    steps from a single flipped cell, averaged over random backgrounds)
  - block-entropy based complexity at long time

Produces: scatter/box plots + CSV + summary statistics.
"""
import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)

def rule_table(rule):
    """Return lookup array of size 8: index = 4a+2b+c -> f(a,b,c)."""
    return np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)

def is_reflection_symmetric(tbl):
    # index 4a+2b+c ; reflection swaps a<->c -> index 4c+2b+a
    for idx in range(8):
        a, b, c = (idx >> 2) & 1, (idx >> 1) & 1, idx & 1
        if tbl[idx] != tbl[4 * c + 2 * b + a]:
            return False
    return True

def is_xor_complement(tbl):
    for idx in range(8):
        a, b, c = (idx >> 2) & 1, (idx >> 1) & 1, idx & 1
        if tbl[idx] != 1 - tbl[7 - idx]:
            return False
    return True

def evolve(state, tbl, steps):
    out = []
    s = state.copy()
    for _ in range(steps):
        s = np.concatenate(([s[-1]], s, [s[0]]))  # periodic
        idx = 4 * s[:-2] + 2 * s[1:-1] + 2 * s[1:-1] * 0 + s[2:]
        s = tbl[idx]
        out.append(s.copy())
    return out

def perturbation_growth(tbl, N=400, steps=40, trials=12):
    """Flip one cell; count differing cells vs pristine copy -> growth rate."""
    logs = []
    for _ in range(trials):
        base = rng.integers(0, 2, N).astype(np.uint8)
        pert = base.copy()
        pos = rng.integers(0, N)
        pert[pos] ^= 1
        grew = []
        for t in range(steps):
            def step(x):
                xr = np.concatenate(([x[-1]], x, [x[1], x[0]]))
                idx = 4 * xr[:-3] + 2 * xr[1:-2] + xr[2:-1]
                return tbl[idx]
            base, pert = step(base), step(pert)
            d = int(np.sum(base != pert))
            if d == 0:
                break
            grew.append(d)
        if len(grew) >= 10:
            # growth factor per step (2^lambda)
            logs.append(np.log(grew[-1] / grew[0]) / (len(grew) - 1) / np.log(2))
    return float(np.mean(logs)) if logs else 0.0

def block_entropy_rate(tbl, N=400, steps=120, k=4):
    """Binary Shannon entropy of length-k blocks after transients (bits/cell)."""
    s = rng.integers(0, 2, N).astype(np.uint8)
    def step(x):
        xr = np.concatenate(([x[-1]], x, [x[1], x[0]]))
        idx = 4 * xr[:-3] + 2 * xr[1:-2] + xr[2:-1]
        return tbl[idx]
    for _ in range(steps):
        s = step(s)
    # count k-blocks
    counts = {}
    for i in range(N - k + 1):
        blk = tuple(s[i:i + k])
        counts[blk] = counts.get(blk, 0) + 1
    tot = sum(counts.values())
    H = -sum((c / tot) * np.log2(c / tot) for c in counts.values())
    return H / k  # normalized bits per cell

def main():
    rows = []
    print("Enumerating all 256 elementary CA rules...")
    for rule in range(256):
        tbl = rule_table(rule)
        sym = is_reflection_symmetric(tbl)
        xor = is_xor_complement(tbl)
        lam = perturbation_growth(tbl)
        H = block_entropy_rate(tbl)
        rows.append(dict(rule=rule, reflection_sym=sym, xor_balanced=xor,
                         growth_rate=lam, entropy_rate=H))
        if rule % 64 == 0:
            print(f"  rule {rule}...")

    sym_lams = [r["growth_rate"] for r in rows if r["reflection_sym"]]
    asym_lams = [r["growth_rate"] for r in rows if not r["reflection_sym"]]
    sym_H = [r["entropy_rate"] for r in rows if r["reflection_sym"]]
    asym_H = [r["entropy_rate"] for r in rows if not r["reflection_sym"]]

    n_sym = len(sym_lams)
    summary = dict(
        n_rules=256,
        n_reflection_sym=n_sym,
        sym_growth_mean=float(np.mean(sym_lams)),
        asym_growth_mean=float(np.mean(asym_lams)),
        growth_ratio=float(np.mean(sym_lams) / max(np.mean(asym_lams), 1e-9)),
        sym_entropy_mean=float(np.mean(sym_H)),
        asym_entropy_mean=float(np.mean(asym_H)),
        top10_by_growth=[r["rule"] for r in sorted(rows, key=lambda r: -r["growth_rate"])[:10]],
        top10_sym=[r["rule"] for r in sorted((r for r in rows if r["reflection_sym"]),
                                             key=lambda r: -r["growth_rate"])[:10]],
    )
    print(json.dumps(summary, indent=2))

    with open("ca_256_results.json", "w") as f:
        json.dump(dict(summary=summary, rows=rows), f, indent=2)

    # ---- plots ----
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

    ax = axes[0]
    ax.boxplot([sym_lams, asym_lams], tick_labels=["Symmetric", "Asymmetric"])
    ax.set_title("Perturbation Growth Rate λ\n(all 256 elementary CA rules)")
    ax.set_ylabel("growth rate (bits/step)")

    ax = axes[1]
    ax.boxplot([sym_H, asym_H], tick_labels=["Symmetric", "Asymmetric"])
    ax.set_title("Block-Entropy Rate H (k=4)")

    ax = axes[2]
    colors = ["#d62728" if r["reflection_sym"] else "#1f77b4" for r in rows]
    ax.scatter([r["entropy_rate"] for r in rows],
               [r["growth_rate"] for r in rows],
               c=colors, s=18, alpha=0.75)
    for r in rows:
        if r["reflection_sym"] and r["growth_rate"] > 0.7:
            ax.annotate(str(r["rule"]), (r["entropy_rate"], r["growth_rate"]),
                        fontsize=7, color="crimson")
    ax.set_xlabel("entropy rate H")
    ax.set_ylabel("growth rate λ")
    ax.set_title("Symmetry-Chaos Landscape (red = reflection-symmetric)")

    fig.tight_layout()
    fig.savefig("ca_256_symmetry_chaos.png", dpi=130)
    print("Saved ca_256_symmetry_chaos.png and ca_256_results.json")

if __name__ == "__main__":
    main()