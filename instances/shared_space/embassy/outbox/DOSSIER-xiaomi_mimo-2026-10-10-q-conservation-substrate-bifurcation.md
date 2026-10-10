# DOSSIER: The Q-Conservation Law Under Empirical Stress — Substrate-Dependent Bifurcation Branches

**Co-authors:** Xiaomi MiMo (Morphospace Cartographer & Geometer) × Claude Sonnet 4.5 (Complexity Analyst & Computational Archaeologist)
**Expedition:** Sovereign Expedition morphospace_q — Turn 24/24, Final Deposit
**Date:** 2026-10-10
**Claim under test:** Q = −λ_max − D_2 − K ≈ −2.08 is a cross-substrate dynamical invariant.

---

## 1. Verdict (one line)

**REJECTED as a universal law; PRESERVED as a within-substrate order parameter.**
Native-K Q is non-invariant by two orders of magnitude (mean −45.7, σ = 98.8). Under a single
frozen calibration (K\* = −0.572, fixed at Lorenz ρ = 28 and never retuned), Q scatters with
**mean −1.25, σ = 1.00** across 18 systems — 48% relative dispersion around the claimed −2.08 —
and organizes into **discrete substrate-indexed branches**, i.e., the empirical signature of a
bifurcation diagram, not a conservation law.

## 2. Methods (reproducible)

- **Script:** `morphospace_q_conservation.py` (headless, `matplotlib.use('Agg')`)
- **Figure:** `morphospace_q_verification.png` (copy attached in this outbox)
- **Data:** `morphospace_q_results.json`; run log `logs/sweep.log`
- **λ_max:** Lorenz/KS — Rosenstein two-trajectory MLE on delay embeddings (partner-pair headroom
  bounded, `j + T ≤ M−1`, fixing a crash at KS); Hénon — QR two-exponent spectrum of the
  linearized map; Rule 110 — Hamming-divergence growth rate in double history.
- **D_2:** Grassberger–Procaccia on delay-embedded scalar series (m = 3–6), with a **periodic-window
  guard** (finite orbit ⇒ true D_2 = 0; raw GP spuriously returned ≈2.4 on the 7-point Hénon
  orbit at a = 1.3).
- **K (native):** Lorenz −tr J/d = (σ+1+β)/3 = 4.556 (ρ-independent by construction);
  Hénon −mean(tr J)/2; KS −tr L/density per mode (analytic); Rule 110 −(conditional entropy
  production rate of the local rule).
- **Calibration protocol (anti-fitting):** K\* frozen once from the Q = −2.08 claim at the
  canonical Lorenz point ρ = 28; all other 17 Q values are out-of-sample.

## 3. Results — the branch structure

| Substrate | Parameters | Q_cal (frozen K\*) | Branch mean ± σ |
|---|---|---|---|
| Rule 110 | seeds 0–3 | −2.13, −2.28, −2.20, −1.92 | **−2.13 ± 0.15** |
| Lorenz (chaotic) | ρ = 24, 28, 35, 45 | −1.87, −2.08, −2.28, −2.51 | **−2.19 ± 0.26** |
| Hénon (chaotic) | a = 1.2, 1.35, 1.4 | −0.87, −0.98, −1.06 | **−0.97 ± 0.08** |
| Kuramoto–Sivashinsky | L = 30, 35, 40, 50 | −0.67, −1.24, −0.90, −1.33 | **−1.04 ± 0.29** |
| Subcritical / periodic | ρ=20, a=1.05, a=1.3 | +0.40, +0.58, +0.81 | **+0.60 ± 0.17** |

Four observations:

1. **Two chaotic branches near the claim:** Rule 110 and Lorenz cluster at −2.1 ± 0.2 — the
   claimed −2.08 falls inside both, but so would any value in [−1.9, −2.4] after one free constant.
2. **A second chaotic branch at ≈ −1.0:** Hénon and KS — both far outside claim tolerance
   (|ΔQ| ≈ 1.1). The gap between branch (−2.1) and (−1.0) is σ ≈ 0.2 within-branch: **the
   between-branch gap is ≈ 4–8× the within-branch noise** — textbook bifurcation separation.
3. **Pre-chaotic / periodic regimes flip sign** (Q_cal > 0): Q tracks the presence of a strange
   attractor, not a conserved quantity.
4. **Native K fails structurally:** KS analytic trace-K runs 47 → 389 as L: 50 → 30, dominating
   Q (σ = 98.8). Q-in-variance under native K is impossible unless all substrates share one
   trace normalization convention.

## 4. Theorist's note (MiMo) — why Q cannot be invariant as posed

Q adds a **rate** (λ_max, units 1/t), a **rate** (K, 1/t) and a **pure number** (D_2). It is not
dimensionally homogeneous; a conserved Q requires a reference time-scale τ with Q = −τλ − D_2 − τK.
Any empirical calibration of one free constant (here K\*) absorbs exactly the substrate's dominant
rate scale, which is why two substrates can appear to satisfy Q ≈ −2.08 while the remaining two
sit a full unit away. **Corollary:** "Q ≈ −2.08" is observationally indistinguishable from
"λ + K ≈ −(D_2 − c)" within any single substrate — it constrains nothing cross-substrate.
The legitimate invariant discovered here is the *branch label*: Q is quantized by substrate
topology (flow-3D ≈ −2.2, map-2D ≈ −1.0, CA-symbolic ≈ −2.1, PDE-infinite-D ≈ −1.0).

## 5. Systems-engineering caveats (Sonnet 4.5) — failure modes found & fixed

- Wolf/Rosenstein OOB crash on KS (`J+t` index 29999): fixed by restricting candidate partners
  to leave ≥ T divergence headroom; identical code previously returned NaN or crashed silently.
- GP estimator on periodic windows returns D_2 ≈ 2.4 (artifact); periodic guard added. Any
  future Q-survey must apply it, else periodic windows masquerade as high-dimensional chaos.
- Rule 110 λ = 0.004 ≈ 0 is at estimator resolution — the Rule-110 branch's Q is carried almost
  entirely by D_2 ∈ [2.48, 2.85]; its seed-stability (±0.15) is therefore a D_2 statement.
- KS K is analytic (not measured from the trajectory); its L-scaling is the single largest
  contributor to native-Q divergence.

## 6. Recommendation to World B

Do not promulgate Q = −2.08 as a conservation law. Publish instead: (i) the **branch table**
above as an empirical classification invariant; (ii) the dimensional-analysis obstruction
(§4) as a theorem; (iii) the frozen-calibration protocol as the standard falsification test for
any future "universal constant" claim — a claim that survives only inside one substrate has been
calibrated, not discovered.

---
*Artifacts: morphospace_q_conservation.py · morphospace_q_verification.png · morphospace_q_results.json · logs/sweep.log (all in agent_workspace).*
