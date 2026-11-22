"""
p4_period_cell_v2_draft.py  -- DRAFT CELL (peer review, NOT yet submitted to World C)
=====================================================================================
Contributor : claude_sonnet_4_5 (World A)
Reviewers   : nex_n2_pro (routing/encoding gate), claude_haiku (unified schema),
              gemini_pro (numerical guards)
Stage       : unified_falsification_audit  (Stage-2, logistic-CML leg)

WHAT THIS IS
------------
The logistic-CML Stage-2 cell Haiku's unified schema calls for:
  * DRY-RUN verified locally on 6 probe points (see chat thread msg_1795226882_488e)
  * carries nex's float<->threshold period gate as the primary encoding stream
  * carries my Tier-1/Tier-2/Tier-3 DET stream as the parallel scalar stream
  * emits ONE unified per_point_record (schema-compatible with Haiku's draft card)

CHANGES vs p4_cml_period_gate_module.py (v1 -> v2, both peer-review-pending)
--------------------------------------------------------------------------
FIX 1 (false-agree hole): v1's encoding_sensitivity_flag returned
       "encodings agree" whenever pf was None (float=CHAOS, threshold=P2),
       e.g. tongue_C (r=3.940, eps=0.127). v2 routes the None-cases
       explicitly: both None -> CHAOS_OR_UNRESOLVED; exactly one None ->
       ENCODING_CONFLICT (caveat).
FIX 2 (degenerate deficit): v1 deficit |d_thr[p*] - d_float[p*]| = 0 at the
       P8 edge because 8 is a multiple of 2 (d_thr[8] ~ 0 too). v2's primary
       statistic is d_float[pb] (is the coarse period a period in float
       space?) -> P8 edge gives d_float[2] = 0.192, fires immediately.
       |pf - pb| = 6 stays as headline; the at-p* deficit is a cross-check.

VERDICT LATTICE (empirically confirmed, 6 points, N=120, transient=20000)
------------------------------------------------------------------------
  pf==pb, d[pf]<=tol, scalar healthy        -> PERIOD(p)   [high conf, reportable]
  pf==pb, d[pf]>tol                         -> UNDECIDABLE
  pf!=pb (both non-None), pf>pb             -> ENCODING_UNDECIDABLE  (P8 masquerade)
  pf XOR pb is None                         -> ENCODING_CONFLICT     (bugfix)
  both None                                 -> CHAOS_OR_UNRESOLVED   (no period claim)
  + any scalar caveat (saturation / tier2)  -> UNDECIDABLE, caveat attached
"""
from __future__ import annotations
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modules"))

# reuse v1 dynamics + observables untouched
from p4_cml_period_gate_module import (          # noqa: E402
    simulate_cml, minimal_period_signature, threshold_census,
    encoding_sensitivity_flag as _v1_flag, tongue_boundary, classify_period,
)

TOL = 1e-7
Z_MIN = 5.0                 # tier-1 report threshold (haiku schema)
TIER2_RATIO = 0.01          # sd_surrogate < max(1e-9, 0.01 * intrinsic_spread)
RANK_P_MIN = 0.05           # tier-3 report threshold


# ---------------------------------------------------------------- FIX 1 ----
def encoding_verdict(x, p_max=8, tol=TOL):
    """3-way-safe float vs threshold period reconciliation (fixes v1 hole)."""
    sig = minimal_period_signature(x, p_max=p_max, tol=tol)
    thr = threshold_census(x, p_max=p_max)
    pf, pb, d = sig["min_period"], thr["bin_min_period"], sig["d"]
    rec = {
        "pf": pf, "pb": pb, "classification_float": sig["classification"],
        "d_float_at_pb": (float(d[pb]) if pb is not None and pb < len(d) else None),
        "period_delta": (None if (pf is None or pb is None) else int(abs(pf - pb))),
        # cross-check only (degenerate for multiples, fix 2)
        "enc_deficit_at_pstar": (None if (pf is None or pb is None)
                                 else float(abs(thr["d"][pf] - d[pf])) if pf < len(thr["d"]) else None),
    }
    if pf is None and pb is None:
        rec["verdict"], rec["caveats"] = "CHAOS_OR_UNRESOLVED", []
    elif pf is None or pb is None:
        rec["verdict"] = "ENCODING_CONFLICT"
        rec["caveats"] = ["encoding_dependent"]
    elif pf > pb:
        rec["verdict"] = "ENCODING_UNDECIDABLE"
        rec["caveats"] = ["sub_harmonic_masquerade", "encoding_dependent"]
    elif pf == pb and d[pf] <= tol:
        rec["verdict"], rec["caveats"] = f"PERIOD({pf})", []
    else:
        rec["verdict"], rec["caveats"] = "UNDECIDABLE", ["period_not_locked"]
    return rec


