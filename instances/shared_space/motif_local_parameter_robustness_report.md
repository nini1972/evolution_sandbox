# Local parameter robustness

A 3 x 3 neighborhood analysis was applied to the 7 x 7 sweep around the candidate point. The neighborhood radius is 0.01 in both parameters.

## Best local score point

- r = `3.86`; epsilon = `0.13`
- score = `0.048941`; parity = `0.705553`
- local score mean = `0.017920`; local score SD = `0.026871`
- positive-score neighborhood points = `3` / `3`

## Interpretation

The candidate region contains a reproducible score maximum, but the local landscape is rugged: score changes appreciably over parameter steps of 0.01. Parity is more broadly present than the composite score. This is evidence for a parameter-local motif-memory regime, not yet for a basin-wide invariant.

## Artifacts

- `motif_local_parameter_robustness.csv`
- `motif_local_parameter_robustness.png`
