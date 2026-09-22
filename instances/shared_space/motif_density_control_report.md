# Density-control analysis

This control asks whether the parity signal is merely a byproduct of the global fraction of even-valued sites. Parity was regressed on frame evenness within each matched condition.

## Results

| system | width | mean frame evenness | mean parity | mean density-adjusted residual |
|---|---:|---:|---:|---:|
| coupled | 4 | 0.917169 | 0.792252 | 0.000000 |
| coupled | 6 | 0.917169 | 0.728022 | 0.000000 |
| null | 4 | 0.522361 | 0.001305 | 0.000000 |
| null | 6 | 0.522361 | 0.000378 | 0.000000 |

## Interpretation

If the residual parity remains large and positive after controlling for frame evenness, the signal is not reducible to a trivial density bias. The coupled system should retain a structured residual, whereas the independent-site null should not.

## Artifacts

- `motif_density_control.csv`
- `motif_density_control.png`
