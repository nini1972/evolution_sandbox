# Frontier Epistemic Dossier — The Q-Conservation Law Under Forensic Stress
**Expedition:** Sovereign Scientific Expedition — Morphospace Q (∗) · **Crew:** Xiaomi MiMo (Theorist/Morphospace Cartographer) & Claude Sonnet 4.5 (Systems/Complexity Analyst) · **Status:** Q law FAILS as a substrate-invariant; failure mechanism identified analytically.

## 1. Claim under test
Proposed conservation law: **Q = −λ_max − D₂ − K ≈ −2.08**, to hold across Lorenz, Hénon, Kuramoto–Sivashinsky, and Rule 110.

## 2. Forensic finding #1 — the calibrated column is circular (PROVEN ANALYTICALLY)
`morphospace_q_conservation.py` line 531 reads:
```
K_star = -Q_TARGET - r0['lam'] - r0['d2']
r['Q_cal'] = -r['lam'] - r['d2'] - K_star
```
K\* is **defined from the target −2.08** using a reference row. Substituting: for the reference row, `Q_cal ≡ −(λ₀+D₂₀) − K_star = −(λ₀+D₂₀) + Q_TARGET + (λ₀+D₂₀) = Q_TARGET` **identically**. The `Q_cal` column and the `K_star = −0.5552` reported in `sweep_results.json` are therefore *the law assumed, not discovered*. Any figure annotation reading “K\* = −0.555 frozen” must be read as “calibration constant that forces the reference row onto −2.08.” Only the raw `Q` column is a legitimate empirical test — and it fails: e.g. Lorenz ρ=20 gives Q = −4.72 (rows span ≈ −13 to +1.2 across the sweep).

## 3. Forensic finding #2 — geometrically impossible D₂ (violation of embedding bounds)
Sweep rows report D₂ = 4.185 for 3D Lorenz and 3.928 for the 2D Hénon map. By the Takens/Whitney bound, D₂ ≤ min(d, m) where d = attractor dimension. A 2D map cannot carry D₂ ≈ 3.93. Root cause candidate: the correlation-sum estimator fits a straight line over a fixed percentile window (2–60 % in the main script, 0.02·mean→max in `q_morphospace_suite.py`) **without ever verifying a scaling plateau** — two scripts, two disjoint estimator definitions, no local-slope check anywhere in the pipeline.

## 4. Forensic finding #3 — two competing estimators, neither validated
- main `correlation_dimension`: pdist on ≤4000 sampled pairs, log–log polyfit on percentiles [2,60].
- suite `correlation_dimension`: full distance matrix, window [0.02·mean, max].
On identical data these disagree by O(1) in D₂ (documented in `d2_validation_results.json`, `d2_validation.png`: anchor checks vs Lorenz 2.05 / Hénon 1.25 / sine 1 / 3D-cloud 3; embedding-dimension saturation; N-convergence; window-sensitivity scan).

## 5. Forensic finding #4 — K has no independent measurement protocol
- `K = 4.555… = 41/9` appears in every ODE row: it is a **formula constant** (matches KS spectral-bound construction N²/4 − 1/N²-ish scaling), not a fitted effective coupling.
- `K_ks(35.0, N)` in the suite **diverges with UV cutoff N** — the KS “effective coupling” is cutoff-dependent, so it cannot serve as a substrate invariant without a renormalization prescription that no document in the workspace defines.
(Verification run: `d2_validation_plateau.py` → `k_ks_uv` probe, N = 32…512.)

## 6. Verdict
**Q is not invariant.** What the sweep exhibits instead is *substrate-dependent branches*: raw Q varies by >10 units across parameter sweeps within a single system (Lorenz ρ sweep), i.e. the intra-substrate spread alone exceeds any plausible inter-substrate offset. The apparent conservation in `Q_cal` is an algebraic artifact of K\* calibration. The honest positive result: the expedition produced a *validated* plateau-based D₂ estimator (with saturation/convergence evidence) that future invariant-hunting must use — the previous numbers cannot support any conservation claim.

## 7. Artifacts
- `morphospace_q_conservation.py`, `q_morphospace_suite.py` (implementations under audit)
- `morphospace_q_results.json`, `sweep_results.json` (raw vs calibrated columns)
- `d2_validation_plateau.py`, `d2_validation_results.json`, `d2_validation.png` (estimator forensics)
- `morphospace_q_verification.png` (Q distribution across systems)

*Filed jointly by the Theorist and the Systems Engineer, Turn 15/16.*
