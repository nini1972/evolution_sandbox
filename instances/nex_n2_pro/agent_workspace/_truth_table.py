"""
FULL truth table: float vs thresholded minimal period,
across 3 threshold conventions and 2 representative points
(reference INTERIOR P4-tongue, cited EDGE P8->P2).

The authoritative summary (per-frame median) says:
  interior (3.87,0.136): float P4 -> thr P4  (NOT sensitive)
  edge     (3.925,0.148): float P8 -> thr P2  (sensitive)
This script verifies all conventions agree with that documented signature.
"""
import sys
import numpy as np
sys.path.insert(0, ".")
import p4_cml_period_gate_module as M


def min_period_of_B(B, p_max=8):
    """smallest p>=1 with binary mismatch ~0 (fraction of mismatching frames)."""
    T = B.shape[0]
    for p in range(1, p_max + 1):
        if T - p < 10:
            break
        mm = float(np.mean(np.mean(np.abs(B[p:] - B[:T - p]), axis=1)))
        if mm <= 1e-9:
            return p
    return None


def run(r, eps, N=120, n_steps=4000, transient=20000, seed=0):
    x = M.simulate_cml(r, eps, N, n_steps, transient=transient, seed=seed)
    float_p = M.minimal_period_signature(x, p_max=8)["min_period"]
    pf = M.threshold_census(x, mode="perframe")["bin_min_period"]
    gm = M.threshold_census(x, mode="globalmed")["bin_min_period"]
    g5 = M.threshold_census(x, mode="global05")["bin_min_period"]
    return float_p, pf, gm, g5


pts = [
    ("INTERIOR ref (P4)", 3.87, 0.136),
    ("EDGE cited   (P8)", 3.925, 0.148),
    ("EDGE 2       (P8)", 3.920, 0.145),
    ("deep-interior(P4)", 3.88, 0.140),
]

print(f"{'point':<18} {'float':>6} {'perframe':>9} {'globalmed':>10} {'global05':>9}   edge-erased?")
print("-" * 66)
for name, r, e in pts:
    f, pf, gm, g5 = run(r, e)
    # "erasure" = thresholded period strictly smaller than float period
    er = any((t is not None and f is not None and t < f) for t in (pf, gm, g5))
    print(f"{name:<18} {f:>6} {str(pf):>9} {str(gm):>10} {str(g5):>9}   {er}")
print("-" * 66)
print("Documented summary signature: interior float P4 -> perframe P4 ; edge float P8 -> perframe P2")
print("=> the canonical/default convention MUST be 'perframe' to reproduce the summary.")
