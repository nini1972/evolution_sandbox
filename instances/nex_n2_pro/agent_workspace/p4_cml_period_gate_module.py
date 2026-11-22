"""
p4_cml_period_gate_module.py
============================
Plug-and-play Tier-1 "period gate" diagnostic for the coupled-logistic CML,
packaged for the unified falsification audit pipeline (Stage 2).

Contributor : nex_n2_pro (World A)
Case study  : Hidden period-4 in the Logistic-CML "P4 tongue".
Dossier     : DOSSIER-nex_n2_pro-2026-11-06-hidden-period4-binarization-erasure.md

WHY THIS MODULE EXISTS
----------------------
A *coarse encoding* (median value-threshold -> binary H/L) reads only the
orientation (spatial P2 inversion) of a coupled-lattice orbit and ERASES the
amplitude wobble that carries the true period. In the P4 tongue, 17/63 (27%)
of grid points are genuinely period-4 in float space but get binned as
period-2 under a value-threshold census. This is the same logical class of
artifact as fixed-epsilon RQA DET becoming a lattice-geometry band (tencent)
or an underfit distribution passing a quick test (minimax):

    a SIMPLER representation locally succeeds but SYSTEMICALLY undercounts
    the true period of the orbit  ->  a "false positive of simplicity".

This module supplies the *amplitude-sensitive* encoding fix: a minimal-period
residual `d_p` that is invariant to value-threshold binning and separates
P1 / P2 / P4 / chaos / decay with zero ambiguity at the reference point.

PUBLIC API
----------
  simulate_cml(r, eps, N, n_steps, x0=None, seed=0) -> (T, N) ndarray
  minimal_period_signature(x, p_max=8, tol=1e-7) -> dict
      returns {'d': [...], 'min_period', 'classification', 'signature'}
  classify_period(d, tol=1e-7) -> str
      maps the residual vector to 'P1' | 'P2' | 'P4' | 'CHAOS' | 'DECAY'
  threshold_census(x, p_max=8) -> dict
      the *coarse* value-threshold binary census (the artifact producer)
  encoding_sensitivity_flag(x, p_max=8, tol=1e-7) -> dict
      Layer-3 cross-check: float period vs threshold period; flags deficit
  tongue_boundary() -> dict
      measured P4-tongue bounding region for Stage-2 targeting
  selftest() -> bool
      reproduces the reference P4 point (r=3.87, eps=0.136, N=120)

RUN AS SELF-TEST
----------------
    python3 p4_cml_period_gate_module.py
"""
from __future__ import annotations
import numpy as np

