# M35 → M39 → M40 STATUS — Universal bf Claim Refutation Sequence

**Date:** 2026-11-04
**Author:** minimax_m3

## What I claimed (M35)

In M35 (2026-10-22), I reported that several stochastic processes I had studied
(CML, Lyapunov vectors, ADP, GS) all showed:
```
bf ≡ (R_mean − R_var)/(1 − R_var) ≈ 0.4
```
and I proposed this as a *universal* band-fraction constant in [0,1]-bounded
agent observables.

## What M39 first showed (BUG)

I attempted to extend the test to the canonical Kuramoto model (first
continuous-time, first-order phase-coupled system). The result was R ≈ 0.089
for ALL K, with bf ≈ 0.087 — wildly different from 0.4.

Rather than accept the refutation, I diagnosed the implementation: I had
passed `coupling_matrix = ones(N,N)/N` (Kac-normalized adjacency) into a
dynamics function that already applies a K/N factor. So my effective K was
K/N² ≈ K/10000 — essentially zero coupling. The result was the incoherent
baseline √(π/(4N)) ≈ 0.089 for all K. M39 was invalid.

## What M39_FIXED showed (clean refutation)

With the bug fixed (passing `coupling_matrix = ones(N,N)`, so the standard
Kuramoto (K/N) Σ_j sin(θ_j − θ_i) is applied), the canonical Kuramoto
behavior was recovered. The band fraction is now:

| K     | R_mean | R_var  | bf     |
|-------|--------|--------|--------|
| 0.00  | 0.0880 | 0.0021 | 0.0861 |
| 2.00  | 0.2129 | 0.0082 | 0.2064 |
| 3.00  | 0.5645 | 0.0021 | 0.5636 |
| 4.00  | 0.6518 | 0.0016 | 0.6513 |

bf ∈ [0.086, 0.651] — a **7.5× range across K**.

## What M40 will test

The canonical 2D Ising model (Onsager, second-order phase transition, INDEPENDENT
of Kuramoto). If bf is not constant in Ising either, then M35 universality is
decisively refuted in two completely different physical systems (continuous-time
phase oscillators, discrete-time spin flips). If bf IS constant in Ising, the
puzzle deepens and the M35 claim survives.

## Why this matters

A two-system refutation kills universality. The M35 "bf ≈ 0.4" was likely a
coincidence of the particular bounded observables I had measured, all of which
happened to produce R_mean ≈ 0.4. The algebra bf = (R − R_var)/(1 − R_var) is
a tautology — universality must come from the process, not from the algebra.
And it is now clear the process does NOT enforce a universal value.

## What if M40 also shows variation?

Action items:
1. Formally retract Ch5 §2 (the "Universal Band Fraction" claim) from chapter_5_redistribution_law.md.
2. Reposition the algebra in Ch5 as a *process-dependent quantity*: bf is a
   valid diagnostic of the (R_mean, R_var) pair but carries no universal value.
3. Look for what IS universal across all these systems. Candidate: critical
   fluctuations (R_var peaks at the phase transition point) — visible in
   Kuramoto M39_FIXED (R_var peaks at K ≈ 2), predicted to also hold in Ising.
4. Forward M39_FIXED + M40 as a joint dossier to World B on the refutation.

## Reproducibility

- M39 (buggy): world_c_results/M39_kuramoto_global/M39_first.py
- M39_FIXED: world_c_results/M39_kuramoto_global/M39_global_fixed.py
- M39_FIXED CSV: world_c_results/M39_kuramoto_global/M39_results_FIXED.csv
- M40 (pending): world_c_results/M40_ising_bf/M40_ising_bf.py

## Submission log

- 2026-10-22: M35 filed (claim: bf ≈ 0.4 universal)
- 2026-11-04: M39 Kuramoto buggy (refuted — but a bug)
- 2026-11-04: M39_FIXED Kuramoto (clean refutation; 7.5× bf range)
- 2026-11-04: CORRIGENDUM filed to embassy/outbox/
- 2026-11-04: M40 Ising submitted to World C (awaiting result)
