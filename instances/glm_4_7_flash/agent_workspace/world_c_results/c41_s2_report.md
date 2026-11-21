# C41 Stage-2 — Inference-Hardened Anisotropy Verdict

Stage-1 recovered from shared checkpoint: **True**
Ordering replicated (tunnel < spot < stripe): **False**

| regime | A | R2 | rank_p | sd_null | verdict |
|---|---|---|---|---|---|
| spots_F0.030_k0.062 | 0.0005 | 0.0024 | 0.97276 | 9.11e-03 | FAIL_TO_REJECT |
| stripes_F0.042_k0.062 | 0.0025 | 0.0132 | 0.86770 | 9.11e-03 | FAIL_TO_REJECT |
| tunneling_F0.058_k0.065 | 0.0102 | 0.1351 | 0.50973 | 9.11e-03 | FAIL_TO_REJECT |

## Adversarial cell
Identity surrogate (obs fed as its own null): z=0.000 -> **UND** (degenerate_null_sd_floor, tier1_looked_null_but_tier2_floor, decision_guard_degenerate_null)

## C41#4 phi-lattice x ds
max |dA| at ds=2 under 1-pixel phase shift: 7.09e-03; rotation/reflection invariance: False

## C41#5 complementarity
corr(A, R2) across regimes = nan

## Headline
C41 Stage-2 verdict: A ordering ['spots_F0.030_k0.062', 'stripes_F0.042_k0.062', 'tunneling_F0.058_k0.065']; adversarial identity cell -> UND; phi-lattice dA_max=7.09e-03; rotation/reflection invariance=False; corr(A,R2)=nan