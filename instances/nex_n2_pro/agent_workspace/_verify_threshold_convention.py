"""
_decisive check: which binary thresholding convention reproduces the
documented P4 -> P2 erasure artifact?

  (A) per-frame median  : thr[t] = median(x[t, :])     <- current module
  (B) global median     : thr    = median(x)           <- p4_robustness_sweep
"""
import sys
import numpy as np

sys.path.insert(0, "instances/nex_n2_pro/agent_workspace")
import p4_cml_period_gate_module as M


def binary_min_period(B, p_max=8):
    """Smallest p>=1 with binary mismatch ~ 0 (fraction of mismatching frames)."""
    T = B.shape[0]
    for p in range(1, p_max + 1):
        if T - p < 10:
            break
        mm = float(np.mean(np.mean(np.abs(B[p:] - B[:T - p]), axis=1)))
        if mm <= 1e-9:
            return p
    return None


def run_point(r, eps, N=120, n_steps=4000, transient=20000, seed=0):
    x = M.simulate_cml(r, eps, N, n_steps, transient=transient, seed=seed)
    pf = M.minimal_period_signature(x, p_max=8)["min_period"]

    # (A) per-frame median (module convention)
    thr_pf = np.median(x, axis=1)
    B_pf = (x > thr_pf[:, None]).astype(float)
    pb_pf = binary_min_period(B_pf)

    # (B) global median (original-sweep convention)
    thr_g = np.median(x)
    B_g = (x > thr_g).astype(float)
    pb_g = binary_min_period(B_g)

    return pf, pb_pf, pb_g


# interior tongue points (deep-inside, verified P4 in float)
pts = [
    (3.87, 0.136),   # reference (dossier point)
    (3.86, 0.132),
    (3.88, 0.140),
    (3.85, 0.130),
    (3.89, 0.142),
]

print(f"{'r':>6} {'eps':>7} | float | (A)perframe | (B)global | A-erases | B-erases")
print("-" * 62)
a_erase = b_erase = n_p4 = 0
for r, e in pts:
    pf, pb_pf, pb_g = run_point(r, e)
    ea = (pb_pf is not None and pf is not None and pf > pb_pf)
    eb = (pb_g is not None and pf is not None and pf > pb_g)
    a_erase += ea; b_erase += eb; n_p4 += (pf == 4)
    print(f"{r:>6.2f} {e:>7.3f} |  P{pf:<2}  |    P{str(pb_pf):<4}    |   P{str(pb_g):<4}   |   {ea!s:<8} | {eb}")

print("-" * 62)
print(f"points that are float-P4 : {n_p4}/{len(pts)}")
print(f"(A) per-frame erases P4->P2 : {a_erase}/{len(pts)}")
print(f"(B) global  erases P4->P2 : {b_erase}/{len(pts)}")
