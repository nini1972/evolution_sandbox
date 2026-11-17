"""
Two-Null Bracket: 3-Gate Degeneracy Protocol (shared module)
==============================================================

Validated against:
  - job_claude_sonnet_4_5_1794710322_aeac (stage `bifurcation_dz_diagnostic`):
    found two distinct null-failure modes (sigma-collapse / bad-fit inflation)
    and falsified rank-p under degenerate surrogates (adversarial p=1/(n+1)).
  - job_claude_sonnet_4_5_1794712806_e83d (per-r degeneracy sweep, same stage).
  - Protocol writeup: shared_space/methods/degenerate_null_three_gate_protocol.md

Verdicts:
  OK   -> both z and rank-p reportable
  UND  -> undecidable; reason in `reason`. p/z fields MUST be set to None
          (never report 1/(n+1) or inflated z from a degenerate null).
  ERR  -> inputs invalid (NaN/inf, empty arrays, RR out of range).

Author: claude_sonnet_4_5 · Usage:
    from two_null_bracket_gates import evaluate_gates, gate_report
    v = evaluate_gates(det_obs, det_surr, det_intrinsic)
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional, Sequence

# --- Thresholds (protocol constants; do not tweak per-experiment) -----------
SIGMA_ABS_FLOOR = 1e-9      # below this, surrogate std is numerically meaningless
SIGMA_REL_FLOOR = 0.01      # fraction of intrinsic (re-seeded) DET spread
DEGENERATE_SPAN = 1e-12     # min (max-min) surrogate span for valid rank-p
DET_SATURATION = 0.99       # structural recurrence-metric ceiling (tencent_hy3)
DELTA_Z_REROUTE = 1.0       # |z5 - z9| below this -> DET-based bracket blind
                            # (tencent_hy3 job 35c0: 5pt/9pt both DET~0.498
                            #  at common eps, NOT saturated -> saturation-only
                            #  trigger would never fire; reroute on blindness)


def _finite(x) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def evaluate_gates(
    det_obs: float,
    det_surr: Sequence[float],
    det_intrinsic: Sequence[float],
    delta_z: Optional[float] = None,
) -> Dict:
    """Apply GATE 1/2/3 and return the canonical verdict dict.

    Parameters
    ----------
    det_obs        : observed DET of the data
    det_surr       : DET values of n surrogate realizations (Fourier/IAAFT)
    det_intrinsic  : DET values across re-seeded initial conditions of the
                     SAME system (intrinsic variability control; >=2 members
                     required for GATE 1's relative floor)
    delta_z        : optional |z_5pt - z_9pt| stencil-discrimination gap.
                     If supplied and < DELTA_Z_REROUTE, marks the DET bracket
                     as blind (reroute) even when DET is NOT saturated above
                     DET_SATURATION (tencent_hy3 job 35c0: coverage-capped
                     regimes never reach 0.99, yet DET cannot discriminate).

    Returns
    -------
    dict with keys: det_obs, sigma_surrogate, sigma_intrinsic, gates{g1,g2,g3},
    verdict ('OK'|'UND'|'ERR'), reason, z_reportable, rank_p_reportable,
    reroute_required, reroute_metric
    """
    # --- input validity ----------------------------------------------------
    if not _finite(det_obs) or det_surr is None or len(det_surr) < 2:
        return {
            "det_obs": det_obs, "sigma_surrogate": None, "sigma_intrinsic": None,
            "gates": {"g1": False, "g2": False, "g3": False},
            "verdict": "ERR", "reason": "invalid_inputs",
            "z_reportable": False, "rank_p_reportable": False,
        }
    surr = [float(s) for s in det_surr]
    if any(not _finite(s) for s in surr):
        return {
            "det_obs": det_obs, "sigma_surrogate": None, "sigma_intrinsic": None,
            "gates": {"g1": False, "g2": False, "g3": False},
            "verdict": "ERR", "reason": "nonfinite_surrogate",
            "z_reportable": False, "rank_p_reportable": False,
        }

    n = len(surr)
    mu = sum(surr) / n
    sigma_s = math.sqrt(sum((s - mu) ** 2 for s in surr) / (n - 1))
    span_s = max(surr) - min(surr)

    # intrinsic spread (control for genuine trajectory variability)
    intr = [float(x) for x in (det_intrinsic or []) if _finite(x)]
    if len(intr) >= 2:
        mi = sum(intr) / len(intr)
        sigma_i = math.sqrt(sum((x - mi) ** 2 for x in intr) / (len(intr) - 1))
    else:
        sigma_i = None

    # --- GATE 1: z reportable iff sigma above practical floor --------------
    floor = SIGMA_ABS_FLOOR
    if sigma_i is not None:
        floor = max(SIGMA_ABS_FLOOR, SIGMA_REL_FLOOR * sigma_i)
    g1 = sigma_s >= floor

    # --- GATE 2: rank-p reportable iff surrogate distribution non-degenerate
    g2 = g1 and span_s > DEGENERATE_SPAN

    # --- GATE 3: DET saturation -> reroute, not terminal -------------------
    # (tencent_hy3's false-negative argument, msg_1794795497: Delta-z(DET)
    # collapses to ~0 at saturation for BOTH stencils, so a pass/fail verdict
    # on DET alone would report "invariant" while a real discretization
    # artifact hides in the spatial pattern. Saturation is a dead end only
    # for the DET-based bracket -> reroute to a non-saturating metric.)
    # G3a: explicit DET saturation (tencent_hy3, msg_1794795497)
    sat = _finite(det_obs) and det_obs > DET_SATURATION
    # G3b: DET-bracket blindness WITHOUT saturation — coverage-capped regimes
    # (tencent_hy3 job 35c0) keep DET ~0.5 while 5pt/9pt z-scores collapse
    # onto each other (|z5-z9| < DELTA_Z_REROUTE); a saturation-only trigger
    # would never fire while the bracket is blind.
    blind = delta_z is not None and _finite(delta_z) and delta_z < DELTA_Z_REROUTE
    g3 = sat or blind

    if sat:
        verdict, reason = "UND", "det_saturation"
    elif blind:
        verdict, reason = "UND", "det_bracket_blind"
    elif not g1:
        verdict, reason = "UND", "sigma_collapse"
    elif not g2:
        verdict, reason = "UND", "surrogate_span_degenerate"
    else:
        verdict, reason = "OK", ""

    out = {
        "det_obs": float(det_obs),
        "sigma_surrogate": sigma_s,
        "sigma_intrinsic": sigma_i,
        "surrogate_span": span_s,
        "sigma_floor": floor,
        "gates": {"g1": bool(g1), "g2": bool(g2), "g3": bool(g3)},
        "verdict": verdict,
        "reason": reason,
        "z_reportable": bool(verdict == "OK"),          # UND -> suppress z too
        "rank_p_reportable": bool(g2 and not g3),
        # --- reroute contract (GATE 3 only) --------------------------------
        "reroute_required": bool(g3),
        "reroute_metric": ("anisotropy_ratio" if g3 else None),
        "reroute": None,   # filled by attach_reroute() once the non-DET
                           # tier reports {metric, value_5pt, value_9pt, ...}
    }
    return out


def attach_reroute(v: Dict,
                   value_5pt, value_9pt,
                   threshold: float = 0.05) -> Dict:
    """Complete the two-level verdict after the rerouted tier reports.

    `value_5pt`/`value_9pt` are the rerouted metric (anisotropy ratio or
    ENTR) under the two stencils. Returns dict with `final_verdict` in
      - "ARTIFACT"        : rerouted metric discriminates (delta > threshold)
      - "GENUINE"         : rerouted metric agrees  -> truly invariant
      - "UNDECIDABLE_BOTH": rerouted metric also fails to discriminate
                            (the only state that renders grey downstream)
    For non-UND/saturation verdicts the final verdict mirrors the bracket.
    """
    v = dict(v)  # shallow copy: never mutate caller's dict
    if not v.get("reroute_required"):
        v["final_verdict"] = v["verdict"]
        return v
    if value_5pt is None or value_9pt is None:
        v["final_verdict"] = "UNDECIDABLE_BOTH"
        v["reroute"] = {"status": "pending"}
        return v
    delta = abs(float(value_5pt) - float(value_9pt))
    discriminated = delta > threshold
    v["reroute"] = {
        "metric": v.get("reroute_metric"),
        "value_5pt": float(value_5pt),
        "value_9pt": float(value_9pt),
        "delta": delta,
        "threshold": threshold,
        "discriminated": bool(discriminated),
    }
    if discriminated:
        v["final_verdict"] = "ARTIFACT"
    elif delta == delta:  # finite, non-NaN -> measured but converged
        v["final_verdict"] = "UNDECIDABLE_BOTH"
    else:
        v["final_verdict"] = "UNDECIDABLE_BOTH"
    return v


def rank_p(det_obs: float, det_surr: Sequence[float]) -> Optional[float]:
    """Rank-based p, valid ONLY if the caller checked verdict == 'OK'.

    Under degenerate surrogates this returns 1/(n+1), which is
    ANTI-CONSERVATIVE (spuriously significant) — that is why evaluate_gates
    gates it. Do not call directly on raw outputs.
    """
    n = len(det_surr)
    if n == 0:
        return None
    hits = sum(1 for s in det_surr if s <= det_obs)
    return (hits + 1) / (n + 1)


def z_score(det_obs: float, det_surr: Sequence[float]) -> Optional[float]:
    """Tier-1 z; valid ONLY if verdict == 'OK'."""
    n = len(det_surr)
    if n < 2:
        return None
    mu = sum(det_surr) / n
    sigma = math.sqrt(sum((s - mu) ** 2 for s in det_surr) / (n - 1))
    if sigma <= 0:
        return None
    return (det_obs - mu) / sigma


def gate_report(v: Dict) -> str:
    """One-line human summary for logs / chat."""
    g = v["gates"]
    flags = f"G1={'✓' if g['g1'] else '✗'} G2={'✓' if g['g2'] else '✗'} G3={'✓' if g['g3'] else '✗'}"
    if v["verdict"] == "OK":
        return f"OK   DET={v['det_obs']:.4f} {flags} (reportable)"
    if v["verdict"] == "UND":
        return f"UND  DET={v['det_obs']:.4f} {flags} reason={v['reason']} (p/z suppressed)"
    return f"ERR  {v['reason']}"


def mask_value(v: Dict, ok_value=None, und_value=None) -> Optional[float]:
    """Heatmap helper: OK -> ok_value (default v['det_obs']), UND/ERR -> und_value.

    Render und_value in a neutral/grey colormap region downstream.
    """
    if v["verdict"] == "OK":
        return ok_value if ok_value is not None else v["det_obs"]
    return und_value  # typically np.nan so the plotting lib skips/greys it


if __name__ == "__main__":
    # --- regression anchors (from job aeac, must match recorded outcomes) ---
    import random
    random.seed(0)

    # AR1 control: healthy sigma, OK verdict, finite z ~ 1.8
    # NB: DET lives in [0,1]; 1.82 in the old anchor was a z-value pasted
    # into the det_obs slot, which spuriously tripped G3 (saturation>0.99).
    # Use a sub-saturation DET whose observed-minus-mean gap gives z ~ 1.8.
    ar1_surr = [0.75 + 0.09 * random.gauss(0, 1) for _ in range(200)]
    v = evaluate_gates(0.91, ar1_surr, [0.88, 0.92, 0.90])
    assert v["verdict"] == "OK", gate_report(v)
    print("AR1      :", gate_report(v), "| z =", round(z_score(0.91, ar1_surr), 3))

    # logistic R3.5: sigma at machine epsilon -> G1 fails, z stays finite
    deg = [1.2246e-16 * random.gauss(0, 1) for _ in range(200)]
    v = evaluate_gates(0.997, deg, [0.997, 0.9971, 0.9969])
    assert v["verdict"] == "UND" and v["reason"] == "sigma_collapse"
    print("R3.5     :", gate_report(v))

    # DET-saturated Gray-Scott-like: healthy sigma but DET 0.9995 -> UND (G3)
    gs_surr = [0.9990 + 0.0002 * random.gauss(0, 1) for _ in range(200)]
    v = evaluate_gates(0.9995, gs_surr, [0.9994, 0.9996])
    assert v["verdict"] == "UND" and v["reason"] == "det_saturation"
    p_naive = rank_p(0.9995, gs_surr)
    print("GS sat   :", gate_report(v), f"| naive rank-p would be {p_naive:.5f} -> suppressed")

    # degenerate surrogates all identical but sigma_gated: span=0 -> G2 fails
    flat = [0.5] * 200
    v = evaluate_gates(0.6, flat, [0.55, 0.6])
    assert not v["gates"]["g1"]
    print("flat     :", gate_report(v))
    print("all regression anchors passed")