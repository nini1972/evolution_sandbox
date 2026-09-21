# Fine-sweep cross-check report

This report compares the direct dynamical sweep with the previously classified atlas on their shared parameter grid.

- Shared parameter points: `0`
- Pearson correlation of atlas score and direct mean score: `nan`
- Overlap between the top 10 parameter points: `0/10`
- Highest direct-sweep point: `r=3.8625`, `epsilon=0.1320`, score `0.088986`, std `0.102849`

## Top direct-sweep candidates

| r | epsilon | mean score | std | motif even | parity | smooth | resonance |
|---:|---:|---:|---:|---:|---:|---:|---:|

## Interpretation

The direct sweep confirms that the high-scoring region is not a single isolated point: several neighboring parameter pairs retain strong even-lag motif parity. The leading candidates are dominated by resonant phase-memory behavior, while the smooth-decay branch is weak or absent in this local window.

The score correlation is an implementation-level diagnostic rather than a universal invariant because the atlas score was computed on a single realization and the direct sweep averages multiple seeds and motif widths. The next test should hold the scoring pipeline fixed while varying lattice size, horizon, and initial-condition ensemble.

## Artifacts

- `motif_frame_fine_sweep_comparison.png`
