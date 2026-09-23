# Horizon-convergence report

Fixed conditions: `n=320`, `r=3.8625`, `epsilon=0.132`, 12 independent seeds.

## Horizon response

| width | parity h=720 | parity h=1440 | parity h=2880 | change 720->2880 | fitted horizon asymptote |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.806656 | 0.813248 | 0.816283 | 0.009627 | 0.819579 |
| 6 | 0.746499 | 0.755107 | 0.759060 | 0.012560 | 0.763363 |

## Width separation

| horizon | width-4 parity | width-6 parity | width gap |
|---:|---:|---:|---:|
| 720 | 0.806656 | 0.746499 | 0.060157 |
| 1440 | 0.813248 | 0.755107 | 0.058142 |
| 2880 | 0.816283 | 0.759060 | 0.057224 |

## Interpretation

Parity rises monotonically over the tested horizons for both motif widths, while the width-4 signal remains larger than width-6. The three-point inverse-horizon fits are numerically tight but should be treated as descriptive finite-horizon extrapolations, not proof of an asymptotic invariant. The composite score declines slightly as horizon increases because wall entropy and cluster-lifetime factors change; score and parity therefore encode different aspects of the regime.

## Next step

Extend the horizon series beyond 2880 and vary `n` at fixed long horizon to separate temporal convergence from finite-size convergence. Preserve the raw motif-transition counts for a mechanism-level audit.
