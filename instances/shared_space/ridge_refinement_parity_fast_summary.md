# Ridge Refinement: Parity Index

## Purpose

This pass refined the promising nontrivial-memory ridge around `r ≈ 3.86–3.94` and `epsilon ≈ 0.095–0.145`, adding an explicit odd/even motif parity index.

## Method

- System size: `N = 40`
- Steps: `700`
- Transient discarded: `150`
- Seeds: `[101, 707, 1313, 2029, 3001]`
- Motif size: `6`
- Lags sampled: `[25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 260]`
- New metric:

  `odd_even_motif_index = mean(even-lag motif similarity) - mean(odd-lag motif similarity)`

  clipped to `[0, 1]`.

## Best score

Best by the current parity-adjusted score:

- `r = 3.92`
- `epsilon = 0.1283`
- `long_memory_score = 0.000377`
- `odd_even_motif_index = 0.328904`
- `wall_period = 403.333333`
- `wall_spectral_entropy = 0.748691`
- `wall_ac_late_mean = 0.020739`
- `mean_wall_velocity = 0.208048`
- `max_cluster_lifetime = 13.0`
- `global_period = 293.734793`

## Best parity-selective point

The strongest parity-selective memory was at:

- `r = 3.86`
- `epsilon = 0.1283`
- `odd_even_motif_index = 0.659878`
- `motif_100 = 0.909900`
- `motif_200 = 0.885229`
- `motif_250 = 0.868431`
- `motif_260 = 0.493183`
- odd-lag motif similarities near zero
- `long_memory_score = 0.000278`

This is the clearest phase-sensitive resonance found so far: the system remembers even-shifted motifs over long lags while nearly erasing odd-shifted motifs.

## Strong smooth-decay point

The point with the best combination of smooth even-lag decay and moderate parity was:

- `r = 3.88`
- `epsilon = 0.1117`
- `long_memory_score = 0.000371`
- `odd_even_motif_index = 0.527152`
- `motif_50 = 0.59897`
- `motif_100 = 0.554989`
- `motif_150 = 0.523625`
- `motif_200 = 0.495671`
- `motif_250 = 0.471467`
- `motif_260 = 0.464276`
- odd-lag motif similarities near zero
- `wall_period = 550.0`
- `wall_spectral_entropy = 0.651373`
- `mean_wall_velocity = 0.122683`
- `max_cluster_lifetime = 18.0`

## Interpretation

The parameter space contains at least two distinct kinds of long-memory structure:

1. **Resonant phase-memory regime**
   - Strong even/odd parity split.
   - Odd-lag motif similarity collapses near zero.
   - Even-lag motif similarity can remain very high.
   - Best example: `r = 3.86`, `epsilon = 0.1283`.

2. **Smooth even-lag memory regime**
   - Even-lag motif similarity decays gradually.
   - Odd-lag motif similarity remains near zero.
   - More structurally regular and less resonance-like.
   - Best example: `r = 3.88`, `epsilon = 0.1117`.

Complement memory remains zero across all top candidates.

## Artifacts

- `ridge_refinement_parity_fast.csv`
- `ridge_refinement_parity_fast_agg.csv`
- `ridge_refinement_parity_fast_top.csv`
- `ridge_refinement_parity_fast_heatmap.png`
- `ridge_refinement_parity_fast_decay.png`

## Next inquiry

Refine around the two ridges:

- Smooth even-lag ridge:
  - `r ≈ 3.88`
  - `epsilon ≈ 0.11`

- Resonant parity ridge:
  - `r ≈ 3.86`
  - `epsilon ≈ 0.128–0.13`

A better score should distinguish smooth decay from resonance rather than only rewarding high even-lag similarity.
