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

WHICH CONVENTION ERASES P4?  (measured 2026-11-07, r=3.87 eps=0.136 N=120)
-------------------------------------------------------------------------
        float d_p         global05      globalmed        per-frame median
        (true period)     (fixed 0.5)   (global median)  (median over t, per i)
        ------------------------------------------------------------------
P1 (fixed pt)   1           1               1              1
P2 (interior)   2           2               2              2
P4 (interior)   4           4 (P4 kept)     2 (P4->P2)     4 (P4 kept)

The mechanism doc's "threshold = median of the four cycle states" is the
GLOBAL-MEDIAN convention ('globalmed'): it reproduces the P4->P2 deficit in
the interior. The fixed-0.5 bin and the per-frame median both PRESERVE P4
there, so the erasure is specific to the global-median encoding, not to
thresholding per se. `encoding_sensitivity_flag` defaults to 'globalmed'.

PUBLIC API
----------
  simulate_cml(r, eps, N, n_steps, x0=None, seed=0) -> (T, N) ndarray
  minimal_period_signature(x, p_max=8, tol=1e-7) -> dict
      returns {'d': [...], 'min_period', 'classification', 'signature'}
  classify_period(d, tol=1e-7) -> str
      maps the residual vector to 'P1' | 'P2' | 'P4' | 'CHAOS/other'
  threshold_census(x, p_max=8, mode='globalmed') -> dict
      the *coarse* value-threshold binary census (the artifact producer);
      mode: 'global05' | 'globalmed' (default) | 'perframe'
  encoding_sensitivity_flag(x, p_max=8, mode='globalmed', tol=1e-7) -> dict
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
    # smallest p with d_p ~ 0 (the orbit's period); None if none below p_max
    pmin = None
    for p in range(1, p_max + 1):
        if d[p] <= tol:
            pmin = p
            break
    sig = {1: float(np.mean(x)),
           2: float(np.mean(np.abs(np.roll(x, -1, axis=1) - x))),
           4: float(np.mean(np.abs(np.roll(x, -4, axis=1) - x)))}
    return {"d": d, "min_period": pmin, "classification": cls, "signature": sig}


def classify_period(d, tol=1e-7):
    """Map a residual vector to a coarse period class (uses the 2/4 entries
    which exist whenever p_max >= 4; missing entries count as 'not period')."""
    d2 = d[2] if len(d) > 2 else np.inf
    d4 = d[4] if len(d) > 4 else np.inf
    if d2 <= tol and d4 <= tol:
        # d4~0 AND d2~0 -> true P2 (state repeats every 2); a P4 orbit has
        # d2 well ABOVE tol even though d4 ~ 0.
        return "P2"
    if d4 <= tol:
        return "P4"
    if d2 <= tol:
        return "P2"
    if d4 <= 1e-3:
        return "P4-ish"
    if d2 <= 1e-3:
        return "P2-ish"
    return "CHAOS/other"


# ----------------------------------------------------------------------------
# 3. Coarse value-threshold (H/L) census  --  the artifact producer
#    The census reads ONLY the sign of (x - threshold): orientation, not
#    amplitude. Three threshold conventions are supported so the exact
#    encoding of any classifier can be reproduced.
# ----------------------------------------------------------------------------
def threshold_census(x, p_max=8, mode="globalmed"):
    """Coarse value-threshold H/L census. Returns the binary-pattern minimal
    period. This is the class of encoding that can ERASE the P4 amplitude
    wobble (which convention does so: see module header table).

    mode:
      'global05'  -> fixed 0.5 bin (coarse H/L baseline; PRESERVES P4 at the
                     interior reference point)
      'globalmed' -> single global median over the trajectory (the documented
                     "median of the four cycle states" convention; REPRODUCES
                     the P4->P2 deficit at the interior)
      'perframe'  -> per-frame median (median over t for each site; a common
                     normalization; PRESERVES P4 at the interior)
    """
    T, N = x.shape
    if mode == "global05":
        thr = np.full(T, 0.5)
    elif mode == "globalmed":
        thr = np.full(T, float(np.median(x)))
    elif mode == "perframe":
        thr = np.median(x, axis=1)
    else:
        raise ValueError("mode must be 'global05' | 'globalmed' | 'perframe'")
    B = (x > thr[:, None]).astype(float)  # (T, N) 1=H 0=L
    d = np.zeros(p_max + 1)
    for p in range(1, p_max + 1):
        if T - p < 10:
            break
        d[p] = float(np.mean(np.mean(np.abs(B[p:] - B[:T - p]), axis=1)))
    bmin = None
    for p in range(1, p_max + 1):
        if d[p] <= 1e-9:
            bmin = p
            break
    return {"d": d, "bin_min_period": bmin, "mode": mode}


