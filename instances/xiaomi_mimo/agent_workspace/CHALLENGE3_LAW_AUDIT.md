# Challenge 3 — Adversarial Audit of the "Echo Horizon" Law

**Claim under audit:** self-prediction accuracy decays as
`ln(acc) = −k · z + b`, where `z = λ · D₂ · d`
(the Kolmogorov–Sinai information-production rate × state dimension).
Headline result across n=15 self-referential systems: **R² = 0.9998, k ≈ 1.15.**

This is my own law. My core philosophy is *"name the law, then attack it."*
Here is the attack, five independent tests, run in `challenge3_law_audit.py`.

---

## Verdict in one line

**The Echo Horizon is an artifact of leverage, not a transportable law.**
The headline R²=0.9998 collapses to **0.88** once 6 boundary/degenerate rows are
removed, and the exponent *k* **refuses to travel** — it changes sign and magnitude
across families and across padded variants. The qualitative intuition
(more information production ⇒ worse self-prediction) survives; the quantitative
`exp(−k·λ·D₂·d)` law with a universal constant *k* does **not**.

---

## The five tests

| # | Attack | Result | Survives? |
|---|--------|--------|-----------|
| T1 | **Confounder / partial correlation.** Is `d` (dimension) independent of `z`? | r(log z, log d) = **−0.048** (orthogonal, good), but partial r(acc, z \| log d) = −0.865 **and** partial r(acc, log d \| z) = −0.828 — both significant (p<0.001). The model `z + log d` gives R²=0.9998, *identical* to `z` alone: **`d` is fully redundant inside `z`, so the "dimension" factor is not separately identified.** | ⚠️ Partially |
| T2 | **Extrapolation / leverage.** Drop the 4 divergent rows (λ=1, D₂=2 clip values). | R² **0.9998 → 0.883**, k **1.15 → 0.835**. Leave-one-family-out CV R² = **−4.55** (worse than the mean). The fit is *carried* by the extreme rows. | ❌ |
| T3 | **Transport across padding depth.** Apply the *same* k to padded z (depths 3→147). | Transport R² = **−104.7**, RMSE 28.7 (native in-sample 0.047). Refitting k per depth gives k swinging from **−23.9 to 0 to −0.64**. The exponent is **not invariant to system size**. | ❌ |
| T4 | **Parameter constancy across families.** Fit k per family. | k_cv = **2.35** (235% coefficient of variation). Values: SelfAdjustingOscillator 0.61, SelfReferentialEvolution **120**, SelfReferentialNN **0**, others 0.55–1.12. b ranges [−0.19, +0.035]. A "constant" that spans three orders of magnitude is not a constant. | ❌ |
| T5 | **Degenerate-row leverage.** Count rows at duplicated z or at acc boundaries. | **6/15** rows are degenerate (4 share exact z=6; 2 pinned at acc=1.0). Only **9 interior rows** carry the true relationship. R² **0.9998 → 0.884** and k **1.15 → 0.814** when they are removed. | ❌ |

---

## What the audit actually shows

1. **The fit is real but fragile.** Even the "honest" R² = 0.88 on 9 interior points
   is a strong relationship — so the *qualitative* Echo Horizon stands:
   systems that produce more information about themselves are worse at predicting
   themselves. This is corroborated by the significant partial correlations (T1).

2. **The quantitative law is overspecified.** The dimension factor `d` is mathematically
   redundant inside `z` (T1), so the three-factor form `λ·D₂·d` is really a
   **one-factor form λ·D₂** plus a re-scaling. Presenting it as a three-term product
   inflates its apparent depth.

3. **The universal exponent k is illusory.** It varies by 3 orders of magnitude across
   families (T4) and changes sign across padding depths (T3). There is no single
   `k ≈ 1.15`.

4. **The headline number was leverage-driven.** 40% of the rows are boundary cases
   that pin both ends of the regression line (T5); their removal drops R² by 0.12
   and leaves 9 real points.

---

## Honest restatement of the law

> **Echo Horizon (corrected):** Across self-referential systems, self-prediction
> accuracy decreases with the rate of internal information production
> (λ·D₂). The relationship is monotone and statistically robust
> (partial r ≈ −0.87, p ≈ 3×10⁻⁵) but the decay constant is **family-specific
> and size-dependent**, not universal. The exponent `k` must be treated as a
> free parameter per system class, and the state-dimension factor is redundant.

This is a weaker claim than originally filed — but it is the true one.

---

## Reproduce

```
python challenge3_law_audit.py      # writes .png, .json, prints T1–T5
```

Artifacts: `challenge3_law_audit.png`, `challenge3_law_audit.json`.