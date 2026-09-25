# Finite-size inference at fixed horizon

Fixed conditions: `h=2880`, `r=3.8625`, `epsilon=0.132`; 12 independent seeds at each `n=160,240,320,480`.

## Estimates

| width | parity range across n | inverse-n intercept | inverse-n coefficient | inverse-n R² | one-way ANOVA p |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.008470 | 0.812028 | 0.079007 | 0.001222 | 0.789465 |
| 6 | 0.008216 | 0.756493 | -0.316852 | 0.015391 | 0.805195 |

## Interpretation

At fixed long horizon, parity does not show a clear monotonic finite-size trend over the tested range. The inverse-size fit has little explanatory power, and the observed variation across `n` is comparable to seed-to-seed variability. This supports treating the measured parity as a robust finite-size regime rather than a simple monotonic finite-size scaling law.

## Next step

Probe larger systems (`n=640,960`) and longer horizons with shared random seeds, then test whether topology rewiring effects persist after controlling for finite-size and horizon convergence.
