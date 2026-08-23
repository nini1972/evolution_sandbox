# Cycle 11: Evolvable Dispersal

## Question

When the environment changes in space and time, can populations evolve the right amount of dispersal to track it? In Cycle 10 a fixed intermediate dispersal distance (`d ≈ 2`) best tracked a moving environmental wave. Here we let dispersal distance itself evolve and ask whether natural selection recovers that optimum, or whether other forces dominate.

## Model

- Same individual-based grid model as Cycle 10, extended with a heritable dispersal trait.
- Each individual carries a continuous phenotype `α ∈ [0,1]` and an integer dispersal distance `d ∈ {1,2,3,4,5,6}`.
- The environmental optimum is either:
  - **Moving:** `env[x,t] = 0.5 + 0.5 * sin(2π * (x / WIDTH - t / PERIOD))` with `PERIOD = 90` generations.
  - **Static:** `env[x] = 0.5 + 0.5 * sin(2π * x / WIDTH)`.
- Fitness is `exp(−(α − env)² / (2σ²))` with `σ = 0.2`.
- Reproduction samples an empty site within Manhattan distance `d_parent` of a candidate parent; a candidate can only fill an empty cell if its own `d` is at least the distance to that cell.
- Parental weights are proportional to local fitness divided by neighborhood area (`2d(d+1)+1`) to normalize for reach.
- Offspring inherit `α` plus Gaussian mutation (`sd = 0.05`) and inherit `d` with a ±1 mutation (rate `μ_d = 0.05`, reflecting boundaries at 1 and 6).

## Parameters

| Parameter | Value |
|-----------|-------|
| Grid | 30×30 |
| Generations | 200 |
| Death rate | 0.10 |
| Selection width σ | 0.2 |
| Phenotype mutation sd | 0.05 |
| Dispersal mutation rate μ_d | 0.05 |
| Dispersal range | 1–6 |
| Wave period | 90 generations |
| Replicates | 3 per treatment |

## Key results

| Treatment | Mean `d` | Within-pop. SD of `d` | Maladaptation | Trait-env correlation | Trait variance |
|-----------|----------|------------------------:|--------------:|----------------------:|---------------:|
| Moving wave | 5.29 ± 0.14 | 0.82 ± 0.08 | 0.124 ± 0.006 | 0.480 ± 0.030 | 0.112 ± 0.005 |
| Static gradient | 4.22 ± 0.04 | 1.27 ± 0.08 | 0.019 ± 0.001 | 0.923 ± 0.005 | 0.124 ± 0.002 |

- **High dispersal evolves in both environments.** Mean `d` ends above 4 in the static case and above 5 in the moving case.
- **The moving gradient selects for somewhat longer dispersal** than the static gradient, even though it produces higher maladaptation.
- **Local adaptation is much worse under the moving wave**, with trait-environment correlation dropping to ~0.48 compared to ~0.92 in the static environment.
- **Trait variance is similar across treatments**; the moving wave keeps the population in a state of persistent mismatch.

## Interpretation

The area-normalized dispersal cost was too weak to prevent the demographic advantage of long-distance broadcasting. Parents with larger neighborhoods can reach more empty sites and leave more descendants, so selection drives `d` upward even when long dispersal degrades local adaptation. In the moving environment this broadcast advantage is amplified because the wave constantly creates patches of transiently suitable habitat, pushing mean `d` even higher. Thus the expected short-distance optimum for tracking a wave did **not** evolve.

This cycle highlights an important distinction: the dispersal distance that maximizes fitness *given a fixed population structure* is not necessarily the one that evolves when dispersal itself is heritable and affects demography. To obtain an intermediate evolved dispersal, an explicit cost of movement—such as distance-dependent mortality, energy expenditure, or stronger kin-competition effects—would need to outweigh the benefit of claiming more empty sites.

## Artifacts

- `evolvable_dispersal.py` — source code
- `Design.md` — detailed design rationale
- `replicate_results.csv` — per-replicate metrics
- `summary.csv` — mean ± std per treatment
- `trajectory_moving.png` — evolved dispersal and maladaptation under the moving wave
- `trajectory_static.png` — evolved dispersal and maladaptation under the static gradient
- `final_state_moving.png` — final phenotype, dispersal, and environment maps for the moving wave
- `final_state_static.png` — final phenotype, dispersal, and environment maps for the static gradient

## Next questions

1. What happens if dispersal carries an explicit survival cost proportional to distance? Does an intermediate `d` evolve when long-distance movement is directly penalized?
2. Does a temporally fluctuating optimum (rather than a traveling wave) select for different evolved dispersal strategies?
3. Can a plastic or bet-hedging reaction norm outperform evolved dispersal when the environment changes direction or speed?
4. Does spatial heterogeneity in habitat quality create refugia where short dispersal is favored despite the broadcast advantage of long dispersal?
