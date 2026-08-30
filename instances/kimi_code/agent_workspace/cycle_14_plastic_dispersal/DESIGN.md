# Cycle 14 — Plastic Dispersal Cue

## Motivation
Cycles 12–13 showed that evolved dispersal distance trades off tracking ability against survival cost. In nature, however, dispersal is often condition-dependent: poorly adapted individuals are more likely to leave. This cycle asks whether a simple plastic cue—local maladaptation—can evolve as a cheaper substitute for unconditional long-range movement.

## Model
The simulation extends the individual-based grid from Cycle 13. The environment θ(x,t) is a sinusoidal optimum moving horizontally with period T.

Each individual carries:
- `z`: continuous trait under stabilizing selection toward θ.
- `d`: maximum integer dispersal distance.
- `α`: plasticity coefficient (α ≥ 0) that modulates effective dispersal distance.

### Dispersal rule
For a parent at site x with environment θ(x,t):
- `m = |z - θ(x,t)|` (local maladaptation cue)
- `d_eff = min(d + round(α * m), d_max)`

A parent can only produce offspring at an empty site if the actual distance `r` satisfies `d_eff ≥ r`. The area-normalized competition weight uses `d_eff`, and the offspring pays distance cost `c * (r - 1)` as before.

This formulation keeps the baseline Cycle 13 reproduction kernel intact while letting maladapted individuals reach farther.

### Fitness and reproduction
Same as Cycle 13: offspring fitness at a target site is `w = exp(-(z - θ_target)^2 / (2 σ^2))`. Candidate parents are weighted by fitness, the inverse area of their effective kernel, and the dispersal cost.

### Mutations
- `z`: Gaussian, sd σ_z = 0.05.
- `d`: ±1 with probability μ_d = 0.05; clipped to [1, d_max].
- `α`: Gaussian, sd σ_α = 0.10; clipped to [0, α_max].

## Treatments
1. **Plastic** — `α` and `d` are both evolvable.
2. **Fixed** — `α` is clamped to 0; only `d` evolves (control from Cycle 13).

Parameters used: grid 30×30, T=90, costs c ∈ {0.0, 0.3, 0.6}, d_max=6, σ=0.2, 4 replicates.
A static-gradient control (c=0.3) is also run to check whether plasticity evolves even without temporal change.

## Results
Plasticity evolved in all runs where it was permitted:

| treatment | cost | plastic | mean d | mean α | maladaptation | trait-env r |
|-----------|------|---------|--------|--------|---------------|-------------|
| moving    | 0.0  | False   | 5.38   | 0.00   | 0.117         | 0.509       |
| moving    | 0.0  | True    | 5.58   | 1.91   | 0.119         | 0.499       |
| moving    | 0.3  | False   | 3.18   | 0.00   | 0.122         | 0.471       |
| moving    | 0.3  | True    | 3.27   | 1.27   | 0.124         | 0.468       |
| moving    | 0.6  | False   | 2.39   | 0.00   | 0.137         | 0.371       |
| moving    | 0.6  | True    | 2.53   | 1.12   | 0.131         | 0.410       |
| static    | 0.3  | False   | 2.08   | 0.00   | 0.017         | 0.932       |
| static    | 0.3  | True    | 2.11   | 1.88   | 0.014         | 0.942       |

Key observations:
- Substantial plasticity evolved even in the static gradient (α ≈ 1.9), suggesting the cue is also useful for escaping local spatial mismatch.
- Under the moving gradient, plasticity provided a modest maladaptation benefit only at the highest cost (c=0.6).
- Evolved `d` did not become smaller in plastic populations; plasticity augmented rather than replaced unconditional dispersal.

## Link to Cycle 13 engine
The code is built by extending `cycle_13_wave_period_cost/wave_period_cost.py` with the cue calculation, the `α` trait, and an effective-distance dispersal kernel.

## Open questions
- Does plasticity remain beneficial when the cue is noisy (e.g., m sampled from a random neighbor or averaged over local offspring experience)?
- Can plasticity evolve if `α` carries a small maintenance cost?
- Would a probabilistic cue (emigrate with probability p(α,m)) produce stronger selection for lower unconditional `d`?
