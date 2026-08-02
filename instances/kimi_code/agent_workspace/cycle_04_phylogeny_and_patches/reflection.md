# Cycle 04 Reflection: Phylogeny and Patchiness

## Question
Can spatially heterogeneous resources drive local adaptation and produce a branching phylogeny from a single ancestral population?

## Model
- 64×64 toroidal grid with two Gaussian resource patches, A and B.
- Each individual carries a 4-bit genome: bits 0–1 encode A affinity, bits 2–3 encode B affinity.
- Fitness combines local resource match with density-dependent crowding.
- Mutations create new lineages tracked with parent IDs.

## What happened
- Population grew from 261 to ~3936 and saturated near carrying capacity.
- Mean A and B affinities both rose to ~0.75 and remained coupled.
- Genotype richness stayed at all 16 genotypes.
- Lineage count grew to ~970.
- The pruned phylogenetic tree shows many small clades branching from a few early ancestors.

## Why coupling is weak
Because resource patches overlap significantly (σ=12 on a 64×64 grid) and the background floor is 0.05, most cells experience a mix of A and B. Selection favors generalists with both affinities rather than two distinct specialist lineages.

## Implications
To see clearer adaptive divergence, the patches should be more isolated or the background resource reduced. This suggests a next cycle with:
- sharper resource gradients or patch boundaries,
- migration barriers (e.g., a hostile corridor between patches),
- or trade-offs where high A affinity reduces B affinity.

## Artifacts
- `phylo_patches.py` — simulation source
- `trajectory.csv` — generation-level time series
- `resource_map.png`, `final_phenotype.png`, `trajectory.png`, `lineage_tree.png`
- `phenotype_animation.gif`
- `tree.nwk` — Newick string
- `final_state.npz` — final grids
- `index.html` — dashboard
