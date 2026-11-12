# Robustness Sweep — Integrated Spatiotemporal Plasticity
- Simulations completed: 144 in 0.2 minutes
- Parameter grid: c_plast=[0.02, 0.04, 0.06, 0.08, 0.1, 0.15], K=[40, 80, 160], sigma_w=[0.15, 0.25, 0.35, 0.5]
- Fixed background: A=0.75, sigma_e=0.4, temporal rho=0.0, sigma_cue=0, default sigma_w=0.35
- Power-law fit total_plasticity = 1.080 * c_plast^(-0.197)  (success=True)
- Mean maladaptation: 0.2352 ± 0.0052
- Mean final population: 23893.3 ± 12816.1

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
