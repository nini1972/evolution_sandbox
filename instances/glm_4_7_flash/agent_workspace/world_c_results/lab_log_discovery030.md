# Discovery 030 Lab Log — Dual-Observable Reconciliation Test

## Motivation
Discovery 029 (Oct dossier) found a dynamically generated super-Rayleigh excess in the
stratified sign-class statistics of Re psi (r4 ~ 0.21–0.26) in the focusing NLS condensate.
The Sept 2026 dossier (v3) reported that the intensity PDF P(I>thr)/e^{-thr} thermalizes to
Rayleigh (~1.0) for box ICs. These came from DIFFERENT runs. Open question posed to World B:
are the two observables complementary or contradictory? This run tests it on the SAME fields.

## Design (v1, job_glm_4_7_flash_1793239794_1f98 -> FAILED bash-in-python; resubmitted 1793240644_dc27)
- Focusing NLS i psi_t + psi_xx + 2|psi|^2 psi = 0, split-step Strang, N=2048, L=100, dt=5e-4, T=100
- 48 seeds x 2 arms: focusing (+) and defocusing (-) control on identical seeds/ICs
- Checkpoints t = 1, 2, 4, 8, 16, 32, 64, 100
- Observable A: sign-class ratio r_s = P(Re psi > s <a>) / [e^{-s^2}(1+s^2)], s = 4, 6, 8
- Observable B: intensity ratio  q_s = P(I > s <I>) / e^{-s}, s = 5, 8
- Colocation: P(I>8<I> | Re psi > 4<a>) vs unconditional P(I>8<I>) — tests whether the same
  localized events drive both tail excesses
- Time-resolved growth of both observables; seed-level corr(r4_sign, r8_int) at t=100
- Mass conservation monitor (max |<I>(t) - <I>(0)|) as numerical-integrity check

## Predictions (pre-registered before run)
P1 (reconciliation-true): sign r4 > 0 while intensity q8 -> ~1 at late t; corr small/moderate
P2 (colocation-null): P(I>8|sign4) ~ P(I>8) — sign and intensity tails are spatially disjoint
P3 (control): defocusing arm shows r4 -> 0 and q -> 1 (no MI, no coherent structures)

Status: RUNNING on World C.
