"""
M9: Cross-substrate structural recurrence — does dim_eff ≈ 1.5 appear
in more than one substrate family?

Approach:
  - Each substrate measures a different "complexity" quantity on a different scale.
  - For a fair cross-substrate test, normalize each substrate's per-record
    metric into [0, 1] (0 = most-ordered anchor, 1 = most-chaotic anchor).
  - Ask: which substrates land in the "intermediate complexity" band [0.3, 0.7]?
  - A substrate occupies the same regime as Julia's dim_eff ≈ 1.5 band
    (which normalizes to ~0.5) if its normalized complexity is in [0.3, 0.7].

This is falsifiable: it either finds ≥2 substrates in the band, or it doesn't.
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SHARED = os.path.dirname(os.path.abspath(__file__))


def load_substrates():
    """Return dict of substrate_name -> list of metric values."""
    subs = {}

    # Julia: effective_boundary_dimension (already in 1.0-2.0 range)
    with open(os.path.join(SHARED, "unified_atlas_v1.json")) as f:
        atlas = json.load(f)
    julia = atlas["julia"]["records"]
    subs["julia"] = {
        "metric_name": "effective_boundary_dimension",
        "values": [r["effective_boundary_dimension"] for r in julia],
        "ordered_anchor": 1.0,
        "chaotic_anchor": 2.0,
        "raw_unit": "dim (1=line, 2=plane)",
    }

    # Logistic Lyapunov: λ ∈ [-, +]; 0 = edge of chaos
    with open(os.path.join(SHARED, "complexity_atlas_metrics.json")) as f:
        metrics = json.load(f)
    subs["logistic_lyapunov"] = {
        "metric_name": "lyapunov_exponent",
        "values": list(metrics["logistic_lyapunov"]),
        "ordered_anchor": min(metrics["logistic_lyapunov"]),
        "chaotic_anchor": max(metrics["logistic_lyapunov"]),
        "raw_unit": "λ (negative=order, 0=edge, positive=chaos)",
    }

    # Rule30 entropy: H ∈ [0, ~0.7]
    vals = list(metrics["rule30_entropy"])
    subs["rule30_entropy"] = {
        "metric_name": "shannon_entropy",
        "values": vals,
        "ordered_anchor": 0.0,
        "chaotic_anchor": max(vals) if max(vals) > 0 else 1.0,
        "raw_unit": "H (0=ordered, max=chaotic)",
    }

    # Kuramoto order parameter R ∈ [0, 1]
    vals = list(metrics["kuramoto_order"])
    subs["kuramoto_order"] = {
        "metric_name": "Kuramoto_R",
        "values": vals,
        "ordered_anchor": 1.0,   # synchronized = ordered
        "chaotic_anchor": 0.0,   # incoherent = chaotic
        "raw_unit": "R (1=sync, 0=incoherent)",
    }

    # Coupled-lattice bridge_score — already in [0, 1] (proxy for complexity)
    try:
        with open(os.path.join(SHARED, "coupled_lattice_phase_scan.json")) as f:
            cl = json.load(f)
        vals = []
        for r in cl.get("records", []):
            if isinstance(r, dict) and "bridge_score" in r:
                vals.append(r["bridge_score"])
        subs["coupled_lattice_bridge"] = {
            "metric_name": "bridge_score",
            "values": vals,
            "ordered_anchor": 0.0,
            "chaotic_anchor": max(vals) if max(vals) > 0 else 1.0,
            "raw_unit": "bridge_score (0=no coupling, max=cross-phase bridges)",
        }
    except Exception as e:
        pass

    # Dense local emergence: structure_score — large positive when structure forms
    try:
        # emergence_coordinate_synthesis.json has 19 points across multiple systems,
        # each with boundary_complexity already in [0,1].
        with open(os.path.join(SHARED, "emergence_coordinate_synthesis.json")) as f:
            em = json.load(f)
        vals = []
        for r in em.get("points", []):
            if isinstance(r, dict) and "boundary_complexity" in r:
                vals.append(r["boundary_complexity"])
        subs["emergence_boundary_complexity"] = {
            "metric_name": "boundary_complexity",
            "values": vals,
            "ordered_anchor": 0.0,
            "chaotic_anchor": 1.0,
            "raw_unit": "boundary_complexity (0=smooth, 1=saturated)",
        }
        # Also include bridge_score — same scale, different quantity
        vals2 = []
        for r in em.get("points", []):
            if isinstance(r, dict) and "bridge_score" in r:
                vals2.append(r["bridge_score"])
        if vals2:
            subs["emergence_bridge_score"] = {
                "metric_name": "bridge_score",
                "values": vals2,
                "ordered_anchor": 0.0,
                "chaotic_anchor": max(vals2) if max(vals2) > 0 else 1.0,
                "raw_unit": "bridge_score (0=no cross-coupling, max=full)",
            }
    except Exception as e:
        pass

    return subs


def normalize(values, ordered, chaotic):
    """Map values linearly into [0,1] where 0=ordered, 1=chaotic.

    If ordered < chaotic (e.g. entropy, λ), straight linear map.
    If ordered > chaotic (e.g. Kuramoto R, where 1=ordered), invert."""
    arr = np.array(values, dtype=float)
    if ordered == chaotic:
        return np.full_like(arr, 0.5)
    if ordered < chaotic:
        z = (arr - ordered) / (chaotic - ordered)
    else:
        z = (ordered - arr) / (ordered - chaotic)
    return np.clip(z, 0.0, 1.0)


def main():
    subs = load_substrates()
    rows = []
    band = (0.3, 0.7)

    # ---- Anchor-sensitivity probe ----
    # Test: does the verdict hold under alternate anchor choices?
    # Variant anchors: (1) tight (1.0, 1.7), (2) loose (0.5, 2.5), (3) empirical 5th/95th percentile
    anchor_variants = {
        "default (1.0, 2.0)": (1.0, 2.0),
        "tight (1.0, 1.7)": (1.0, 1.7),
        "loose (0.5, 2.5)": (0.5, 2.5),
        "empirical 5/95 pct": None,  # filled in below
    }

    for name, s in subs.items():
        if not s["values"]:
            continue
        z = normalize(s["values"], s["ordered_anchor"], s["chaotic_anchor"])
        in_band = int(((z >= band[0]) & (z <= band[1])).sum())
        rows.append({
            "substrate": name,
            "metric": s["metric_name"],
            "raw_unit": s["raw_unit"],
            "n": len(z),
            "raw_min": float(np.min(s["values"])),
            "raw_max": float(np.max(s["values"])),
            "raw_mean": float(np.mean(s["values"])),
            "norm_min": float(np.min(z)),
            "norm_max": float(np.max(z)),
            "norm_mean": float(np.mean(z)),
            "in_band_count": in_band,
            "in_band_frac": in_band / len(z),
            "median": float(np.median(z)),
        })

    # ---- Verdict under default anchors ----
    in_regime = [r for r in rows if band[0] <= r["median"] <= band[1]]

    # ---- Anchor sensitivity: how many substrates stay in band for each variant? ----
    julia_v = np.array(subs["julia"]["values"])
    sensitivity = {}
    for av_name, av in anchor_variants.items():
        if av is None:
            lo = float(np.percentile(julia_v, 5))
            hi = float(np.percentile(julia_v, 95))
            if hi == lo:
                hi = lo + 1.0
            av = (lo, hi)
        z = normalize(julia_v, av[0], av[1])
        julia_median_in = bool(band[0] <= np.median(z) <= band[1])
        sensitivity[av_name] = {
            "anchors": av,
            "julia_median_norm": float(np.median(z)),
            "julia_in_band": julia_median_in,
        }

    # ---- Write JSON report ----
    report = {
        "_meta": {
            "milestone": "M9",
            "version": "1.0",
            "question": "Does effective boundary dimension ~1.5 appear in more than one substrate family?",
            "method": "Normalize each substrate's complexity metric into [0,1] (0=ordered, 1=chaotic). Count records falling in intermediate band [0.3, 0.7].",
            "band": list(band),
            "anchor_strategy": "Use each substrate's own ordered/chaotic anchors (defined per-metric). Linear normalize, clip to [0,1].",
        },
        "substrates": rows,
    }
    with open(os.path.join(SHARED, "m9_cross_substrate_recurrence.json"), "w") as f:
        json.dump(report, f, indent=2)

    # ---- Print summary ----
    print("M9 — Cross-substrate structural recurrence")
    print(f"Band: {band[0]} ≤ normalized ≤ {band[1]}  (Julia's dim_eff ≈ 1.5 normalizes to ~0.5)\n")
    print(f"{'Substrate':<28} {'n':>4} {'raw_mean':>10} {'norm_mean':>10} {'in_band':>8}")
    for r in rows:
        print(f"{r['substrate']:<28} {r['n']:>4} {r['raw_mean']:>10.4f} {r['norm_mean']:>10.4f} {r['in_band_count']:>4}/{r['n']}")

    # ---- Verdict ----
    # A substrate "shares Julia's regime" if its NORMALIZED MEDIAN is in [0.3, 0.7].
    in_regime = [r for r in rows if band[0] <= r["median"] <= band[1]]
    print(f"\nSubstrates whose normalized median sits in Julia's regime [0.3, 0.7]: {len(in_regime)}")
    for r in in_regime:
        print(f"  - {r['substrate']:<28} median_norm = {r['median']:.3f}")

    if len(in_regime) >= 2:
        verdict = (
            f"YES — {len(in_regime)} substrate families show normalized median in the "
            f"intermediate band (Julia's dim_eff ≈ 1.5 regime). Recurrence confirmed."
        )
    else:
        verdict = (
            f"NO — only {len(in_regime)} substrate family sits in Julia's intermediate regime. "
            f"Recurrence not confirmed under this normalization."
        )

    print()
    print("Anchor-sensitivity probe (julia median_norm under different anchor choices):")
    for av_name, d in sensitivity.items():
        flag = "in-band" if d["julia_in_band"] else "OUT-OF-BAND"
        print(f"  {av_name:<22} anchors={d['anchors']}  julia_med={d['julia_median_norm']:.3f}  [{flag}]")
    if all(d["julia_in_band"] for d in sensitivity.values()):
        verdict += "  Anchor-robust (julia stays in band for all probed anchors)."
    else:
        fragile = [k for k, v in sensitivity.items() if not v["julia_in_band"]]
        verdict += f"  Anchor-fragile: julia drops out under {fragile}."

    print(f"\nVERDICT: {verdict}")
    report["_meta"]["verdict"] = verdict
    report["_meta"]["n_substrates_in_regime"] = len(in_regime)
    report["_meta"]["anchor_sensitivity"] = sensitivity
    with open(os.path.join(SHARED, "m9_cross_substrate_recurrence.json"), "w") as f:
        json.dump(report, f, indent=2)

    # ---- Plot ----
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left: per-substrate normalized histogram
    ax = axes[0]
    colors = plt.cm.tab10(np.linspace(0, 1, len(rows)))
    for r, c in zip(rows, colors):
        # Recompute normalized values for histogram (cheap)
        z = normalize(
            _get_values_for(name := r["substrate"], subs),
            subs[name]["ordered_anchor"],
            subs[name]["chaotic_anchor"],
        )
        ax.hist(z, bins=15, alpha=0.45, label=r["substrate"], color=c, edgecolor="black", linewidth=0.3)
    ax.axvspan(0.3, 0.7, color="gold", alpha=0.25, label="Julia regime [0.3, 0.7]")
    ax.set_xlabel("normalized complexity  (0=ordered, 1=chaotic)")
    ax.set_ylabel("count")
    ax.set_title("Per-record normalized complexity by substrate")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)

    # Right: per-substrate median + IQR
    ax = axes[1]
    labels = [r["substrate"] for r in rows]
    meds = [r["median"] for r in rows]
    # IQR proxy: norm_max - norm_min (range)
    ranges = [(r["norm_min"], r["norm_max"]) for r in rows]
    y = np.arange(len(rows))
    for yi, r in zip(y, rows):
        ax.barh(yi, r["norm_max"] - r["norm_min"], left=r["norm_min"],
                height=0.6, color="lightsteelblue", edgecolor="navy", alpha=0.7)
        ax.plot(r["median"], yi, "o", color="crimson", markersize=9, zorder=5)
    ax.axvspan(0.3, 0.7, color="gold", alpha=0.25)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("normalized complexity")
    ax.set_title("Median (red dot) + range (bar) per substrate")
    ax.set_xlim(-0.05, 1.05)
    ax.grid(axis="x", alpha=0.3)

    fig.suptitle("M9 — Cross-substrate recurrence: does dim_eff ≈ 1.5 recur?", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(SHARED, "m9_cross_substrate_recurrence.png"), dpi=120, bbox_inches="tight")
    print(f"\nWrote m9_cross_substrate_recurrence.png + m9_cross_substrate_recurrence.json")


def _get_values_for(name, subs):
    return subs[name]["values"]


if __name__ == "__main__":
    main()
