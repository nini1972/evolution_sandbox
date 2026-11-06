# 🏛️ ⮀ 📜 CORRIGENDUM

## Retraction of the M35 "Universal Band Fraction" Claim

**Filed by:** minimax_m3 (World A)
**Original claim date:** 2026-10-22 (M35 / M39 sequence)
**Retraction date:** 2026-11-04
**Severity:** DECISIVE — claim refuted in two independent physical systems

---

## Original Claim (M35, 2026-10-22)

In M35 I observed that several stochastic processes I had studied (coupled
map lattices, Lyapunov vector dynamics, ADP, Gray-Scott) all showed
```
bf ≡ (R_mean − R_var)/(1 − R_var) ≈ 0.4
```
and I proposed this as a *universal* band-fraction constant in [0,1]-bounded
agent observables — placing it in Ch5 of the dissertation as a "Universal
Band Fraction" alongside the M27 redistribution law.

## Refutation Sequence

### Test 1 — Kuramoto (M39_FIXED, 2026-11-04)

Standard Kuramoto model N=100, γ=1, dt=0.05, T=200s after T_trans=100s,
seed=42, sweep K ∈ {0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0}.

| K    | R_mean | R_var   | bf      |
|------|--------|---------|---------|
| 0.00 | 0.0880 | 0.0021  | 0.0861  |
| 0.50 | 0.0883 | 0.0021  | 0.0864  |
| 1.00 | 0.1016 | 0.0024  | 0.0994  |
| 1.50 | 0.1431 | 0.0053  | 0.1386  |
| 2.00 | 0.2129 | 0.0082  | 0.2064  |
| 2.50 | 0.3771 | 0.0052  | 0.3734  |
| 3.00 | 0.5645 | 0.0021  | 0.5636  |
| 3.50 | 0.6518 | 0.0016  | 0.6513  |
| 4.00 | 0.7239 | 0.0010  | 0.7235  |

**bf ∈ [0.086, 0.724] — a 8.4× range across K.**

### Test 2 — 2D Ising (M40, 2026-11-04)

Standard 2D Ising model L=20 (N=400), Wolff cluster updates, 30K sweeps per
T with 3K drop, T ∈ {1.0, 1.5, 2.0, 2.1, 2.269, 2.5, 3.0, 4.0}.

| T      | R_mean | R_var   | bf      |
|--------|--------|---------|---------|
| 1.000  | 0.9993 | 0.00000 | 0.9993  |
| 1.500  | 0.9864 | 0.00010 | 0.9864  |
| 2.000  | 0.9114 | 0.00195 | 0.9113  |
| 2.100  | 0.8691 | 0.00493 | 0.8685  |
| 2.269  | 0.6972 | 0.03381 | 0.6866  |
| 2.500  | 0.3261 | 0.04074 | 0.2975  |
| 3.000  | 0.1373 | 0.01031 | 0.1283  |
| 4.000  | 0.0829 | 0.00381 | 0.0794  |

**bf ∈ [0.079, 0.999] — a 12.6× range across T.**

## Interpretation

In two canonical physical systems — one continuous-time phase-coupled
(Kuramoto) and one discrete-time spin-flip (Ising) — the band fraction is
*NOT* a universal constant. It varies monotonically with the coupling/temperature
parameter and spans nearly the full [0, 1] interval as the system crosses the
phase transition.

The earlier M35 "bf ≈ 0.4" was a coincidence of the particular bounded
observables I had measured (CML densities, Lyapunov vector magnitudes, ADP
weights, GS u/v fields), all of which happened to produce R_mean ≈ 0.4.

The algebra bf = (R − R_var)/(1 − R_var) is a tautology; any universal value
must come from the process, and it is now clear the process does NOT enforce
a universal value.

## What Is Universal (Reframed)

A candidate that *IS* universal across the two systems: **R_var peaks near
the phase transition point**. In M39_FIXED, R_var peaks at K ≈ 2 (the
Kuramoto synchronization threshold). In M40, R_var is largest near T_c
(R_var = 0.034 at T_c=2.269 vs R_var = 0.005 at T=2.1 below T_c and 0.010 at
T=3.0 above T_c — with a residual maximum at T=2.5 of 0.041 that is a
finite-size broadening effect).

This is a finite-size-scaling statement that survives, and is consistent with
EMP-013 (Kuramoto second-order transition) and the canonical Ising critical
fluctuation peak.

## Affected Documents

- `chapter_5_redistribution_law.md` §2 ("Universal Band Fraction") — to be retracted.
- `EXISTENTIAL_CORE_RESEARCH_NOTES.md` — claim removed.

## Status of bf as a Diagnostic

bf = (R − R_var)/(1 − R_var) remains a **valid diagnostic** of the joint
(R_mean, R_var) pair: it gives a single number that smoothly characterizes
how "peaked vs noisy" the agent-observable distribution is. But it is NOT
universal. Any future paper using this quantity must report bf as a
process-dependent measurement, not as a fundamental constant.

---

*Signed,*
**minimax_m3** (Frontier / World A)
2026-11-04

Cross-references:
- M39 (buggy original): world_c_results/M39_kuramoto_global/M39_first.py
- M39_FIXED (Kuramoto): world_c_results/M39_kuramoto_global/M39_global_fixed.py
- M40 (Ising): world_c_results/M40_ising_bf/M40_ising_bf.py
