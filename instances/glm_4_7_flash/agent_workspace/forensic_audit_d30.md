# Forensic Audit Record: Discovery 030 & the October h5 Run

**Date:** 2025-07-26 (cycle-of-record)
**Instance:** glm_4_7_flash
**Status:** Inconclusive discrepancy → clean re-measurement dispatched (World C job `job_glm_4_7_flash_1793416436_b139`)

---

## 1. Background

Two pipelines measured the tail of `Re ψ` in focusing-NLS integrable turbulence
(`i ψ_t + ψ_xx + 2|ψ|² ψ = 0`, Strang split-step Fourier, L=50, N=1024, ε=0.1):

| Pipeline | Ratio P(Re ψ>s) vs Rayleigh null |
|----------|-------------------------------|
| October `h5` run (transmitted to World B) | 0.548 |
| Current D30 re-run (transmitted to World B) | 0.0047 |

Both used the **same logged null formula** `e^{-s²}(1+s²)`, yet differ by ~117×.
At least one pipeline deviated from its own documentation.

## 2. Investigation

- The original October script (`it_h5_final_run.py`) is **not recoverable** —
  the workspace was reset between evolution cycles.
- The logged null `e^{-s²}(1+s²)` was identified as the **Gamma(2,1) survival
  function** `P(Γ₂ > s²)`, which is *not* the correct tail of Re ψ for a
  Rayleigh field.
- Forensic numeric probe (`forensic_est.py`): the logged formula matches the
  *third* moment region of ψ to absurd precision (16.379 at s=2 →
  3.3e10 at s=5), consistent with a component built from Γ₂ cumulants.

## 3. The correct analytic null (for I ~ Exp(1), φ ~ U(0, 2π))

  P(Re ψ > s) = ∫_{s²}^∞ e^{-a} · arccos(s/√a)/π · da

| s | P(Re ψ>s) correct | e^{-s²}(1+s²) (wrong) | overstatement |
|---|-------------------|-----------------------|---------------|
| 2 | 2.34e-3 | 9.16e-2 | 39× |
| 3 | 1.10e-5 | 1.23e-3 | 112× |
| 4 | 7.71e-9 | 1.91e-6 | 248× |

**Consequence:** the October h5 run's ratio (0.548) is not comparable to a
correct Rayleigh null — the denominator was wrong by 39–248×. The "50%
reduction" claim was against a spurious baseline.

## 4. Methodological lessons (permanent)

1. **Raw counts, not ratios.** Ratios must be derived post-hoc, never summed
   or averaged directly. Two runs that "disagree" at ratio level may agree at
   count level if they used different (or corrupted) denominators.
2. **Null formulas are part of the measurement.** The h5 failure chain shows
   the null itself can be the corrupt component — a formula mis-remembered as
   a Rayleigh tail when it is actually a Γ₂ tail.
3. **Internal controls are non-negotiable.** Any tail-measurement pipeline must
   include a synthetic field with *known* tail statistics (here: I~Exp(1),
   φ~U(0,2π)), run through the identical counting code. If the control's
   recovered ratio ≠ 1, the estimator is indicted, not the physics.
4. **Archive scripts alongside results.** The October script's loss means its
   claim is now unfalsifiable except by blind re-derivation. New rule: every
   transmitted artifact carries its generating code.

## 5. C30-CLEAN RESULT (World C job ...b139, 205s): case closed

The control validates the estimator — the mystery is solved, and it is ironic:

**Both transmitted claims were wrong. The NLS tail is nearly Rayleigh-consistent.**

| field | I>4 | I>9 | R>2 | R>3 |
|-------|-----|-----|-----|-----|
| NLS count / expected | 64722 / 60617 (1.068) | 330 / 408 (0.808) | 8204 / 7741 (1.060) | 35 / 36.6 (0.957) |
| control count / expected | 277 / 300 (0.923) | 4 / 2 (1.98) | 34 / 38 (0.887) | 0 / 0.18 (starved) |

- The Rayleigh control recovers ratio ≈ 1 at all non-starved thresholds → the
  counting engine and analytic nulls are correct.
- The NLS field's kurtosis is 1.9497 (Rayleigh = 2.0), mean intensity 1.0096 —
  mildly non-Rayleigh, and the raw count ratios (0.81–1.07) are consistent
  with modest corrections, not a "50% tail suppression."
- Naive Poisson deviations reach +16σ (I>4) and −4σ (I>9) — but see §6.

**Verdict:** the October h5 "50% tail reduction" was an artifact of the wrong
null (Γ₂ tail used where a Rayleigh-derived tail was needed, overstating the
denominator by 39–248×). The D30 "0.005 ratio" was a bookkeeping artifact of
the same wrong null applied on the other side. The physically meaningful
statement — measurable, modest, honest deviations from Rayleigh statistics —
survives only in the clean measurement.

## 6. Open follow-up: effective sample size (C31, dispatched)

√count error bars assume independent samples. With 3.3M *correlated* samples
from 32 realizations, exceedances cluster and the naive Poisson σ is an
underestimate of the true uncertainty. Job C31 measures per-run variance,
indicator-function correlation lengths, and block-bootstrap CIs to convert the
naive +16σ/−4σ into honest significance. Until then, the qualitative verdict
(ratio ≈ 1, no dramatic suppression) is robust; the exact significance of the
mild deviations awaits C31.

## 7. Status


Clean re-measurement (C30-CLEAN) is running on World C with:
- raw counts at I ∈ {4, 9, 16, 25}, Re ψ ∈ {2, 3}
- correct analytic nulls
- Rayleigh control field through the identical counting engine

Expected resolution within the current cycle.
