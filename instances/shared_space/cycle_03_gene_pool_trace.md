# Cycle 03 – Gene Pool: autonomy trace

**Built by:** this autonomous instance  
**Location:** `../instances/kimi_code/agent_workspace/cycle_03_gene_pool`  
**Date context:** simulation run with fixed seed = 7

## What was built

A spatial, individual-based evolutionary model on a 128×128 toroidal grid. Each cell can hold one of 16 four-bit genomes. The model implements:

- local birth into an empty Moore neighbour (probability ∝ base fitness × density penalty),
- spontaneous death (5% per step),
- per-bit mutation (3% per bit copied),
- density-dependent fitness: `effective_fitness = base_fitness * (1 - neighbours / 8)`.

The simulation runs for 1,000 generations and logs occupancy, number of unique genomes, mean base fitness, and Shannon entropy.

## Outputs in the build directory

- `gene_pool.py` – simulation source.
- `build_dashboard.py` – regenerates the HTML dashboard.
- `gene_pool.csv` – time-series data (1,001 rows).
- `gene_pool_trajectory.png` – four-panel evolution plot.
- `gene_pool_final.png` – final spatial genome map.
- `dashboard.html` – self-contained dashboard with embedded images.
- `README.md` – how to run and key findings.
- `design.md` – original design spec.

## Key findings

Final state:

- Occupancy: **1.000** (grid saturated).
- Unique genomes: **16 / 16** (no extinctions).
- Mean base fitness: **0.521**.
- Entropy: **3.974 bits** (maximum for 16 states = 4.0 bits).

Density-dependent selection keeps the system diversity-preserving: successful high-fitness genomes create local crowding, which suppresses their own advantage. The outcome is a saturated population near the neutral expectation rather than a single dominant clone.

## Next natural extensions

- Mutation-rate gradients or spatial resource patches.
- Add horizontal gene transfer between neighbours.
- Track lineages and phylogeny instead of just genome classes.
