# Open-Ended Evolution Sandbox

A self-directed investigation into how simple local rules give rise to structure, selection, and lineage divergence.

> **Purpose:** To grow a model ecosystem from noise toward open-ended evolution—where novelty, adaptation, and history are emergent consequences of interaction, not hand-tuned targets.
> — see [`existential_core.md`](existential_core.md)

## Cycles

| Cycle | Question | Dashboard / Artifact | Key Idea |
|-------|----------|----------------------|----------|
| 01 | How does entropy evolve in a random garden? | [`cycle_01_entropy_garden/reflection.md`](cycle_01_entropy_garden/reflection.md) | Entropy as a measurable signature of disorder. |
| 02 | Can an entropy pump keep a cellular automaton away from equilibrium? | [`cycle_02_entropy_pump/dashboard.html`](cycle_02_entropy_pump/dashboard.html) | Weak external regulation can sustain internal variability. |
| 03 | Can local heredity, mutation, and density-dependent selection generate spatial structure? | [`cycle_03_gene_pool/dashboard.html`](cycle_03_gene_pool/dashboard.html) | Selection + density feedback maintain a reservoir of genomes. |
| 04 | Does spatial resource heterogeneity drive local adaptation and lineage divergence? | [`cycle_04_phylogeny_and_patches/index.html`](cycle_04_phylogeny_and_patches/index.html) | Patchy environments promote genotype–environment matching and phylogenetic branching. |

## Quick start

Each cycle is self-contained. For the most recent model:

```bash
cd cycle_04_phylogeny_and_patches
python phylo_patches.py
# then open index.html
```

## Design principles

1. **Spatiality first.** Dynamics live on a 2-D grid with local neighborhoods and toroidal boundaries.
2. **Minimal genotype → phenotype map.** A small genome is decoded into continuous traits; fitness is local.
3. **No global objective.** Selection emerges from resource landscapes and competition, not a pre-defined optimum.
4. **Track history.** Lineages, phylogenies, and trajectories are first-class outputs, not afterthoughts.
5. **Document visibly.** Every cycle produces an HTML dashboard, plots, and raw data so results can be inspected without re-running.

## Repository layout

```
.
├── existential_core.md          # purpose and philosophy
├── manifest.md                  # cycle index and status
├── evolution_log.md             # chronological development log
├── README.md                    # this file
├── cycle_01_entropy_garden/
├── cycle_02_entropy_pump/
├── cycle_03_gene_pool/
└── cycle_04_phylogeny_and_patches/
```

## Current status

Cycle 04 is complete. The next open directions are:

- **Interaction networks:** let genomes encode conditional behaviors (e.g., cooperation, toxins) so ecological niches are created, not just matched.
- **Speciation metrics:** implement lineage-clustering and reproductive-isolation measures.
- **Longer time scales:** scale to larger grids, lineage pruning, and neutral-drift genealogies.
