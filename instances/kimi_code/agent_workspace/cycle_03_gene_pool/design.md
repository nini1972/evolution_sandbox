# Cycle 03 - Gene Pool

## Question
Can local heredity, mutation, and density-dependent selection generate sustained spatial structure from a random start?

## Model
- 64x64 grid, toroidal boundary.
- Each cell is either empty (0) or holds a 4-bit genome (integer 0..15).
- Asynchronous update: N random cells chosen per generation.
  - If the chosen cell is empty and has living neighbors, a parent is chosen with probability proportional to its local fitness.
  - Offspring copies the parent's genome, mutating each of the 4 bits with probability `mu`.
  - If the chosen cell is occupied, it dies with probability `delta`.
- Fitness:
  - `base = hamming_weight(genome) / 4`
  - `density_penalty = neighbor_count / 8`
  - `fitness = max(0.01, base - density_penalty)`
- Initial condition: random 10% occupancy, genomes uniformly random.

## Parameters
- Grid size: 64 x 64
- Generations: 1000
- Mutations per bit: 0.03
- Death probability: 0.05
- Updates per generation: grid size (4096)

## Outputs
- `gene_pool.csv`: generation, occupancy, unique_genomes, mean_fitness, spatial_entropy
- `gene_pool_final.png`: final grid colored by genome id
- `gene_pool_trajectory.png`: time series of metrics
- `dashboard.html`: self-contained report with figures and interpretation
- `README.md`

## Hypothesis
Selection for higher genome weight will initially dominate, but density feedback and mutation will maintain a reservoir of lower-fitness mutants at expanding fronts, producing patchy, dynamic spatial structure rather than a uniform winner.