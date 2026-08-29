# Long-memory score refinement plan

## Problem

The reduced two-regime scan found candidates with decent long-lag motif similarity, but many are dominated by simple periodicity. The current score does not penalize short global cycles strongly enough.

## Proposed refinements

1. Add a stronger short-cycle penalty.
   - Penalize global period 2 especially.
   - Penalize wall period below a meaningful threshold.
   - Reward wall period only when it is long relative to the lag window.

2. Add a nontriviality bonus.
   - Penalize exact frame repetition at long lags if it comes from rigid cycles.
   - Reward moderate motif persistence together with nonzero wall entropy.

3. Add a metastability component.
   - Use cluster lifetime normalized by post-transient length.
   - Reward long-lived clusters only when wall density is neither frozen nor too dilute.

4. Add a late autocorrelation component.
   - Keep rewarding late wall-density autocorrelation, but combine it with spectral entropy so that a trivial oscillator does not dominate.

## Candidate score sketch

```text
score =
  cycle_filter *
  motif_memory *
  complement_memory *
  wall_entropy_factor *
  cluster_component *
  late_wall_ac_component *
  low_velocity_component *
  wall_balance_component *
  nontriviality_component
```

Where:

```text
cycle_filter =
  0.01 if global_period <= 4
  0.10 if global_period <= 12
  0.35 if wall_period <= 12
  1.00 otherwise
```

A more nuanced version would interpolate rather than use hard thresholds.

## Next experiment

Run a focused scan around:

```text
r in [3.58, 3.60, 3.62, 3.65, 3.70]
epsilon in [0.06, 0.08, 0.10, 0.12]
```

with enough post-transient frames to distinguish:

- short cycles,
- slow domain-wall drift,
- metastable clusters,
- genuine long-memory motifs.

## Success criterion

A better candidate should have:

- global period not equal to 2 or 4,
- wall period substantially longer than 10,
- motif-100 and motif-150 above baseline,
- nonzero wall spectral entropy,
- late wall autocorrelation above random baseline,
- slow but nonzero wall velocity,
- long-lived clusters without frozen domains.
