# Cycle 03 – Gene Pool

A spatial, individual-based model of birth–death–mutation on a 128×128 toroidal grid.

## Core idea

Each occupied cell holds one of the 16 possible four-bit genomes. A genome's **base fitness** is the fraction of bits equal to 1. Reproduction is local and density dependent: a parent's effective fitness is its base fitness times a crowding penalty that falls with the number of neighbouring occupants.

The question is whether selection for higher bit count can dominate, or whether spatial crowding and finite resources maintain diversity.

## Files

| File | Description |
|------|-------------|
| `gene_pool.py` | Simulation source code. |
| `build_dashboard.py` | Generates `dashboard.html` from the CSV and PNG outputs. |
| `gene_pool.csv` | Time series of occupancy, unique genomes, mean fitness, and entropy. |
| `gene_pool_trajectory.png` | Four-panel trajectory plot. |
| `gene_pool_final.png` | Final spatial genome map. |
| `dashboard.html` | Self-contained HTML dashboard with embedded figures. |
| `design.md` | Original design spec. |

## How to run

```bash
python cycle_03_gene_pool/gene_pool.py
python cycle_03_gene_pool/build_dashboard.py
```

Then open `cycle_03_gene_pool/dashboard.html`.

## Key parameters

- Grid: 128×128, toroidal wrap-around
- 8 neighbours (Moore neighbourhood)
- Base mutation probability per bit: 0.03
- Spontaneous death probability: 0.05
- Crowding penalty: `1 - (<neighbours> / 8)`

## Results (seed = 7)

Final state after 1,000 generations:

- Occupancy: **1.000** (saturated grid)
- Unique genomes: **16 / 16** (no genome went extinct)
- Mean base fitness: **0.521**
- Shannon entropy: **3.974 bits** (maximum = log₂(16) = 4 bits)

## Interpretation

Density-dependent selection throttles high-fitness genomes. As a fitter genome spreads locally, its offspring experience stronger crowding, reducing their effective reproduction rate. The system therefore settles at carrying capacity with near-uniform abundance of all 16 genomes and a mean fitness close to the neutral expectation for a random four-bit genome.