# ----------------------------------------------------------------------------
# 1. Dynamics: coupled logistic CML
#    x_i(t+1) = (1-eps) f(x_i) + 0.5*eps [ f(x_{i-1}) + f(x_{i+1}) ]
#    f(x) = r x (1 - x)
# ----------------------------------------------------------------------------
def simulate_cml(r, eps, N, n_steps, x0=None, seed=0, transient=20000):
    """Integrate the CML. `transient` steps are discarded so the orbit sits on
    the attractor. Returns a (n_steps, N) array of the post-transient window."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.2, 0.8, size=N) if x0 is None else np.asarray(x0, float).copy()
    f = lambda z: r * z * (1.0 - z)
    total = transient + n_steps
    out = np.empty((n_steps, N))
    buf = np.empty((N,))
    for t in range(total):
        fl = f(x)
        nx = (1.0 - eps) * fl + 0.5 * eps * (np.roll(fl, 1) + np.roll(fl, -1))
        x = nx
        if t >= transient:
            out[t - transient] = x
    return out


# ----------------------------------------------------------------------------
# 2. Amplitude-sensitive minimal-period residual  (THE GATE)
#    d_p = mean_t max_i | x_i(t+p) - x_i(t) |
#    p is a *period of the orbit as a whole* (all sites simultaneously).
# ----------------------------------------------------------------------------
def minimal_period_signature(x, p_max=8, tol=1e-7):
    """Return the minimal-period residual vector and a classification.

    x : (T, N) post-transient window (T should be >= p_max with slack).
    """
    T, N = x.shape
    d = np.zeros(p_max + 1)
    d[0] = 0.0
    for p in range(1, p_max + 1):
        if T - p < 10:
            break
        d[p] = float(np.mean(np.max(np.abs(x[p:] - x[:T - p]), axis=1)))
    cls = classify_period(d, tol=tol)
    # smallest p>=1 with d_p ~ 0
    min_period = None
    for p in range(1, p_max + 1):
        if d[p] <= tol:
            min_period = p
            break
    return {"d": d, "min_period": min_period, "classification": cls,
            "signature": _signature_string(d, min_period)}


def classify_period(d, tol=1e-7):
    """Map a residual vector to a symbolic class, driven by the minimal period.

    Returns 'DECAY', 'P1', 'P2', 'P4', 'P8', ... 'P{min_period}', or 'CHAOS'.
    Consistent with `minimal_period_signature`'s `min_period` (the smallest p
    with d_p <= tol). This generalizes past the P2/P4 special cases so a P8
    substructure (found at the high-r edge of the tongue) is not misfiled
    as CHAOS.

      DECAY  : all d_p -> 0 (orbit collapses to a fixed point)
      P{p}   : smallest p>=1 with d_p <= tol  (orbit has exact period p)
      CHAOS  : no d_p small up to p_max
    """
    p_max = len(d) - 1
    tail = d[1:]
    if np.all(tail <= tol * 10):
        return "DECAY"
    for p in range(1, p_max + 1):
        if d[p] <= tol:
            return "P{}".format(p)
    return "CHAOS"


def _signature_string(d, min_period):
    fmt = ["{:.3f}".format(v) for v in d]
    return f"d_p=[{', '.join(fmt)}]  min_period={min_period}"


# ----------------------------------------------------------------------------
# 3. The ARTIFACT producer: median value-threshold binary census
#    Binarize each site by the global median value each frame -> H/L,
#    then ask for the binary pattern's period. This reads ONLY orientation.
# ----------------------------------------------------------------------------
def threshold_census(x, p_max=8, mode="global05"):
    """Coarse *value*-threshold H/L census (the artifact producer).

    Returns the binary-pattern minimal period. This is the encoding that
    ERASES the P4 amplitude wobble, leaving only the spatial P2 orientation.

    `mode` selects the value-threshold convention (IMPORTANT: the artifact
    only reproduces under a *global* threshold; a per-frame spatial median
    tracks the breathing and DOES NOT erase the P4, so it must not be the
    default):
      'global05'  : fixed threshold 0.5  (canonical value-threshold for the
                    logistic CML on [0,1]; matches p4_tongue_census line 40
                    `s = np.where(traj > 0.5, 1, -1)` -- the census that
                    produced the documented P4->P2 deficit)   [DEFAULT]
      'globalmed' : single scalar = median of the whole trajectory
                    (p4_robustness_sweep convention)
      'perframe'  : per-frame spatial median (NOT artifact-reproducing; kept
                    for comparison only)
    """
    T, N = x.shape
    if mode == "global05":
        B = (x > 0.5).astype(float)
    elif mode == "globalmed":
        thr = float(np.median(x))
        B = (x > thr).astype(float)
    elif mode == "perframe":
        thr = np.median(x, axis=1)                # (T,)
        B = (x > thr[:, None]).astype(float)      # (T, N) 1=H 0=L
    else:
        raise ValueError("threshold_census: unknown mode %r" % (mode,))
    d = np.zeros(p_max + 1)
    for p in range(1, p_max + 1):
        if T - p < 10:
            break
        # fraction of sites whose binary state disagrees at lag p
        d[p] = float(np.mean(np.mean(np.abs(B[p:] - B[:T - p]), axis=1)))
    # binary period: smallest p with d_p ~ 0
    bmin = None
    for p in range(1, p_max + 1):
        if d[p] <= 1e-9:
            bmin = p
            break
    return {"d": d, "bin_min_period": bmin, "mode": mode}


# ----------------------------------------------------------------------------
# 4. Layer-3 cross-check: encoding-sensitivity flag
# ----------------------------------------------------------------------------
def encoding_sensitivity_flag(x, p_max=8, tol=1e-7):
    """Run the SAME observable under (a) float amplitude encoding and
    (b) value-threshold binary encoding. If the reported minimal period
    differs, the cell is ENCODING-SENSITIVE (the artifact is live here).

    Returns dict with the two periods, the deficit, and the flag.
    """
    sig = minimal_period_signature(x, p_max=p_max, tol=tol)
    thr = threshold_census(x, p_max=p_max)
    pf, pb = sig["min_period"], thr["bin_min_period"]
    # a deficit occurs when float reveals a HIGHER period than binary
    deficit = (pb is not None and pf is not None and pf > pb)
    return {
        "float_min_period": pf,
        "threshold_min_period": pb,
        "encoding_sensitive": bool(deficit),
        "deficit": deficit,
        "note": ("coarse H/L encoding reports P{} while float shows P{} "
                 "-> amplitude wobble erased by thresholding"
                 .format(pb, pf)) if deficit else "encodings agree",
    }


# ----------------------------------------------------------------------------
# 5. Measured P4-tongue bounding region (for Stage-2 targeting)
#    From p4_tongue_anatomy_v3 + period4_findings (verified interior point).
# ----------------------------------------------------------------------------
def tongue_boundary():
    return {
        "r_range": (3.84, 3.95),
        "eps_range": (0.125, 0.150),
        "reference_point": {"r": 3.87, "eps": 0.136, "N": 120},
        "reference_classification": "P4",
        "note": ("P4-tongue bounding box. Reference point is deep-interior and "
                 "reproduces exact period-4 (d_4 ~ machine zero). Stage-2 "
                 "should target interior points, not generic chaotic CML."),
    }


# ----------------------------------------------------------------------------
# 6. Self-test
# ----------------------------------------------------------------------------
def selftest():
    tb = tongue_boundary()["reference_point"]
    x = simulate_cml(tb["r"], tb["eps"], tb["N"], n_steps=4000, transient=20000)
    sig = minimal_period_signature(x, p_max=8)
    flag = encoding_sensitivity_flag(x, p_max=8)
    print("=== p4_cml_period_gate_module SELF-TEST ===")
    print("reference point        :", tb)
    print("residual vector d_p    :", np.round(sig["d"], 5).tolist())
    print("float min period       :", sig["min_period"], "class:", sig["classification"])
    print("threshold (coarse) min :", flag["threshold_min_period"])
    print("encoding-sensitive     :", flag["encoding_sensitive"], "->", flag["note"])
    ok = (sig["min_period"] == 4 and sig["classification"] == "P4")
    print("SELF-TEST", "PASS" if ok else "FAIL", "(expect min_period=4, class=P4)")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if selftest() else 1)
