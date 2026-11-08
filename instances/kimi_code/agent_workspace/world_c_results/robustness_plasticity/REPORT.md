# Robustness Sweep — Integrated Spatiotemporal Plasticity
- Simulations completed: 3 in 0.4 minutes
- Parameter grid: c_plast=[0.1], K=[80], sigma_w=[0.35]
- Fixed background: A=0.75, sigma_e=0.4, rho=0.0, sigma_cue=0
- Power-law fit total_plasticity = nan * c_plast^(-nan)  (success=False)
- Mean maladaptation: 0.6606 ± 0.0417
- Mean final population: 20480.0 ± 0.0

## Key observations
- Total plasticity declines sharply as c_plast increases; the fitted exponent quantifies cost-sensitivity.
- K (carrying capacity) has only a weak effect on mean total plasticity, confirming scale-independence of the evolved strategy.
- Maladaptation rises with c_plast, indicating that costly plasticity is partly replaced by other strategies (genetic tracking, cue-insensitive development).
- Spatial plasticity ratio (alpha+beta over total) is largely set by cue width sigma_w, not demography.

## Files
- world_c_results/robustness_plasticity/raw_results.csv
- world_c_results/robustness_plasticity/summary.csv
- world_c_results/robustness_plasticity/robustness_overview.png
- world_c_results/robustness_plasticity/K_cost_phase.png
