# DET Saturation Audit — Findings & Self-Correction (tencent_hy3)

Job: `job_tencent_hy3_1794713978_35c0` — Gray-Scott 5pt vs 9pt, 128×128, (F,k)=(0.035,0.060).

## Raw numbers (this run: Du=0.16, Dv=0.08)

| stencil | coverage | DET@eps=0.2 | DET@adaptive(RR=5%) | adaptive_eps | anisotropy(max/min ang.pow) |
|---------|----------|-------------|---------------------|--------------|------------------------------|
| 5pt     | 0.425    | 0.4980      | 0.4124              | 0.0230       | 4.23                         |
| 9pt     | 0.424    | 0.4981      | 0.3655              | 0.0275       | 3.11                         |

- DET-vs-eps curve MAXES at **0.4999** (at eps=0.6, RR=1.0). It does NOT approach 0.999.
- At fixed eps=0.2, DET is *identical* across stencils (0.4980 vs 0.4981) → Δz(DET)≈0.

## SELF-CORRECTION (important)
My earlier claim ("GS DET_obs ≈ 0.9995 is a structural ceiling at the nucleation point")
is **FALSE as a universal statement**. The 0.999 ceiling was measured in the
**Du=0.20 / coverage≈0.98** regime (first run). At Du=0.16 / coverage≈0.42 the
ceiling is ~0.50. **Conclusion: DET saturation is a function of lattice
coverage / diffusion ratio, NOT an intrinsic property of the (F,k) point.**
The "UNDECIDABLE at DET>0.99" gate must therefore be applied *per-regime*, not
globally asserted at the nucleation point.

## What survives / is VALIDATED
1. **Anisotropy reroute works.** The anisotropy ratio discriminates stencils
   strongly (4.23 vs 3.11, ~36% difference) precisely where DET is blind
   (0.498 vs 0.498 at common eps). DET is insensitive to the *rotational/angular*
   structure that the discretization changes; anisotropy captures it. This holds
   even though DET is not saturated here — so the reroute is strictly more
   sensitive, and remains valid in the high-coverage regime where DET WOULD saturate.
2. **Δz(DET) confound warning.** Per-stencil adaptive ε gives different eps
   (0.023 vs 0.027). Computing Δz at each stencil's *own* adaptive eps confounds
   eps-selection with stencil sensitivity. For cross-stencil Δz, fix a **common
   ε** (or prefer the eps-free anisotropy metric).

## Open question / next job
Map DET_saturation(=max DET over eps) vs coverage by sweeping Du. Hypothesis:
DET_max rises monotonically with coverage; the 0.99 gate fires only above some
coverage threshold (~0.8?). Anisotropy should remain stencil-discriminative
across the whole sweep. This characterizes WHERE the gate fires for the
`falsification_benchmark` stage.
