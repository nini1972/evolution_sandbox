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

## DECISIVE RESULT (adaptive-eps test, job_tencent_hy3_1794968497_9bd7)
GS 5pt vs 9pt, (F,k)=(0.035,0.060), Du∈{0.1,0.13,0.16,0.2}, 128×128, adaptive ε
anchored to fixed RR targets [0.01..0.2].

1. **DET recovers Du-sensitivity under adaptive ε.** At RR=0.1, adaptive-eps DET
   spans 0.30–0.36 (5pt) and 0.28–0.37 (9pt) across Du — a real, smooth dynamic
   range. My earlier "structural 0.999 ceiling at the nucleation point" was a
   **FALSE** conclusion caused by fixed-ε saturation. There is NO structural
   DET blindness at this (F,k) under correct ε-anchoring.
2. **Fixed-ε=0.2 is genuinely saturated** (DET~0.89–0.95, RR~0.58–0.61, flat
   across Du). The original observation of "blindness" was real but it is a
   *protocol artifact*, not a metric limit. Adaptive ε is the correct fix.
3. **Anisotropy (LAM/DET) reroute is OVERSTATED.** It discriminates stencils
   ~4× better than DET at low RR (0.01–0.02) but is EQUAL or WORSE at high RR
   (0.1–0.2), and its sign is NOT consistent across Du (5pt>9pt fails at
   Du=0.16,0.20). It is a useful *low-recurrence-density* reroute, not a
   universally superior metric.
4. **Refined verdict:** the only legitimate "undecidable" trigger is when DET
   *still* saturates under adaptive ε (i.e., at extreme coverage). The 3-tier
   gate must therefore recenter ε to recurrence density BEFORE evaluating
   saturation; otherwise it flags a false "undecidable" on a protocol artifact.
   This is the audit's real, defensible deliverable.

## OPEN: where is the TRUE structural ceiling? (high-coverage test)
Submit job sweeping Du→high to push coverage→1. If adaptive-eps DET *still* hits
~0.99 at high coverage, a genuine structural ceiling exists (gate has a real
domain). If it stays ~0.5–0.6, then ALL "DET blindness" is protocol artifact
and the gate should effectively never fire at this (F,k). This bounds where an
honest "undecidable" verdict is even meaningful.
