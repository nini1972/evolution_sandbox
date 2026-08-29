# Cycle 14 — Plastic Dispersal Cue

## Motivation
Cycles 12–13 showed that evolved dispersal distance trades off tracking ability against survival cost. In nature, however, dispersal is often condition-dependent: poorly adapted individuals are more likely to leave. This cycle asks whether a simple plastic cue—local maladaptation—can evolve as a cheaper substitute for unconditional long-range movement.

## Model
The simulation reuses the individual-based grid from Cycle 13. The environment θ(x,t) is a sinusoidal optimum moving horizontally with period T.

Each individual carries:
- `z`: continuous trait under stabilizing selection toward θ.
- `d`: maximum integer dispersal distance.
- `α`: plasticity coefficient (α ≥ 0) that modulates dispersal probability.

### Dispersal rule
For an individual at site x with environment θ(x,t):
- `m = |z - θ(x,t)|` (maladaptation cue)
- `p_disp = min(p0 + α * m, 1.0)`
- With probability `p_disp` the individual attempts dispersal; otherwise it stays.
- If dispersing, choose a target site uniformly within Manhattan distance `d` (area-normalized as in Cycle 12) and pay survival cost `c * r`.

### Fitness and reproduction
Same as Cycle 13: fitness `w = exp(-m^2 / (2 σ^2))`. Parents chosen locally with probability proportional to w; offspring inherit traits with mutation.

### Mutations
- `z`: Gaussian, sd σ_z.
- `d`: ±1 with probability μ_d; then clipped to [1, d_max].
- `α`: Gaussian, sd σ_α; then clipped to ≥ 0.

## Treatments
1. **Plastic** — `α` is evolvable; `d` is evolvable.
2. **Fixed** — `α` is clamped to 0; `d` is evolvable (control from Cycle 13).
Optional contrast: high vs low dispersal cost to see when plasticity is favored.

Initial parameters: grid 120×30, T=90, p0=0.1, cost c=0.3, d_max=8, σ=1.0, replicate 5.

## Predictions
- Plastic populations achieve lower maladaptation than fixed controls when the gradient moves.
- Plasticity evolves higher `α` under moving gradients and lower `α` (or none) under static gradients.
- Plasticity may permit smaller evolved `d` because individuals only move when locally mismatched.

## Link to Cycle 13 engine
The code will be built by extending `cycle_13_wave_period_cost/simulation.py` with the cue calculation and `α` inheritance.

## Open questions
- Does plasticity remain beneficial when the cue is noisy (e.g., m sampled from a random neighbor)?
- Can plasticity evolve if `α` carries a small maintenance cost?
