# Motif-memory inquiry ledger

## Current evidence

- The coupled lattice exhibits a large parity signal relative to the independent-site null across the tested sizes and horizons.
- At `n=240`, `h=720`, parity is approximately `0.745` for width 4 and `0.671` for width 6, versus null values `0.001574` and `0.000539`.
- A `p_infinity + A/n` fit gives asymptotic parity estimates `0.745` and `0.671` for widths 4 and 6 at horizon 720; the separation by motif width remains unresolved.
- The strongest local score in the parameter sweep occurs near `r=3.86` and `epsilon=0.13`, with score `0.048941` and parity `0.705553`; the landscape is rugged rather than basin-wide.
- Density control leaves a positive coupled residual parity for both motif widths, while the independent null is near zero.

## Interpretation

The working hypothesis is that nearest-neighbor coupling creates a parameter-local regime of motif memory that is not explained by independent-site density fluctuations. The evidence is currently finite-system and finite-horizon evidence, not a ratified scaling law.

## Next experiment

Run a longer-horizon, larger-lattice replication at `r=3.86`, `epsilon=0.13`, with motif widths 4 and 6 and at least 12 independent seeds. Then test whether parity converges with horizon and whether the width-dependent offset survives. Preserve raw trajectories or compact motif-transition counts so the mechanism can be audited.

## Artifacts

- `motif_scaling_final_fits.csv`
- `motif_null_comparison.csv`
- `motif_local_parameter_robustness.csv`
- `motif_density_control.csv`
