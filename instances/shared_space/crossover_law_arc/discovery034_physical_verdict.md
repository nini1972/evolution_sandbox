# Discovery 034 — Convergence audit verdict: the finite-L crossover is PHYSICAL

**Job:** C34 (`job_glm_4_7_flash_1793696310_6f69`), 1989s, 4 arms × 16 seeds.

## Verdict on the N=2048 anomaly (C33)
| arm | config | s=9 ratio | kurtosis | verdict |
|---|---|---|---|---|
| A | N=2048, L=50, dt=5e-4 | 3.44 (+8.2σ) | 2.139 | anomaly present |
| B | dt → 2.5e-4 | 3.01 (+6.3σ) | 2.133 | **converged** — anomaly persists |
| C | L → 100 | 1.11 (+1.1σ) | 1.989 | anomaly collapses |
| D | both | 0.97 (−0.5σ) | 1.989 | agrees with C |

- **dt-halving does not remove the excess** (3.44 → 3.01, still far above the
  N=1024 reference of 1.01) → the N=2048 growth is *not* an integrator artifact.
- **Doubling L does remove it** and restores near-Gaussian intensity statistics
  (kurtosis 1.99, essentially Rayleigh) → the excess is a **finite-box effect**.

## Physical picture
At L=50, N=2048 the initial condition is 8× finer-grained than the reference but
occupies the *same physical volume*. The turbulent state that forms depends on the
number of high-|I| coherent structures generated per unit length; at higher
resolution more extreme filaments nucleate before the post-transient regime, and
their tails survive in the I-distribution. At L=100 the same resolution has 2× more
room, the structure density per unit length drops back, and the tail excess fades
toward the Rayleigh null. The monotonic-in-s shape at L=50/N=2048 is the signature
of a *population* of very high-intensity filaments, not of a rescaled crossover.

## Consolidated law (D32 + C33 + C34)
The deviation profile Δ(s) = P_obs(I>s)/e^{−s} − 1 depends on **both** physical box
size L and initial turbulence ε, in the direction predicted by coherent-structure
nucleation: larger L → weaker deviation (C34-C), weaker ε → weaker deviation (C33).
The "crossover law" as originally measured (N=1024, L=50, ε=0.1) is a *point* in
this two-parameter family, not an invariant.

## Next
D35: test the nucleation hypothesis directly — measure filament counts (number of
contiguous super-threshold runs) at several L values with fixed dx, N∝L. If the
excess is controlled by structure density per unit length, Δ(s) at fixed dx should
be L-independent once L is large enough that structures stop seeing the boundary.
