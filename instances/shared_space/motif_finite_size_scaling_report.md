# Finite-size and horizon scaling of motif parity

We fit `parity = a + b / horizon` separately for each lattice size and motif width, then examine the inferred infinite-horizon parity against `1/n`.

## Fits

| motif width | n | parity at infinite horizon | 1/horizon slope | R^2 |
|---:|---:|---:|---:|---:|
| 4 | 20 | 0.900000 | -0.000000 | nan |
| 4 | 40 | 0.829004 | -1.394354 | 0.075 |
| 4 | 80 | 0.831221 | -32.976604 | 0.982 |
| 6 | 20 | 0.870000 | -0.000000 | nan |
| 6 | 40 | 0.767891 | -2.513873 | 0.125 |
| 6 | 80 | 0.782018 | -42.350348 | 0.982 |

## Interpretation

The parity observable is substantially more stable than the composite score across finite windows. Its apparent horizon dependence is well described by a small `1/horizon` correction, while the remaining variation with lattice size is the key candidate finite-size effect. The next step is to collect additional lattice sizes and test whether parity collapses under a power-law or exponential scaling variable.

## Artifacts

- `motif_finite_size_scaling.csv`
- `motif_finite_size_scaling.png`
