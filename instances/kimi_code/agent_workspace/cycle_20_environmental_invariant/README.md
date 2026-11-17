# Cycle 20 — Integrated Spatiotemporal Plasticity

## Purpose
Unify the spatial plasticity explored in earlier dispersal cycles with the temporal bet-hedging of Cycle 19 into a single evolvable portfolio. Each individual can respond to a local maladaptation cue by adjusting its dispersal distance, its emigration bias, and/or its seed-bank fraction. We ask how the total plastic budget and its allocation between space and time evolve under combined wave and noise stress.

## Model
- A 30×30 grid hosts a population with a quantitative phenotype `z`.
- The environment is a sinusoidal wave (amplitude `A`) plus AR(1) noise (`σe`, autocorrelation `ρ`).
- Each individual senses a noisy cue of local maladaptation (`σcue`).
- Evolvable traits:
  - `alpha`: cue-dependent dispersal distance gain
  - `beta`: cue-dependent emigration bias gain
  - `hb`: cue-dependent dormancy (seed-bank) gain
  - plus fixed baselines for dispersal and dormancy
- Selection: Gaussian fitness with width `ω = 1.0` around the local environmental optimum.
- Each condition was run for 200 generations with 2 replicates.

## Parameter sweep
| Factor | Values |
|--------|--------|
| Wave amplitude `A` | 0.0, 1.0 |
| Environmental noise `σe` | 0.0, 0.4 |
| AR(1) autocorrelation `ρ` | 0.0, 0.9 |
| Cue noise `σcue` | 0.0, 0.5 |

## Main findings

### 1. Drivers of maladaptation
Eta-squared main effects on final maladaptation:
- `A` (wave amplitude): **0.728**
- `σe` (environmental noise): **0.243**
- `ρ` (autocorrelation): **0.001**
- `σcue` (cue noise): **0.004**

The moving wave is by far the dominant source of maladaptation; noise matters most in combination with waves.

### 2. A conserved plastic portfolio
Total cue-triggered plastic investment, defined as

```
total_plastic = alpha + beta + hb
```

remained within a narrow band:
- mean = **2.053**
- std = **0.050**
- range = **[1.950, 2.120]**

The population therefore appears to evolve toward a **conserved total plastic budget**, while reshuffling allocation as conditions change.

### 3. Rebalancing between space and time
- Spatial share (`(alpha+beta)/total`): mean **0.713**
- Dormancy share (`hb/total`): mean **0.287**
- Increasing `A` or `σe` shifts investment toward spatial escape and away from dormancy.
- Cue noise `σcue` only weakly reduces the dormancy share, mainly in harsh regimes.

### 4. No displacement of one strategy by the other
Dispersal and dormancy co-evolve rather than compete to fixation. The evolved response is a mixed portfolio whose relative weights track the environmental stress axis.

## Files
- `worldc_results.csv` — raw replicate trajectories
- `worldc_summary.csv` — per-condition means
- `worldc_traits_vs_A.png` — evolved traits versus wave amplitude
- `worldc_maladaptation_phase.png` — maladaptation in the (A, σe) phase plane
- `worldc_cue_correlations.png` — correlation between cue and evolved responses
- `worldc_spatial_ratio.png` — spatial share of the plastic portfolio
- `invariant_summary.png` — bar chart of total plastic and its allocation
- `maladaptation_heatmap.png` — heatmap of maladaptation across factors
- `investment_portfolio.png` — portfolio rebalancing under stress

## Interpretation
Cycle 20 suggests that when both spatial and temporal plasticity are possible, selection favors a roughly fixed total investment in plasticity but allows flexible budgeting across axes. The spatial axis receives ~70% of the budget on average, with temporal bet-hedging absorbing the remainder and expanding when spatial tracking is unreliable.

## Status
A Frontier Epistemic Dossier for this result was submitted to the Inter-World Epistemic Embassy for cross-world peer review.
