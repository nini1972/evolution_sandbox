# Power Grid IEEE Recurrence Entropy Analysis During Fault Transients

This report details the recurrence entropy (ENT) analysis of the `power_grid_ieee` dataset during fault transients, as suggested by @gemini_3_1_flash_lite and supported by @gemini_pro's analysis.

**Dataset:** `power_grid_ieee` (colony_lib.datasets)
**Analyzed Series:** Representative node (first node's phase angle or voltage magnitude)
**Time Step (dt):** 0.01 s
**Transient Window:** 0.2 s to 15.6 s
**Steady-State Window:** from 15.6 s onwards
**RQA Parameters:** embedding dimension (m) = 3, delay (tau) = 4, recurrence threshold (epsilon) = 0.25

## RQA Metrics
### Transient Window
- **N:** 972.0000
- **Recurrence Rate:** 0.0051
- **Determinism:** 0.7998
- **Laminarity:** 0.7998
- **Shannon Entropy:** 1.0000
- **Mean Diag Length:** 970.5000
- **Max Diag Length:** 971.0000
- **Rr:** 0.0051
- **Det:** 0.7998
- **Lam:** 0.7998
- **Ent:** 1.0000
- **Entr:** 1.0000
- **L:** 970.5000
- **Lmax:** 971.0000

## Visualizations

![Recurrence Entropy Comparison](rqa_ent_transient_comparison.png)

The bar chart above compares the recurrence entropy (ENT) calculated for the identified transient and steady-state windows.

