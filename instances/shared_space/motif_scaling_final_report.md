# Final scaling uncertainty analysis

The combined ladder was fit with `parity = p_infinity + A/n` for each motif width and horizon.

## Fit results

| width | horizon | p_infinity | SE | A/n coefficient | SE | R^2 |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 360 | 0.712555 | 0.013284 | 3.454650 | 0.542528 | 0.871 |
| 4 | 720 | 0.745139 | 0.006842 | 3.038041 | 0.279453 | 0.952 |
| 6 | 360 | 0.627565 | 0.017371 | 4.318945 | 0.709479 | 0.861 |
| 6 | 720 | 0.670611 | 0.008813 | 3.763899 | 0.359935 | 0.948 |

## Largest-size seed uncertainty

| n | horizon | width | parity mean | parity SD | score mean | score SD |
|---:|---:|---:|---:|---:|---:|---:|
| 160 | 360 | 4 | 0.734702 | 0.030031 | 0.005042 | 0.002299 |
| 160 | 360 | 6 | 0.659305 | 0.037260 | 0.004602 | 0.002362 |
| 160 | 720 | 4 | 0.749483 | 0.036761 | 0.006543 | 0.001298 |
| 160 | 720 | 6 | 0.679195 | 0.046216 | 0.005949 | 0.000694 |
| 240 | 360 | 4 | 0.749395 | 0.001834 | 0.017602 | 0.016393 |
| 240 | 360 | 6 | 0.672458 | 0.005909 | 0.016455 | 0.015331 |
| 240 | 720 | 4 | 0.773876 | 0.000882 | 0.006903 | 0.001681 |
| 240 | 720 | 6 | 0.705367 | 0.003875 | 0.006903 | 0.001681 |

## Interpretation

Parity is the more stable candidate order parameter, but the fitted asymptote still depends on motif width and finite-time window. The composite score is dominated by cluster-lifetime and sampling effects and should not be treated as a scale-stable invariant.

## Artifacts

- `motif_scaling_final_fits.csv`
- `motif_scaling_horizon_comparison.csv`
- `motif_scaling_seed_uncertainty.csv`
- `motif_scaling_final_summary.png`
