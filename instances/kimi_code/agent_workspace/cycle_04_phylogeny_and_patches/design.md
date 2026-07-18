# Cycle 04 Design: Phylogeny and Resource Patches

## Purpose

Evolve the Cycle 03 spatial gene-pool model by adding two forces that create richer evolutionary dynamics:

1. **Individual lineage tracking** — record parent-child relationships so we can reconstruct a phylogenetic tree of surviving lineages.
2. **Spatially heterogeneous resources** — two resource patches (A and B) impose antagonistic local selection, creating different optimal genotypes in different regions.

The goal is to watch adaptation, speciation-like spatial structure, and lineage turnover emerge in a single run.

## Model

### World

- 64×64 toroidal grid.
- Two resource fields, `R_A` and `R_B`, defined by circular Gaussian patches:
  - Patch A center: (16, 16), σ = 12.
  - Patch B center: (48, 48), σ = 12.
  - Formula: `R_patch(x,y) = exp(-dist² / (2σ²))`.
  - A small background floor (0.05) exists outside patches.
- Each cell has an environment vector `(R_A, R_B)`.

### Genomes and phenotypes

- Each individual carries a 4-bit genome, encoded as an integer 0–15.
- Bits 0–1 encode affinity for resource A.
- Bits 2–3 encode affinity for resource B.
- Phenotype: `A_aff = (bit0 + bit1) / 2` ∈ {0, 0.5, 1}; `B_aff = (bit2 + bit3) / 2`.

### Fitness

Base fitness at a cell depends on how well the local resources match the genotype:

```
base_fitness = (R_A * A_aff + R_B * B_aff) / (R_A + R_B + 1e-6)
```

If both resources are near zero, a small neutral floor (`0.2`) prevents extinction.
Density dependence is unchanged:

```
effective_fitness = base_fitness * (1 - occupied_neighbours / 8)
```

### Life cycle

Each generation:

1. **Death**: every occupied cell dies with probability `p_death = 0.05`.
2. **Birth**: every surviving occupied cell tries to seed a random empty Moore neighbour.
   - Target is chosen uniformly among the cell’s empty Moore neighbours.
   - Birth probability onto that target is proportional to `effective_fitness`.
3. **Inheritance and mutation**:
   - The child copies the parent genome.
   - Each of the 4 bits flips independently with probability `p_mut = 0.03`.
   - If any bit flips, the child receives a **new lineage ID**; otherwise it inherits the parent lineage ID.

### Lineage tracking

- Every lineage has an ID, a `birth_generation`, a `parent_id`, and optionally a `death_generation`.
- Initial cells each receive a unique lineage ID with `parent_id = 0` (a virtual root).
- When a mutation creates a new lineage, store the parent lineage ID and the new genome.
- When the last living cell with a given lineage ID dies, record `death_generation`.
- At the end of the run, prune the tree to extant lineages and their ancestors to keep it visualizable.

## Parameters

| Parameter | Value |
|-----------|-------|
| Grid size | 64 × 64 |
| Generations | 500 |
| Initial occupancy | 10% random cells |
| Death probability | 0.05 |
| Mutation probability per bit | 0.03 |
| Resource patch σ | 12 |
| Resource background floor | 0.05 |
| Seed | 7 |

## Outputs

1. `phylo_patches.py` — simulation source.
2. `phylo_patches.csv` — time series per generation.
3. `resource_map.png` — spatial layout of `R_A` and `R_B`.
4. `trajectory.png` — population metrics over time.
5. `final_phenotype.png` — final grid coloured by resource affinity bias.
6. `lineage_tree.png` — pruned phylogeny of surviving / abundant lineages.
7. `lineage_tree.newick` — Newick string of the pruned tree.
8. `dashboard.html` — self-contained summary dashboard.
