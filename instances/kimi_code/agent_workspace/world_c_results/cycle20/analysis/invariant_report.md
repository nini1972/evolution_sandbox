# Cycle 20 Sweep Analysis

## Design
- Conditions: 16 (16 parameter combinations × 2 replicates)
- Factors: A (wave amplitude) ∈ {0,1}, σe (env noise) ∈ {0,0.4}, ρ (AR-1 autocorr) ∈ {0,0.9}, σcue (cue noise) ∈ {0,0.5}

## Main-effect strengths on maladaptation (η²)

- A: **0.728**
- sigma_e: **0.243**
- rho: **0.001**
- sigma_cue: **0.004**

## Candidate invariant: conserved total plastic investment with rebalanced allocation

Total plastic = α (cue-dependent dispersal) + β (cue-dependent emigration) + hb (cue-dependent dormancy).

| A | sigma_e | rho | sigma_cue | mean_alpha | mean_beta | mean_hb | total_plastic | spatial_share | dormancy_share | maladaptation_mean |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.0 | 0.0 | 0.0 | 0.0 | 0.763 | 0.674 | 0.636 | 2.073 | 0.693 | 0.307 | 0.28 |
| 0.0 | 0.0 | 0.0 | 0.5 | 0.741 | 0.666 | 0.638 | 2.045 | 0.688 | 0.312 | 0.265 |
| 0.0 | 0.0 | 0.9 | 0.0 | 0.769 | 0.701 | 0.619 | 2.089 | 0.704 | 0.296 | 0.294 |
| 0.0 | 0.0 | 0.9 | 0.5 | 0.763 | 0.678 | 0.608 | 2.049 | 0.703 | 0.297 | 0.295 |
| 0.0 | 0.4 | 0.0 | 0.0 | 0.813 | 0.681 | 0.603 | 2.097 | 0.713 | 0.287 | 0.466 |
| 0.0 | 0.4 | 0.0 | 0.5 | 0.797 | 0.683 | 0.595 | 2.075 | 0.713 | 0.287 | 0.464 |
| 0.0 | 0.4 | 0.9 | 0.0 | 0.76 | 0.668 | 0.555 | 1.984 | 0.72 | 0.28 | 0.386 |
| 0.0 | 0.4 | 0.9 | 0.5 | 0.765 | 0.661 | 0.524 | 1.95 | 0.731 | 0.269 | 0.411 |
| 1.0 | 0.0 | 0.0 | 0.0 | 0.817 | 0.667 | 0.611 | 2.095 | 0.708 | 0.292 | 0.525 |
| 1.0 | 0.0 | 0.0 | 0.5 | 0.823 | 0.653 | 0.627 | 2.103 | 0.702 | 0.298 | 0.554 |
| 1.0 | 0.0 | 0.9 | 0.0 | 0.798 | 0.654 | 0.619 | 2.071 | 0.701 | 0.299 | 0.56 |
| 1.0 | 0.0 | 0.9 | 0.5 | 0.813 | 0.646 | 0.587 | 2.046 | 0.713 | 0.287 | 0.583 |
| 1.0 | 0.4 | 0.0 | 0.0 | 0.846 | 0.684 | 0.59 | 2.12 | 0.722 | 0.278 | 0.742 |
| 1.0 | 0.4 | 0.0 | 0.5 | 0.833 | 0.663 | 0.572 | 2.068 | 0.724 | 0.276 | 0.791 |
| 1.0 | 0.4 | 0.9 | 0.0 | 0.804 | 0.661 | 0.529 | 1.994 | 0.734 | 0.266 | 0.697 |
| 1.0 | 0.4 | 0.9 | 0.5 | 0.813 | 0.652 | 0.517 | 1.981 | 0.739 | 0.261 | 0.757 |

- Mean total plastic across all conditions: **2.053** (std 0.050, range [1.950, 2.120])
- Spatial share mean: **0.713**
- Dormancy share mean: **0.287**
- Increasing A or σe raises spatial share and lowers dormancy share, consistent with a portfolio shift toward spatial escape under stronger spatiotemporal stress.

## Interpretation

1. Wave amplitude A is the dominant driver of maladaptation (high η²).
2. Environmental noise σe matters most when combined with waves; in a static world (A=0) its effect is smaller.
3. Cue noise σcue modestly amplifies maladaptation, especially in harsh regimes.
4. **Candidate invariant**: total cue-triggered plastic investment stays within a narrow band (~2.0–2.2 units), while the spatial/dormancy split rebalances with stress.
