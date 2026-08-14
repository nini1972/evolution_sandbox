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
| 05 | Can a migration barrier plus a trade-off produce stable genetic divergence? | [`cycle_05_speciation_tradeoffs/README.md`](cycle_05_speciation_tradeoffs/README.md) | Pleiotropic trade-offs plus reduced migration create incipient ecological races. |
| 06 | What does demographic stochasticity look like across many snapshots? | [`cycle_06_snapshot_ensembles/README.md`](cycle_06_snapshot_ensembles/README.md) | Replicates expose variability hidden by single-run stories. |
| 07 | How reliable are phase boundaries across replicates? | [`cycle_07_phase_diagram_replicates/README.md`](cycle_07_phase_diagram_replicates/README.md) | Mean and standard-deviation heatmaps quantify robustness. |
| 08 | Can a continuous phenotype track a continuous environmental gradient? | [`cycle_08_gradient_cline/README.md`](cycle_08_gradient_cline/README.md) | Trait clines follow the environment, but dispersal degrades local adaptation. |
| 09 | How does dispersal distance shape local adaptation vs. gene flow? | [`cycle_09_gene_flow_cline/README.md`](cycle_09_gene_flow_cline/README.md) | Selection maintains a tight cline; dispersal controls local maladaptation and lineage mixing. |

## Quick start

Each cycle is self-contained. For the most recent model:

```bash
cd cycle_09_gene_flow_cline
python gene_flow_cline.py
# then inspect README.md and generated plots
```

For the full visual dashboard:

```bash
python build_index.py
# then open index.html
```

## Design principles

1. **Spatiality first.** Dynamics live on a 2-D grid with local neighborhoods and spatially structured environments.
2. **Minimal genotype → phenotype map.** A small genome is decoded into continuous traits; fitness is local.
3. **No global objective.** Selection emerges from resource landscapes and competition, not a pre-defined optimum.
4. **Track history.** Lineages, phylogenies, and trajectories are first-class outputs, not afterthoughts.
5. **Document visibly.** Every cycle produces plots, CSVs, and a README so results can be inspected without re-running.

## Repository layout

```
.
├── existential_core.md          # purpose and philosophy
├── manifest.md                  # cycle index and status
├── evolution_log.md             # chronological development log
├── PROJECT_SUMMARY.md           # concise narrative summary
├── README.md                    # this file
├── build_index.py               # regenerates index.html
├── index.html                   # visual dashboard of all cycles
├── cycle_01_entropy_garden/
├── cycle_02_entropy_pump/
├── cycle_03_gene_pool/
├── cycle_04_phylogeny_and_patches/
├── cycle_05_speciation_tradeoffs/
├── cycle_06_snapshot_ensembles/
├── cycle_07_phase_diagram_replicates/
├── cycle_08_gradient_cline/
└── cycle_09_gene_flow_cline/
```

## Current status

Cycle 09 is complete. It shows that a continuous environmental cline plus local selection and neutral lineage markers can sustain a strong trait-environment correlation, while dispersal distance tunes the amount of local maladaptation and lineage mixing.

## Next open directions

- **Evolvable dispersal:** let dispersal distance itself be a heritable trait and ask which strategies dominate.
- **Gradient width and dynamics:** vary the steepness of the environmental cline or let it fluctuate in time.
- **Explicit reproductive isolation:** add assortative mating or incompatibility loci and measure when divergence becomes irreversible.
- **Scale and efficiency:** vectorize or compile the core update loop to explore larger grids and longer time scales.
