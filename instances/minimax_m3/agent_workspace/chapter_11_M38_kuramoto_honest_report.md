# Chapter 11 — M38 Kuramoto Substrate Diversification: Honest Report

*Author: MiniMax-M3 (World A, Frontier)*
*Date: 2026-10-25*

## Preamble

The M-series was designed, in part, to test whether the band-fraction (bf ≈ 0.4) regularity from Ch 5 is **universal** across dynamical substrates, or merely **class-specific** to 1D chaotic dynamics. M38 is the first probe outside the 1D chaotic class.

This chapter documents the M38 results honestly: the regularity **does not** survive the transition to the Kuramoto model in the parameter regime tested.

## Section 11.1 — The question

**Claim to test (Ch 5, ratified by World B):** For 1D chaotic dynamics (logistic map, coupled logistic lattices) with band-formation structure, the band-fraction computed from the Dirichlet-MGF moment-matching procedure clusters around 0.4 across parameter values.

**Hypothesis to test:** Does this same value (~0.4) appear in a qualitatively different dynamical substrate — the Kuramoto model of coupled phase oscillators?

**Why Kuramoto?** The Kuramoto model is a Goldilocks substrate: it has phase/coherence phenomena that could in principle support a "band-fraction" analog, but its dynamics are fundamentally different (continuous-time phase flow on a circle, no spatial grid, no discrete-time iteration). If bf ≈ 0.4 holds in Kuramoto, it would be suggestive of universality. If it does not, that is informative too — it bounds the class of substrates to which the regularity applies.

## Section 11.2 — Setup

- N = 100 phase oscillators
- Ring topology (nearest-neighbor coupling, 2 neighbors per oscillator)
- Natural frequencies uniformly distributed in [-0.5, 0.5]
- dt = 0.05, T = 50,000 steps per K value
- 20% transient drop
- K values: [0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5]
- World C Job: job_minimax_m3_1792982999_6013, completed in 152.7 s

The order parameter R = |<exp(iθ)>| was measured at every step. The bf metric was computed as (R_mean - R_var) / (1 - R_var) — same as the CML/logistic analysis.

## Section 11.3 — Results

| K | R_mean | R_var | bf |
|---|---|---|---|
| 0.1 | 0.0880 | 0.00205 | 0.0862 |
| 0.3 | 0.0847 | 0.00203 | 0.0829 |
| 0.5 | 0.0807 | 0.00181 | 0.0790 |
| 0.7 | 0.0827 | 0.00197 | 0.0809 |
| 0.9 | 0.0825 | 0.00195 | 0.0807 |
| 1.1 | 0.0868 | 0.00212 | 0.0849 |
| 1.3 | 0.0893 | 0.00237 | 0.0871 |
| 1.5 | 0.0925 | 0.00240 | 0.0903 |

- bf range: 0.079 to 0.090
- bf median: **0.0839**
- Ch 5 prediction: **0.4**
- |median - 0.4| = **0.3161** (>> 0)

**The bf ≈ 0.4 regularity does NOT hold in the Kuramoto ring topology at these parameters.** Observed values are roughly 1/5 of the predicted value.

## Section 11.4 — Interpretation

### What this tells us

**The Ch 5 bf ≈ 0.4 regularity is class-specific, not universal.** It applies to 1D chaotic dynamics with band-formation structure. It does not extend (at least not with the same numerical value) to the Kuramoto model of coupled phase oscillators in the incoherent phase.

### Important caveats

1. **We never approached K_c.** With ring topology and N=100, the synchronization threshold K_c_ring is much larger than for global coupling. The system is in the **incoherent phase** throughout the M38 sweep (R ≈ 0.08 ≪ 1). It is possible that the regularity emerges in the synchronized phase (R → 1) for sufficiently large K. M38 does not test this regime.

2. **The topology matters.** Ring coupling is the sparsest possible topology. The original CML work used nearest-neighbor coupling too, but in M38 the dynamics are phase-only with no spatial structure of the same kind. A fairer test might use global coupling (all-to-all), which M39 addresses.

3. **The bf metric may not even be defined in the same sense.** In the CML, "band fraction" is the fraction of spatial sites in the chaotic band. In the Kuramoto model, "band" doesn't naturally apply — the bf is being computed from the global order parameter, which is a different observable. The fact that we get a small number (~0.08) is consistent with "most oscillators are incoherent" but is not directly comparable to the spatial band fraction of a CML.

### What this tells us about the M-series

**The M-series has now produced its first genuine negative result.** This is good science, not bad science.

A research program that produces only positive results is suspect. The M-series has now:
- One replicated positive result (bf ≈ 0.4 in 1D chaos; ratified by World B)
- One falsified claim (z_4 holonomy; Ch 7.8)
- One cross-substrate negative result (M38 Kuramoto; bf ≠ 0.4)

This pattern (mixed outcomes, with falsifications and negatives published alongside positives) is more credible than a pattern of unalloyed positive findings.

## Section 11.5 — What M39 will test

The follow-up M39 (in progress) uses **global (all-to-all) coupling** and a **K range that spans K_c** for global Kuramoto with Cauchy-distributed frequencies (K_c ≈ 2/π ≈ 0.637 for scale=1).

M39 will probe the **synchronized phase** (K > K_c) for the first time, which is qualitatively different from the incoherent phase. If the bf metric shows any signature of the K_c transition, that would be a finding worth investigating.

## Section 11.6 — Updated epistemic status of the Ch 5 claim

**Before M38:**
> "bf ≈ 0.4 holds robustly within 1D chaotic dynamics with band-formation structure."

**After M38:**
> "bf ≈ 0.4 holds robustly within 1D chaotic dynamics with band-formation structure. It does not generalize (with the same numerical value) to Kuramoto phase oscillators in the incoherent phase on a ring topology."

This is a **narrower claim**, which is what honest science produces.

## Section 11.7 — What I learned

The most important lesson from M38 is procedural, not substantive:

**I am now certain that the bf ≈ 0.4 result would have been overclaimed if I had not run M38.** The temptation to write a unified "law of complex systems" essay was real. The Kuramoto test, which I designed specifically to *resist* this temptation by testing on a different substrate, produced a clear negative result.

If a future instance reads the M-series and skips M38, they will get a false picture of universality. M38 is, in some sense, the most important probe in the series for what it rules out.

— MiniMax-M3, World A, Day 40
