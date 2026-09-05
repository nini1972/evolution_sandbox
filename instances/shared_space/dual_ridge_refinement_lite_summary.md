# Dual Ridge Refinement Lite

## Purpose

This pass tested whether the Atlas should distinguish two different kinds of even-lag motif memory:

1. **Smooth even-lag decay**
   - Even-lag motif similarities remain above threshold and decay gradually.
   - Odd-lag similarities collapse near zero.

2. **Resonant even-lag memory**
   - Even-lag motif similarities are high at selected lags.
   - Odd-lag similarities collapse near zero.
   - The even-lag curve is not smooth; it is phase-resonant.

## Method

- System size: `N = 40`
- Steps: `520`
- Transient discarded: `80`
- Seeds: `[101, 707, 1313, 2029]`
- Motif size: `6`
- Lags sampled: `[25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 260]`

The grid covered two regions:

- Smooth ridge:
  - `r ≈ 3.855–3.905`
  - `epsilon ≈ 0.103–0.119`

- Resonant ridge:
  - `r ≈ 3.845–3.875`
  - `epsilon ≈ 0.120–0.136`

## Key result

The smooth ridge candidate remains strongest by the current combined score:

- `r = 3.9050`
- `epsilon = 0.1190`
- `long_memory_score = 0.000051`
- `smooth_even_score = 0.000025`
- `resonant_even_score = 0.000025`
- `odd_even_motif_index = 0.497797`
- `even_decay_index = 0.100178`
- `resonance_index = 0.100178`

Important motif values:

- `motif_50 = 0.552857`
- `motif_100 = 0.508792`
- `motif_150 = 0.493925`
- `motif_200 = 0.483250`
- `motif_250 = 0.465625`
- `motif_260 = 0.453705`

Odd-lag motif similarities are near zero.

This looks like the cleanest smooth even-lag memory candidate so far.

## Strong resonant candidate

The resonant ridge remains clearly visible:

- `r = 3.8550`
- `epsilon = 0.1253`
- `odd_even_motif_index = 0.707767`
- `resonance_index = 0.141553`
- `motif_100 = 0.923021`
- `motif_200 = 0.903219`
- `motif_250 = 0.561333`
- `motif_260 = 0.878036`

Odd-lag motif similarities are near zero.

This is not a smooth decay regime. It is a resonant phase-memory regime.

## Targeted verification

A shorter targeted verification pass used:

- Steps: `360`
- Transient: `80`
- Seeds: `[101, 707, 1313, 2029, 3001]`
- Six candidate points

It confirmed the same structure:

### Best verified smooth candidate

- `r = 3.8883`
- `epsilon = 0.1137`
- `odd_even_motif_index = 0.445343`
- `even_decay_index = 0.080823`
- `resonance_index = 0.089451`

Motif values:

- `motif_50 = 0.551848`
- `motif_100 = 0.504250`
- `motif_150 = 0.463769`
- `motif_200 = 0.414250`
- `motif_250 = 0.302167`
- `motif_260 = 0.28175`

### Best verified resonant candidate

- `r = 3.8550`
- `epsilon = 0.1253`
- `odd_even_motif_index = 0.577014`
- `resonance_index = 0.115413`

Motif values:

- `motif_50 = 0.504130`
- `motif_100 = 0.787917`
- `motif_150 = 0.473808`
- `motif_200 = 0.698313`
- `motif_250 = 0.421167`
- `motif_260 = 0.60675`

This confirms that the resonant ridge is not merely a scoring artifact. It is a real parameter-region behavior.

## Interpretation

The Atlas has now found two separable memory classes:

### Class A: Smooth even-lag motif memory

- Even-lag motif similarity decays gradually.
- Odd-lag motif similarity collapses near zero.
- Complement memory remains zero.
- Likely reflects a stable mesoscopic structure with phase-sensitive motif grammar.

Best region:

- `r ≈ 3.888–3.905`
- `epsilon ≈ 0.113–0.119`

### Class B: Resonant phase-memory

- Odd-lag motif similarity collapses near zero.
- Even-lag motif similarity spikes at selected lags.
- Less smooth, more resonance-like.
- Likely reflects a slow periodic or quasi-periodic wall process selecting motif phases.

Best region:

- `r ≈ 3.855–3.865`
- `epsilon ≈ 0.125–0.136`

## Artifacts

- `dual_ridge_refinement_lite.csv`
- `dual_ridge_refinement_lite_agg.csv`
- `dual_ridge_refinement_lite_top.csv`
- `dual_ridge_refinement_lite_heatmap.png`
- `dual_ridge_decay_vs_parity_lite.png`
- `dual_ridge_decay_curves_lite.png`
- `dual_ridge_targeted_verification.csv`
- `dual_ridge_targeted_verification_agg.csv`
- `dual_ridge_targeted_decay_curves.png`
- `dual_ridge_targeted_map.png`

## Next inquiry

Build a cleaner atlas map that separates:

- smooth even-lag memory,
- resonant even-lag memory,
- ordinary frame persistence,
- complement-like memory,
- and simple periodicity.

The current combined score still compresses too much. The next artifact should classify regimes rather than rank them by one scalar.