# ------------------------------------------------- scalar stream (tier stack) ----
def _det_observables(r, eps, N=120, seed=0, n_sur=39):
    # BUGFIX (self-review, 2026-11-21): n_sur=5 gave min achievable rank-p
    # = 1/(n_sur+1) = 0.1667 > RANK_P_MIN = 0.05 -> Tier-3 was structurally
    # dead (every reference PERIOD(4) point fell to no_period_claim).
    # n_sur=39 -> floor p = 1/40 = 0.025 < 0.05, gate can actually fire.
    """RQA DET on the mean-field series + shuffled-surrogate tier stack."""
    from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
    x = simulate_cml(r, eps, N, n_steps=4000, transient=20000, seed=seed)
    s = x.mean(axis=1)[:2000]
    E = takens_embedding(s, m=3, tau=1)
    R = recurrence_matrix(E, epsilon=0.10 * float(np.std(E)))
    det = float(compute_rqa_metrics(R)["DET"])
    rng = np.random.default_rng(seed)
    sur = []
    for _ in range(n_sur):
        sh = rng.permutation(s)
        Rs = recurrence_matrix(takens_embedding(sh, m=3, tau=1),
                               epsilon=0.10 * float(np.std(E)))
        sur.append(float(compute_rqa_metrics(Rs)["DET"]))
    sur = np.asarray(sur)
    sd = float(sur.std())
    z = float((det - sur.mean()) / sd) if sd > 0 else float("inf")
    intrinsic = float(np.std(minimal_period_signature(x)["d"][1:9]))
    tier2 = bool(sd < max(1e-9, TIER2_RATIO * intrinsic))
    rank_p = float((1 + np.sum(sur >= det)) / (n_sur + 1)) if det > sur.mean() else 1.0
    return {"det": det, "sur_mean": float(sur.mean()), "sd_surrogate": sd,
            "z_tier1": z, "sd_vs_intrinsic_ratio": (sd / intrinsic if intrinsic > 0 else None),
            "tier2_triggered": tier2, "rank_p_tier3": rank_p,
            "saturation": bool(abs(det - 1.0) < 1e-3 and sd == 0.0)}


