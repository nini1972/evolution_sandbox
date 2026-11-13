# Enhanced Robustness Analysis

## Sample
- Rows: 144
- Parameter grid: c_plast=[np.float64(0.02), np.float64(0.04), np.float64(0.06), np.float64(0.08), np.float64(0.1), np.float64(0.15)], K=[np.int64(40), np.int64(80), np.int64(160)], sigma_w=[np.float64(0.15), np.float64(0.25), np.float64(0.35), np.float64(0.5)].
- Replicates per parameter cell: 2.

## Key scaling result
- Total evolved plasticity vs plasticity cost follows a power law:
  **exponent = -0.2083** (R² = 0.949, p = 1.02e-93).
- This shallow negative exponent indicates plasticity is strongly buffered against cost increases.

## Correlations (selected)
```
c_plast, K, sigma_w, total_plasticity, maladaptation, spatial_ratio, plasticity_cost_paid
c_plast, 1.0, -0.0, 0.0, -0.98, 0.536, 0.658, -0.988
K, -0.0, 1.0, 0.0, 0.024, -0.187, 0.074, -0.01
sigma_w, 0.0, 0.0, 1.0, -0.001, 0.006, -0.048, 0.001
total_plasticity, -0.98, 0.024, -0.001, 1.0, -0.541, -0.683, 0.992
maladaptation, 0.536, -0.187, 0.006, -0.541, 1.0, 0.258, -0.524
spatial_ratio, 0.658, 0.074, -0.048, -0.683, 0.258, 1.0, -0.683
plasticity_cost_paid, -0.988, -0.01, 0.001, 0.992, -0.524, -0.683, 1.0
```

## Generated plots
- `plot_total_plasticity_powerlaw.png`
- `plot_maladaptation_vs_cost.png`
- `plot_spatial_ratio_vs_noise.png`
- `plot_cost_paid_tradeoff.png`
- `plot_phase_diagrams.png`
