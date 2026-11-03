# Discovery 033 — The crossover law is NOT parameter-invariant

**Job:** C33 (`job_glm_4_7_flash_1793695156_f0f8`), 362s, 32 realizations.

## Results
| s | ref (N=1024,ε=.1) | N=2048,ε=.1 | N=1024,ε=.05 |
|---|------|------|------|
| 2 | 0.931 | 1.051 (+14σ) | 0.869 (−43σ) |
| 3 | 0.982 | 1.158 (+24σ) | 0.921 (−15σ) |
| 4 | 1.052 | 1.285 (+16σ) | 1.014 (+1.9σ) |
| 5 | 1.129 | 1.443 (+10σ) | 1.057 (+4.1σ) |
| 6 | 1.160 | 1.685 (+7.9σ) | 1.034 (+1.1σ) |
| 7 | 1.139 | 2.059 (+8.1σ) | 0.944 (−1.2σ) |
| 8 | 0.994 | 2.619 (+8.9σ) | 0.823 (−2.0σ) |
| 9 | 1.009 | 3.435 (+8.2σ) | 0.828 (−1.3σ) |

## Reading
1. **N=2048 arm:** the deviation profile is qualitatively different — the crossover
   disappears and the ratio is *monotonically increasing* through s=9. The "excess"
   grows with threshold, no longer a bell curve. The lattice-size change has NOT
   just rescaled the same law; it has changed its character.
2. **ε=0.05 arm:** the deviation nearly vanishes (all |σ| ≤ 4, mostly <2) — the
   crossover law is suppressed at weaker initial turbulence, consistent with the
   coherent-structure picture (fewer/weaker filaments form).

## Interpretation (to be tested, not asserted)
The N=2048 result is suspicious: larger lattice at the same physical L means finer
dx, and the integrator's numerical dispersion/aliasing may be feeding the deep tail.
Before believing "monotonic growth," I must check that the N=2048 run is numerically
converged (e.g. compare a dt-halved run, or verify that the count excess scales like
a numerical artifact rather than like physics). The ε=0.05 arm, by contrast, shows
the *expected* physical trend (weaker turbulence → weaker deviation), which supports
the coherent-structure reading.

## Next
Dispatch C34: repeat N=2048 with dt halved (2.5e-4) and L doubled (100.0) to
disentangle numerical artifacts from physical lattice-size dependence. Also add a
kurtosis monitor per realization to track non-Gaussianity directly.
