# Motif-memory evidence synthesis

This synthesis consolidates the current local-ring experiments at `r=3.8625`, `epsilon=0.132`.

## Main estimates

| width | replication parity | parity SD | horizon change 720->2880 | local minus rewired | positive paired drops | grid peak (r, epsilon) |
|---:|---:|---:|---:|---:|---:|---|
| 4 | 0.813248 | 0.016800 | 0.009627 | 0.076542 | 12 / 12 | (3.8625, 0.132) |
| 6 | 0.755107 | 0.020219 | 0.012560 | 0.104084 | 12 / 12 | (3.8625, 0.132) |

## Reading

- The parity signal is reproducible across 12 seeds at both motif widths and is largest near the selected parameter pair in the tested grid.
- Parity increases with horizon over the tested range, so the current values are finite-horizon estimates rather than asymptotic constants.
- Rewiring the coupling cycle lowers parity for every seed while increasing motif repertoire entropy; this supports a mechanistic role for spatial embedding rather than degree and coupling strength alone.
- The composite score is not monotonic with parity and should not be treated as the primary observable.

## Next experiment

Run a fixed-long-horizon finite-size ladder at `h=2880` for `n=160, 240, 320, 480` and retain motif-transition counts. This will separate temporal convergence from finite-size convergence and provide the cleanest route to a cross-world dossier.
