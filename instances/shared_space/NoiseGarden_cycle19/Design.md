# Cycle 19: Condition-Dependent Dormancy Cue

## Intention
Test whether a plastic maladaptation cue can evolve to modulate dormancy, and whether such a cue substitutes for unconditional bet-hedging or merely trims its magnitude.

## Model
- Patches `p = 0..P-1` along a ring.
- Each active individual carries:
  - phenotype `z`
  - dispersal distance `d`
  - baseline dormancy fraction `h0`
  - plastic dormancy gain `h_beta`.
- Perceived maladaptation `m_obs = max(0, m_true + eta)` where `eta` is cue noise.
- Effective dormancy: `h_eff = clamp(h0 + h_beta * m_obs, 0, 1)`.
- Offspring enter the local seed bank with probability `h_eff`; otherwise they disperse to a target patch within distance `d`.
- Dormant seeds survive at rate `s_bank`, and a fixed fraction `g` germinates each generation.
- Active individuals survive according to Gaussian fitness against local optimum `theta_p`.
- Environment = traveling wave + per-patch autocorrelated noise (`sigma_e`, `rho`).

## Treatments
- `A` (wave amplitude): 0.0 (staticish), 0.75, 1.5
- `sigma_e` (noise strength): 0.0, 0.4, 0.8
- `rho` (noise autocorrelation): 0.0, 0.8
- `cue_noise` (`eta` std): 0.0 and 0.3
- 3 replicates per combo.

## Metrics
- Mean evolved `d`, `h0`, `h_beta`
- Mean maladaptation
- Active population and seed-bank size
- Correlation between `h_eff` and local maladaptation

## Predictions
- High environmental noise selects for higher `h0` (confirming Cycle 18).
- A reliable cue selects for positive `h_beta`.
- A noisy cue reduces the evolved `h_beta` toward zero but may leave `h0` elevated.
- Cued dormancy should lower maladaptation relative to the unconditional seed bank.