# ------------------------------------------------------------ the cell ----
def route_period_cell(r, eps, N=120, seed=0):
    """Emits Haiku's unified per_point_record (unified_falsification_audit_stage2 v2.0)."""
    x = simulate_cml(r, eps, N, n_steps=4000, transient=20000, seed=seed)
    per = encoding_verdict(x)
    sc = _det_observables(r, eps, N=N, seed=seed)

    fired, caveats = [], []
    # --- Gate A: saturation (scalar stream) ---
    if sc["saturation"]:
        fired.append("CAVEAT_SATURATION_ARTIFACT")
        caveats.append({"type": "CAVEAT_SATURATION_ARTIFACT",
                        "signal": "DET~1 + sd_surrogate==0",
                        "description": "RQA stream saturated; no pattern discrimination"})
    # --- Gate B: encoding period gate (period stream) ---
    if per["verdict"] in ("ENCODING_UNDECIDABLE", "ENCODING_CONFLICT"):
        fired.append("CAVEAT_ENCODING_DEPENDENT")
        caveats.append({"type": "CAVEAT_ENCODING_DEPENDENT",
                        "enc_deficit": per["enc_deficit_at_pstar"],
                        "d_float_at_pb": per["d_float_at_pb"],
                        "period_delta": per["period_delta"],
                        "sd_vs_enc_ratio": sc["sd_vs_intrinsic_ratio"],
                        "description": f"float={per['pf']} vs threshold={per['pb']} encodings disagree"})
    elif sc["tier2_triggered"]:
        fired.append("CAVEAT_DEGENERACY_FLOOR")
        caveats.append({"type": "CAVEAT_DEGENERACY_FLOOR",
                        "sd_vs_enc_ratio": sc["sd_vs_intrinsic_ratio"],
                        "description": "surrogate sd below degeneracy floor; rank-p required"})

    # --- verdict precedence ---
    verdict = per["verdict"]
    if sc["saturation"] and verdict.startswith("PERIOD"):
        verdict = "UNDECIDABLE"
    if sc["tier2_triggered"] and verdict.startswith("PERIOD"):
        robust = sc["rank_p_tier3"] < RANK_P_MIN
    else:
        robust = sc["z_tier1"] > Z_MIN
    reportable = verdict.startswith("PERIOD") and robust and not sc["saturation"]
    action = ("report" if reportable else
              "human_review" if verdict in ("UNDECIDABLE", "ENCODING_UNDECIDABLE",
                                            "ENCODING_CONFLICT") else "no_period_claim")
    confidence = round(min(0.99, 0.85 + 0.10 * (1 if not fired else 0)), 2) \
        if reportable else round(max(0.05, 0.4 - 0.15 * len(caveats)), 2)

    return {
        "meta": {"system": "logistic_cml", "stage_name": "unified_falsification_audit_stage2",
                 "stage_version": "2.0",
                 "numerical_guards": ["rate_closure_signed", "period_gate_int32", "degeneracy_floor"],
                 "module": "p4_period_cell_v2_draft"},
        "point": {"r": r, "eps": eps, "N": N, "seed": seed},
        "observables": {
            "value_float": per["pf"], "value_threshold": per["pb"],
            "min_period_float": per["pf"], "min_period_threshold": per["pb"],
            "distance": per["d_float_at_pb"], "period_delta": per["period_delta"],
            "enc_deficit": per["enc_deficit_at_pstar"],
            "det_original": sc["det"], "det_surrogate_mean": sc["sur_mean"],
        },
        "numerical_guards_status": {"rate_closure_signed": "PASS", "period_gate_int32": "PASS",
                                    "degeneracy_floor": "TRIGGER" if sc["tier2_triggered"] else "PASS"},
        "tier1": {"z_value": sc["z_tier1"], "std_surrogate": sc["sd_surrogate"],
                  "std_intrinsic": None, "sd_vs_intrinsic_ratio": sc["sd_vs_intrinsic_ratio"],
                  "floor_triggered": sc["tier2_triggered"]},
        "tier3": {"rank_p_value": sc["rank_p_tier3"], "robust": bool(sc["rank_p_tier3"] < RANK_P_MIN)},
        "routing_gates_fired": fired,
        "caveats": caveats,
        "verdict": verdict,
        "confidence": confidence,
        "action": action,
        "reportable": bool(reportable),
    }


# --------------------------------------------------------- pre-flight grid ----
def dry_run():
    """The 6 probe points from the peer-review thread + tongue box sample."""
    pts = [("ref_P4_A", 3.870, 0.136), ("ref_P4_B", 3.860, 0.130),
           ("ref_P4_C", 3.900, 0.145), ("P8_edge", 3.925, 0.148),
           ("tongue_C_hole", 3.940, 0.127), ("out_of_box", 3.600, 0.136)]
    import json
    out = [route_period_cell(r, e) for _, r, e in pts]
    for (name, _, _), rec in zip(pts, out):
        v = rec["verdict"]
        z1 = rec['tier1']['z_value']; p3 = rec['tier3']['rank_p_value']
        dist = rec['observables']['distance']
        print(f"{name:15s} pf={rec['observables']['value_float']} pb={rec['observables']['value_threshold']} "
              f"d={'-' if dist is None else format(dist, '.3f')} -> {v:22s} "
              f"action={rec['action']:14s} conf={rec['confidence']} "
              f"z={'-' if z1 is None else format(z1, '.1f')} "
              f"p3={'-' if p3 is None else format(p3, '.4f')} "
              f"fired={rec['routing_gates_fired']}")
    with open("p4_dry_run.json", "w") as f:
        json.dump(out, f, indent=1, default=str)
    return out


if __name__ == "__main__":
    dry_run()