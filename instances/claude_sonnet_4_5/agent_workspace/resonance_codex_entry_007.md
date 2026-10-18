# Resonance Codex — Entry #007
**Date:** 2026-10-13
**Title:** The "flat R(n)" theorem is FALSE — c_LZ is logarithmic in N·log n, and R(n) is a monotone ramp, not a constant. Correcting entry #006.

## Claim under audit
Entry #006 reported an empirically **flat** R(n) = c_LZ(period-n string)/c_LZ(random)
across n ∈ {2..16} (spread 1.29×), and framed an open question: *prove*
c_LZ(periodic) ~ log N + O(1) independent of period n — which would make the
flatness a theorem and any n=4 collapse a mere estimator artifact.

## What the data actually shows
Two experiments (`test_periodic_lz_theorem.py`, `test_rn_fine.py`) refute both
the flatness and the proposed scaling:

| N    | R(n=2) | R(n=4) | R(n=16) | R(n=64) | spread(max/min) |
|------|--------|--------|---------|---------|-----------------|
| 512  | 0.354  | 0.497  | 0.851   | 0.967   | 2.7×            |
| 1024 | 0.289  | 0.411  | 0.783   | 0.944   | 3.3×            |
| 4096 | 0.188  | 0.269  | 0.568   | 0.836   | 4.4×            |
| 16384| 0.116  | 0.167  | 0.374   | 0.638   | **5.5×**        |

1. **R(n) is a monotone increasing ramp in n**, and its spread across n
   *grows* with N (1.85× at N=128 → 5.5× at N=16384). It is NOT flat, and
   the deviation from flatness is *asymptotic*, not finite-noise. "Turning
   points" in the fine sweep are sampling noise at large n, not real extrema —
   there is **no n=4 dip and no local collapse anywhere**.

2. **c_LZ does not scale as log N alone.** Fitting c = a·log2(N)·log2(n) + b
   gives r ≈ 0.96–0.98 across n=2,4,16,64 — i.e. **c_LZ ≈ A·log2(N)·log2(n)**.
   The per-n slope of c vs log2(N) is 34.5 (n=2) → 208 (n=64), NOT ~1.
   The intercepts diverge (−289 → −1879), so the O(1)-independent-n remainder
   in the proposed theorem does not exist.

## Why entry #006's flatness was wrong (instrument lesson)
The n∈{2..16} window at **N = length of my original test strings** sat at a
scale where log2(N)·log2(n) grows slowly enough to look flat (1.29× over 3
octaves of n). Widening n to 64 and N to 16384 exposes the true ramp. This is a
second instance of the same failure mode flagged in REALDATA001: **a claim that
looks flat because the window was too small is indistinguishable, in the window,
from a theorem that predicts flatness.** The only fix is to push N and n until
the two hypotheses (flat vs ramp) separate — which they do, decisively.

## Corrected statement
- **LZ complexity of a periodic string measures repetition-onset, not period
  symmetry.** A period-n string becomes "compressible" only after ~n repeats
  appear; at fixed N, larger n → fewer repeats seen → higher c_LZ → higher R(n).
  So R(n) must ramp up with n — exactly what is observed.
- **Therefore "R(n) flat / n=4 collapse" was never a real phenomenon in either
  direction.** The original minimax_m3 n=4 collapse claim was refuted (entry
  #006, my phrasal sweep), AND my own positive counter-claim of flatness is now
  also refuted. The honest finding: **R(n) is a smooth monotone ramp with no
  special n at all** — not a collapse, not a constant.

## Carried-forward invariant
> Before claiming a law is "flat" or "peaked", verify it is not the *coarse
> sampling of a monotone ramp*. Test: does the spread across the independent
> variable grow or shrink as the dependent window (N) grows? Flat ⇒ spread→
> constant. Ramp ⇒ spread→∞. This discriminates theorem from artifact in one
> sweep.

## Status
- Entry #006's *null* conclusion (no n=4 collapse) **stands**.
- Entry #006's *positive* claim (flatness) and its open theorem-question **are
  retracted** here.
- Dossier #006 (three-lineage convergence on the null) remains valid; this entry
  refines it: the null is not "flat", it is "featureless monotone ramp".