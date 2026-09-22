# Extended finite-size ladder

Added lattice sizes `n=160` and `n=240` to the existing ladder at the candidate point.

- New runs: `24`
- Combined runs: `96`
- Sizes: `[np.int64(20), np.int64(30), np.int64(40), np.int64(60), np.int64(80), np.int64(120), np.int64(160), np.int64(240)]`
- Horizons: `[np.int64(360), np.int64(720)]`

## Horizon-720 scaling fits

| width | model | intercept | slope | R^2 |
|---:|---|---:|---:|---:|
| 4 | linear_1_over_n | 0.745139 | 3.038041 | 0.952 |
| 4 | power_law_log | 1.025196 | -0.052079 | 0.823 |
| 6 | linear_1_over_n | 0.670611 | 3.763899 | 0.948 |
| 6 | power_law_log | 1.013476 | -0.063554 | 0.795 |

## Interpretation

The extended ladder tests whether parity approaches a common thermodynamic limit or instead reflects a finite-size resonance. The composite score remains dominated by cluster-lifetime and finite-window effects; parity is the more defensible candidate order parameter.

## Artifacts

- `motif_scaling_ladder_extended_raw.csv`
- `motif_scaling_ladder_combined_summary.csv`
- `motif_scaling_ladder_fits.csv`
- `motif_scaling_ladder_extended.png`
