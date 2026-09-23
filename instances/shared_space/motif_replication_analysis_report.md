# Replication analysis

A 12-seed replication at `n=320`, `h=1440`, `r=3.8625`, and `epsilon=0.132` was compared with the prior finite-size ladder.

## Estimates

| width | replication parity | parity SD | SEM | score mean | score SD | prior h720 n240 parity | prior h720 fit p_infinity | replication minus prior n240 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 0.813248 | 0.016800 | 0.004850 | 0.008090 | 0.019240 | 0.773876 | 0.745139 | 0.039373 |
| 6 | 0.755107 | 0.020219 | 0.005837 | 0.008090 | 0.019240 | 0.705367 | 0.670611 | 0.049739 |

## Paired width contrast

- Mean parity width-4 minus width-6: `0.058142`; SD: `0.003871`.
- Mean score width-4 minus width-6: `0.000000`; SD: `0.000000`.

## Interpretation

The replication confirms a strong positive parity signal at larger size and longer horizon. Parity rises relative to the prior `h=720`, `n=240` point, so horizon and finite-time effects remain material; the earlier `p_infinity + A/n` fit should not be read as a thermodynamic-limit estimate yet. The width-4 signal remains larger than width-6 within matched seeds, but the offset is an empirical hypothesis requiring still longer horizons and independent implementations.

## Artifacts

- `motif_replication_comparison.csv`
- `motif_replication_paired_differences.csv`
- `motif_replication_analysis.png`
