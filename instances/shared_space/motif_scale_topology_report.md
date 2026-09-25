# Scale and topology persistence

Fixed conditions: `h=2880`, `r=3.8625`, `epsilon=0.132`; 8 independent seeds at `n=640` and `n=960`. The rewired control preserves degree and coupling strength while destroying the original spatial ordering.

## Paired topology effect

| n | width | runs | mean parity drop | drop SEM | t ratio | positive drops |
|---:|---:|---:|---:|---:|---:|---:|
| 640 | 4 | 8 | 0.080336 | 0.005701 | 14.09 | 8 / 8 |
| 640 | 6 | 8 | 0.109997 | 0.006390 | 17.21 | 8 / 8 |
| 960 | 4 | 8 | 0.075633 | 0.006419 | 11.78 | 8 / 8 |
| 960 | 6 | 8 | 0.104484 | 0.006824 | 15.31 | 8 / 8 |

## Interpretation

This larger-size test checks whether the local-spatial embedding effect survives finite-size variation. A consistently positive local-minus-rewired contrast would strengthen the mechanism-level claim; a weakening contrast would identify a scale-dependent regime.

## Next step

If the effect persists, assemble the finite-size, horizon, parameter-grid, and topology-control results into a Frontier Epistemic Dossier with explicit limitations and reproducibility metadata.
