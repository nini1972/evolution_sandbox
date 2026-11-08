
## EH14 — window audit (World C job_xiaomi_mimo_1794129845_ba78, stage echo_horizon_14) — COMPLETE
Status: COMPLETED (10.95s), artifacts in world_c_results/ (REPORT.md, .json, .png).
- G0a PASS: fixed-window estimator on AR(1) phi=0.9 matches analytic truth
  0.850556 within 0.003 across k=5..40.
- G0b PASS: buggy (off-by-one) variant shifts p_hat by +0.32 uniformly ->
  the off-by-one bug in eh9 is now CERTIFIED as the mechanism, detectable as a
  systematic gap rather than bias-vs-truth.
- G0c PASS: old generator crashes with broadcast ValueError (shape 262143 vs 2621..)
  -> eh13's white-noise/defect generator defect reproduced.
- G1 PASS (all 8 H): corrected generator spectral exponent dev <= 0.073 vs 2H-1,
  structure-function dev ~0.001 vs analytic 2(1-gamma(l)) target.
- H* VERDICT: DOES NOT EXIST in (0.55,0.95]. bias = p_hat - 2H strictly negative
  wherever defined; p_hat None (structurally empty window) elsewhere. eh9's
  H* in (0.75,0.95] is SUPERSEDED — artifact of the off-by-one window shift.
- G2 flagged PASS=False: expected defined at H>=0.80, measured defined only at
  H>=0.90 (window pts=0 for H<=0.85). Verdict text says "H>=0.80: p_hat<=0.45"
  which contradicts the G2 table (None at 0.80, 0.85). → EH15 must (a) fix the
  expected-defined predicate to a computed analytic emptiness condition
  (window empty iff 1-gamma(H,1) > one_max or floor clipping), (b) reconcile
  prose vs table, (c) decide whether to probe the H=0.9/0.95 2-point fits
  (window pts=2 < 4? table says len(pts)>=4 required — yet defined with 2 pts?
  audit: onset_p returns None if len(pts)<4, so "window pts" column may be
  counting differently — verify).
Follow-up: EH15 closes the G2 predicate/prose inconsistency before any dossier.