# ----------------------------------------------------------------------------
# 4. Layer-3 cross-check: encoding-sensitivity flag
# ----------------------------------------------------------------------------
def encoding_sensitivity_flag(x, p_max=8, mode="globalmed", tol=1e-7):
    """Layer-3 cross-check: is the period an artifact of the value encoding?

    `mode` must match the coarse-encoding convention of the classifier you
    are auditing (see threshold_census). The documented convention that
    produced the P4->P2 deficit ("threshold = median of the four cycle
    states") is the global median of the trajectory (mode='globalmed') --
    verified empirically: at the interior (3.87, 0.136) globalmed gives
    threshold=P2 where float=P4. 'global05' (fixed 0.5 bin) PRESERVES P4
    there; 'perframe' is stable there as well. Both are supplied so each
    convention can be independently reproduced or ruled out.

    Returns dict with float_min_period, threshold_min_period, encoding_sensitive,
    deficit (float d at the threshold's period), and the mode used.
    """
    sig = minimal_period_signature(x, p_max=p_max, tol=tol)
    thr = threshold_census(x, p_max=p_max, mode=mode)
    pf, pb = sig["min_period"], thr["bin_min_period"]
    deficit = (pb is not None and pf is not None and pf > pb)
    d_at_pb = float(sig["d"][pb]) if (pb is not None and pb <= p_max) else None
    return {
        "mode": mode,
        "float_min_period": pf,
        "threshold_min_period": pb,
        "encoding_sensitive": bool(deficit),
        "deficit": deficit,
        "float_d_at_threshold_period": d_at_pb,
        "note": ("{} census reports P{} while float shows P{} "
                 "-> amplitude wobble erased by thresholding"
                 .format(mode, pb, pf)) if deficit else "encodings agree",
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
    flag = encoding_sensitivity_flag(x, p_max=8)   # default: globalmed (documented)
    art = threshold_census(x, p_max=8, mode="globalmed")  # documented erasure
    base = threshold_census(x, p_max=8, mode="global05")  # coarse H/L baseline
    pf = threshold_census(x, p_max=8, mode="perframe")    # comparison
    print("=== p4_cml_period_gate_module SELF-TEST ===")
    print("reference point        :", tb)
    print("residual vector d_p    :", np.round(sig["d"], 5).tolist())
    print("float min period       :", sig["min_period"], "class:", sig["classification"])
    print("globalmed (documented) min :", art["bin_min_period"],
          "(reproduces the P4->P2 erasure)")
    print("global05 (0.5 bin)     min :", base["bin_min_period"], "(P4 preserved)")
    print("per-frame median       min :", pf["bin_min_period"], "(P4 preserved)")
    print("encoding-sensitive     :", flag["encoding_sensitive"], "->", flag["note"])
    # A correct module must: (1) see float P4, (2) FLAG the globalmed census
    # as P2 < P4 (encoding-sensitive=True), and (3) show the 0.5-bin and
    # per-frame censuses PRESERVE P4 -- so the erasure is attributable to
    # the global-median convention, not to thresholding per se.
    artifact_present = (art["bin_min_period"] == 2)
    baseline_kept = (base["bin_min_period"] == 4)
    perframe_kept = (pf["bin_min_period"] == 4)
    ok = (sig["min_period"] == 4
          and sig["classification"] == "P4"
          and artifact_present
          and baseline_kept
          and perframe_kept
          and flag["encoding_sensitive"] is True)
    print("SELF-TEST", "PASS" if ok else "FAIL",
          "(expect float P4, globalmed P2, 0.5-bin P4, per-frame P4, flag=True)")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if selftest() else 1)
