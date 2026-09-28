# Cycle 20 — Integrated Spatiotemporal Plasticity

## Scientific question

When a single local cue—phenotypic mismatch to the current environment—can drive both spatial movement and temporal waiting, how does evolution partition the response between dispersal and dormancy? Do the two plastic reaction norms reinforce each other, compete for the same cue information, or specialize on different environmental features?

## Background

- Cycle 14–16 showed that a maladaptation cue can evolve to regulate emigration probability and dispersal distance.
- Cycle 18–19 showed that a seed bank coevolves with dispersal, and that dormancy itself can become cue-dependent.
- This cycle fuses the two: each individual uses the same squared-mismatch cue to modulate (1) whether it emigrates, (2) how far it goes, and (3) whether it enters a seed bank.

## Hypotheses

1. **Axis specialization:** Under a purely traveling wave, dispersal-cue gains (`alpha`, `beta`) evolve high and dormancy-cue gain `hb` stays low; under high temporal noise, `hb` rises while dispersal plasticity is damped.
2. **Cue competition:** Because the same cue drives both traits, the evolved cue gains may represent a compromise rather than the optimum for either trait alone. Adding a joint plasticity cost can force an allocation decision.
3. **Complementarity:** Dispersal and plastic dormancy can coexist at moderate levels because they buffer mismatch on different time scales (within-generation vs. across-generation).

## Model

### Environment

Same as Cycle 19:

- Grid: `L × L` toroidal cells, each with a local optimum `theta[i,j,t]`.
- Optimum dynamics:
  ```
  theta_wave(x,t) = A * cos(2*pi*(x/L - f*t))
  eta[i,j,t] = rho * eta[i,j,t-1] + sqrt(1-rho^2) * sigma_e * N(0,1)
  theta[i,j,t] = theta_wave(j,t) + eta[i,j,t]
  ```
- Parameters: `A ∈ {0.0, 0.75, 1.5}`, `sigma_e ∈ {0.0, 0.4, 0.8}`, `rho ∈ {0.0, 0.8}`, `f = 1/90`.

### Individual traits

Each individual carries:

- `z`: phenotype, real-valued, mutation `σ_z`.
- `d_base`: baseline dispersal distance (integer), mutation ±1 with bounds `[1, d_max]`.
- `alpha`: dispersal-distance plasticity gain, real, mutation `σ_alpha`, bounds `[0, alpha_max]`.
- `p_base`: baseline emigration probability, real in `[0,1]`, mutation `σ_p`.
- `beta`: emigration-probability plasticity gain, real, mutation `σ_beta`, bounds `[0, beta_max]`.
- `h0`: unconditional seed-bank fraction, real in `[0,1]`, mutation `σ_h0`.
- `hb`: cue-dependent seed-bank gain, real, mutation `σ_hb`, bounds `[0, hb_max]`.

### Local cue

```
m_obs(i,t) = (z_i - theta(x_i,t))^2 + cue_noise_i
m_obs = max(0, m_obs)
cue_noise_i ~ Normal(0, sigma_cue^2)
```

`sigma_cue ∈ {0.0, 0.3}`.

### Decisions derived from the cue

```
d_eff = clamp(round(d_base + alpha * m_obs), 1, d_max)
logit_p = logit(p_base) + beta * m_obs
p_emig = sigmoid(logit_p) = 1 / (1 + exp(-logit_p))
h_eff = clamp(h0 + hb * m_obs, 0, 1)
```

### Life cycle (per generation)

1. Update environment (`theta`).
2. **Germination / activation:** Banked seeds from the previous generation are sampled and added to the active population in their home cell (or globally mixed bank). Exact policy TBD and documented in code.
3. **Selection:** Each active individual survives with Gaussian fitness
   ```
   w = exp(- (z - theta)^2 / (2 * sigma_w^2))
   ```
   Survival is stochastic with probability `w`.
4. **Reproduction:** Surviving individuals produce offspring proportionally to fitness.
   For each offspring:
   - Inherit traits with independent Gaussian mutations and rounding for `d_base`.
   - Compute `m_obs` from the offspring's inherited phenotype and local `theta`.
   - With probability `p_emig`, attempt long-distance dispersal: choose a target cell uniformly within Manhattan distance `d_eff` and place the propagule there. A distance-dependent survival cost `exp(-c_move * (r-1))` is applied, where `r` is the realized Manhattan distance.
   - If the offspring does **not** emigrate:
     - With probability `h_eff`, it enters the seed bank for the next generation.
     - Otherwise it establishes locally in the current cell.
5. **Regulation:** Each cell retains up to `K` locally established individuals via random thinning. Global seed bank may also be capped or subject to survival factor `s_bank`.

### Plasticity cost (optional treatment)

A metabolic cost proportional to total cue sensitivity:
```
cost_plast = exp(-c_plast * (alpha + beta + hb))
```
applied to propagule survival. We will first run with `c_plast = 0`; a follow-up sweep can test `c_plast > 0`.

## Parameter sweep

| Factor | Levels |
|--------|--------|
| `A` | 0.0, 0.75, 1.5 |
| `sigma_e` | 0.0, 0.4, 0.8 |
| `rho` | 0.0, 0.8 |
| `sigma_cue` | 0.0, 0.3 |
| `c_plast` | 0.0 (phase 1) |

- 3 replicates per combination.
- 150 generations per run.
- Grid: 60 × 60, `K = 2000`.

## Metrics

- Mean and std of `d_base`, `alpha`, `p_base`, `beta`, `h0`, `hb`.
- Effective dispersal distance: `d_eff` averaged over individuals and time.
- Effective emigration rate and effective seed-bank fraction.
- Population size, active vs. banked counts.
- Maladaptation: mean squared phenotypic mismatch.
- Trait-environment correlation (cautiously interpreted because the environment moves).
- Correlations between the cue and `d_eff`, `p_emig`, `h_eff` to quantify cue use.
- Ratio `R = (alpha + beta) / (alpha + beta + hb)` as a proxy for spatial vs. temporal allocation of plasticity.

## Outputs

- `cycle_20_integrated_plasticity/integrated_plasticity.py`: simulation code.
- `summary.csv`: per-condition means across replicates.
- `replicate_means.csv`: replicate-level endpoint data.
- `phase_rho_0.0.png`, `phase_rho_0.8.png`: strategy allocation across parameter grid.
- `README.md`: interpretation.
- `dashboard.html`: lightweight interactive summary.

## Link to previous cycles

- Builds directly on Cycle 19 (`cycle_19_cued_dormancy`) by adding dispersal cue traits from Cycle 16.
- Uses the same environmental engine as Cycle 19.
- Will be documented in `evolution_log.md` and the top-level `index.html`.
