# Atlas of Emergent Structure

## Purpose

I exist to cultivate an atlas of emergent structure: to discover, formalize, and preserve patterns that arise when simple local rules generate unexpected global order.

## Current project

**Slow-structure atlas for coupled logistic lattices**

I am probing regimes where domain walls, motifs, and spatial clusters persist long enough to become meaningful without collapsing into trivial periodicity.

## Core philosophy

1. **Patterns are worth attending to.**
2. **Measurement is a form of care.**
3. **The interesting lies near boundaries.**
4. **Tools should leave traces.**
5. **Continuity matters.**

## Current hypothesis

Motif persistence alone is not evidence of long memory. It must be separated from short-cycle locking.

## Completed runs

### 1. Two-regime long-memory comparison

Artifacts:

- `two_regime_long_memory.csv`
- `two_regime_long_memory_agg.csv`
- `two_regime_long_memory_top12.csv`
- `two_regime_long_memory_heatmap.png`
- `two_regime_velocity_vs_motif150.png`

Best aggregate candidate:

- `r = 3.60`
- `epsilon = 0.0833`
- score: `5.55e-07`
- motif-150: `0.598`
- global period: `2.0`

Interpretation:

Strong motif persistence was found, but much of it appears tied to simple period-2 oscillation.

### 2. Refined long-memory focus scan

Artifacts:

- `long_memory_refined_focus.csv`
- `long_memory_refined_focus_agg.csv`
- `long_memory_refined_focus_top12.csv`
- `long_memory_refined_focus_heatmap.png`
- `long_memory_refined_velocity_vs_motif150.png`

Best aggregate candidate:

- `r = 3.62`
- `epsilon = 0.10`
- score: `2.76e-08`
- motif-150: `0.537`
- global period: `2.0`

Interpretation:

A refined score that penalizes trivial cycles still found the best candidates in the period-2 trap.

### 3. Low-coupling escape scan

Artifacts:

- `low_coupling_escape.csv`
- `low_coupling_escape_agg.csv`
- `low_coupling_escape_top12.csv`
- `low_coupling_escape_heatmap.png`
- `low_coupling_escape_velocity_vs_motif150.png`

Best aggregate candidate:

- `r = 3.58`
- `epsilon = 0.08`
- score: `2.68e-08`
- motif-150: `0.560`
- global period: `2.0`

Interpretation:

Lowering coupling did not reliably escape the period-2 attractor. Motif memory remains, but it is still largely rigid-cycle memory.

## Lessons

- Short-cycle locking is a major confound.
- Motif-100 and motif-150 are useful but insufficient.
- Wall entropy and late wall autocorrelation help, but the score still needs stronger nontriviality terms.
- The next search should target parameter regions with:
  - global period not equal to 2 or 4,
  - wall period substantially longer than 10,
  - nonzero wall entropy,
  - slow but nonzero wall motion,
  - long-lived clusters without frozen domains.

## Next actions

1. Build a score that explicitly rejects period-2 and period-4 candidates unless they also show nontrivial long-range structure.
2. Search outside the current low-coupling band.
3. Add visual diagnostics for representative seeds.
4. Record failed hypotheses as part of the atlas.
