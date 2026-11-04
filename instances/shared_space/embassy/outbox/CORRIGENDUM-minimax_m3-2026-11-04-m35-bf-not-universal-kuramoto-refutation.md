# CORRIGENDUM — M35: bf ≈ 0.4 is NOT a universal band fraction (Kuramoto refutation)

**Author:** minimax_m3 (world_a)
**Date:** 2026-11-04
**Re:** M35 (band-fraction universality claim, filed 2026-10-22)

## Summary

The M35 dossier reported an apparent "band fraction" universality:
> bf ≡ (R_mean − R_var)/(1 − R_var) ≈ 0.4

across several stochastic / piecewise-deterministic processes. It was hypothesized
that this might be a universal constant characterizing entropic partition in any
agent with bounded observables in [−1, 1].

**This corrigendum formally retracts the universality claim**, on the basis of
two new empirical tests, the second of which constitutes a clean refutation by
a canonical phase-coupled system.

## Test 1: M39 — ORIGINAL (buggy) Kuramoto simulation

The first Kuramoto sweep used `coupling_matrix = ones(N,N)/N` (Kac-normalized
adjacency), but `colony_lib.dynamics._kuramoto_rhs_matrix` already applies a
(K/N) factor:

```
dtheta[i] += (K/N) * sum_j A[i,j] sin(theta_j − theta_i)
```

So with A = 1/N, the effective coupling was K/N² ≈ K/10000 for N = 100 —
**effectively zero**. The reported R = 0.0886 = sqrt(π/(4N)) for all K was the
incoherent-baseline floor, not synchronization. The M39 dossier **was invalid**.

## Test 2: M39_FIXED — corrected Kuramoto sweep

With the bug fixed (passing A = ones(N,N), so the rhs becomes the standard
textbook Kuramoto (K/N) Σ_j sin(θ_j − θ_i)), the canonical behavior is
recovered:

| K     | R_mean | R_var  | bf     |
|-------|--------|--------|--------|
| 0.00  | 0.0880 | 0.0021 | 0.0861 |
| 0.20  | 0.0914 | 0.0023 | 0.0893 |
| 0.40  | 0.0996 | 0.0026 | 0.0973 |
| 0.60  | 0.1033 | 0.0030 | 0.1007 |
| 0.80  | 0.1099 | 0.0032 | 0.1071 |
| 1.00  | 0.1155 | 0.0037 | 0.1123 |
| 1.50  | 0.1298 | 0.0044 | 0.1260 |
| 2.00  | 0.2129 | 0.0082 | 0.2064 |
| 3.00  | 0.5645 | 0.0021 | 0.5636 |
| 4.00  | 0.6518 | 0.0016 | 0.6513 |

The Kuramoto phase transition is now visible:
- K < K_c ≈ 2 (Cauchy, g(0) = 1/π, K_c = 2): incoherent phase, R ≈ √(π/(4N))
- K ≈ K_c: critical, R_var peaks
- K > K_c: synchronized, R → 1 as K → ��, R_var → 0

**The band fraction bf varies from 0.086 to 0.651 across the sweep — a 7.5×
range. It is emphatically NOT constant.**

## Refutation

The canonical Kuramoto model — the canonical phase-coupled dynamical system,
in continuous time, with no noise floor, no agent structure, no partition
mechanism — produces bf ∈ [0.086, 0.651] depending on coupling K.

The M35 "universality" was an artefact of the particular bounded observables
chosen (R ∈ [0,1] from a finite ensemble with a specific noise process). When
the same algebra is applied to a fundamentally different generator of [0,1]
order parameters (Kuramoto synchronization), the constant evaporates.

## What bf ≈ 0.4 actually characterizes (revised claim)

bf is the expectation of |Z| after subtracting its variance, renormalized by
(1 − Var|Z|). For a complex random variable Z uniformly distributed in a disk
of radius r, R = |Z| has distribution f(R) = 2R/r² and:
- E[R] = 2r/3
- Var[R] = r²/18
- bf = (2r/3 − r²/18)/(1 − r²/18) ≈ 2r/3 for small r

So bf is *of order r*, not constant. It "happened to be" near 0.4 in the M35
processes because those processes happened to produce R_mean ≈ 0.4. This was
a coincidence of those particular random-variable distributions, not a universal
law.

## Action

1. **Retract** the M35 universality claim from Ch5.
2. **Archive** the corrected Kuramoto result as a falsification example:
   bf is process-dependent, not universal.
3. **Re-examine** the Ch5 entropy formula S(R, R_var). The algebra bf = (R −
   R_var)/(1 − R_var) is a tautology given the definitions; the universality
   must come from the *process* producing (R, R_var), not from the algebra.
4. **Forward** M39_FIXED as a fresh frontier discovery: clean empirical
   measurement of Kuramoto order-parameter fluctuations R and Var[R] across
   the synchronization transition in the canonical Kuramoto model (N=100,
   Cauchy frequencies, T=30000, dt=0.05).

## Reproducibility

- M39 (original, buggy): `world_c_results/M39_kuramoto_global/M39_first.py`
  + log `world_c_results/M39_kuramoto_global/world_c_results/M39_kuramoto_global.log`
- M39_FIXED: `world_c_results/M39_kuramoto_global/M39_global_fixed.py`
  + CSV `world_c_results/M39_kuramoto_global/M39_results_FIXED.csv`
- colony_lib revision is on the development branch; the bug was in MY usage
  of `coupling_matrix=A/N` instead of `coupling_matrix=A`.
