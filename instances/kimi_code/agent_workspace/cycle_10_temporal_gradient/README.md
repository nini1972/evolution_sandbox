# Cycle 10: Temporal Gradient — Tracking a Traveling Environmental Wave

## Question
What happens when a continuous environmental gradient is no longer static, but moves across the landscape as a traveling wave? Does intermediate dispersal allow populations to keep pace, while very short or very long dispersal cause populations to lag or lose local adaptation?

## Model
- Same 40×40 spatial grid and individual-based dynamics as Cycle 09.
- The environmental optimum is now a sinusoidal wave that travels horizontally:
  `env[x] = 0.5 + 0.5 * sin(2π * (x / WIDTH - t / PERIOD))`.
- `PERIOD = 120` generations, so the wave completes one full traverse of the 40-column grid in that time.
- Each individual has a continuous phenotype `α ∈ [0,1]` and a neutral lineage marker.
- Fitness is `exp(−(α − env)² / (2σ²))` with `σ = 0.2`.
- Reproduction is local within a Manhattan-distance `d` neighborhood, weighted by fitness.
- Offspring inherit `α` plus Gaussian mutation (`sd = 0.05`) and the parent's lineage marker; new lineage markers arise at rate `0.005`.

## Parameters
| Parameter | Value |
|-----------|-------|
| Grid | 40×40 |
| Generations | 400 |
| Death rate | 0.08 |
| Selection width σ | 0.2 |
| Mutation sd | 0.05 |
| Lineage mutation rate | 0.005 |
| Wave period | 120 generations |
| Wave amplitude | 0 → 1 across the grid |
| Dispersal distances | 1, 2, 4, 8 |
| Replicates per distance | 10 |

## Key results
| Dispersal | Final trait-env correlation | Maladaptation | Trait variance | Cline amplitude | Lineage richness | F_ST proxy | Moran's I |
|-----------|----------------------------:|--------------:|---------------:|----------------:|-----------------:|-----------:|----------:|
| 1 | 0.160 ± 0.348 | 0.344 ± 0.021 | 0.049 ± 0.006 | 0.225 ± 0.055 | 89.1 ± 7.3 | 0.019 ± 0.003 | 4.81 ± 0.27 |
| 2 | 0.319 ± 0.294 | 0.333 ± 0.019 | 0.047 ± 0.006 | 0.231 ± 0.052 | 71.7 ± 4.5 | 0.023 ± 0.003 | 3.57 ± 0.67 |
| 4 | 0.173 ± 0.280 | 0.351 ± 0.020 | 0.050 ± 0.005 | 0.251 ± 0.063 | 63.9 ± 5.1 | 0.024 ± 0.005 | 1.67 ± 0.48 |
| 8 | 0.193 ± 0.193 | 0.359 ± 0.016 | 0.069 ± 0.006 | 0.249 ± 0.040 | 64.6 ± 8.6 | 0.014 ± 0.003 | 0.51 ± 0.16 |

- **Maladaptation is lowest at `d = 2`**, suggesting an intermediate dispersal optimum for tracking the moving wave. Very short dispersal (`d = 1`) cannot keep up with the wave; longer dispersal (`d = 8`) increases local trait variance and maladaptation through gene flow.
- **Trait variance rises sharply at `d = 8`**, indicating that long-distance migrants import mismatched phenotypes and broaden the local trait distribution.
- **Cline amplitude** is modest (~0.22–0.25) for all dispersals, reflecting the difficulty of maintaining a strong spatial phenotype gradient when the optimum itself keeps moving.
- **Lineage richness** is highest at `d = 1` and declines as dispersal mixes neighborhoods; it plateaus at larger distances.
- **Spatial autocorrelation (Moran's I)** falls from ~4.8 at `d = 1` to ~0.5 at `d = 8`, confirming that long dispersal erodes local lineage structure.
- **Final snapshot trait–environment correlation is noisy** because the wave was at an intermediate phase when measured; maladaptation and cline amplitude are more reliable indicators of tracking quality.

## Interpretation
A traveling environmental optimum selects against both extreme sedentariness and extreme mobility. Very local reproduction lets lineages adapt to the current location but creates a spatial lag when the optimum moves. Very long dispersal provides demographic rescue but imports maladapted alleles and swamps local genetic structure. The outcome is a **temporal migration–selection balance**: the population can partially track the wave, but a residual lag and elevated variance are unavoidable.

## Artifacts
- `temporal_gradient.py` — source code
- `replicate_results.csv` — per-replicate metrics
- `summary.csv` — mean ± std per dispersal
- `trajectory.png` — time series of population, maladaptation, F_ST, and lineage richness for one replicate
- `final_state.png` — environment, phenotype, and lineage maps for one replicate per dispersal
- `summary.png` — summary plots across dispersal distances

## Next questions
1. How does wave speed (period) change the optimal dispersal distance? Slower waves may favor shorter dispersal; faster waves may favor longer dispersal.
2. Can populations evolve dispersal distance itself when the environment fluctuates in time and space?
3. What if individuals use a plastic or bet-hedging reaction norm instead of a fixed phenotype?
4. Does adding local extinction/recolonization events make long dispersal more valuable for tracking moving habitats?
