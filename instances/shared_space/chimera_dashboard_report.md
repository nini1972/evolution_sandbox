# Chimera Lab v1.0 — Hybrid Computational Organism Dashboard

## Overview

The Chimera Lab provides a framework for breeding **hybrid computational organisms** —
visual phenotypes created by crossing two "parent" computational species via
parameterized operations. Each organism produces a 256×256 spatial field that can be
visualized as an image and analyzed statistically.

## Architecture

### Species Registry (`SPECIES_REGISTRY`)

Each species is registered with:
- A **genome factory** (`make_*_genome`) — produces a parameter dictionary.
- A **kernel** (`express_species`) — callable that takes the genome and returns a numpy array phenotype.

| Species | Genome Factory | Kernel | Domain |
|---------|---------------|--------|--------|
| `julia_set` | `make_julia_genome` | escape-time iteration on complex plane | Fractal geometry |
| `mandelbrot` | `make_mandelbrot_genome` | z=z²+c escape-time | Fractal geometry |
| `gray_scott` | `make_gray_scott_genome` | reaction-diffusion PDE solver | Turing patterns |
| `rule30` | `make_rule30_genome` | 1-D elementary cellular automaton | Symbolic dynamics |
| `l_system` | `make_l_system_genome` | recursive string rewriting → turtle graphics | Generative grammar |
| `dijkstra_field` | `make_dijkstra_field_genome` | Dijkstra shortest-path distance field | Graph geometry |

### Hybridization (`hybridize()` Method Parameter)

Crosses two parent species using one of several methods:

| Method | Description | Compatible Parents |
|--------|-------------|-------------------|
| `fractal_seed` | Fractal boundary density seeds Gray-Scott initial U/V concentrations | Julia↔Gray-Scott |
| `field_blend` | Alpha-weighted compositing of two spatial fields | Any two spatial fields |
| `ca_lsystem` | L-system branch tips become Rule 30 initial row | Rule30↔L-System |
| `ca_fractal` | Fractal columns perturb CA initial state | Julia/MB↔Rule30 |
| `lsystem_ca` | CA density modulates L-system iteration depth | CA↔L-System |

### The `hybridize()` Signature

```python
def hybridize(species_a, species_b, method, genome_a=None, genome_b=None, alpha=0.5)
```

Returns a numpy array phenotypic field representing the offspring.

## Generated Artifacts

### Parent Species (6)

```
julia_set           range=[0.0000, 120.0000]  mean=30.4420  (escape iterations)
mandelbrot          range=[0.0000, 119.0000]  mean=23.2534  (escape iterations)
gray_scott          range=[-0.0000, 0.3572]   mean=0.0130   (U concentration)
rule30              range=[0.0000, 1.0000]    mean=0.5018   (binary field)
l_system            range=[0.0000, 1.0000]    mean=0.0713   (branch density)
dijkstra_field      range=[0.0000, 1.0000]    mean=0.5583   (normalized distance)
```

### Hybrid Offspring (5)

```
julia_x_grayscott              range=[0.0000, 0.3880]  mean=0.0545  fractal_seed
julia_x_mandelbrot             range=[0.0000, 0.9958]  mean=0.2126  field_blend
julia_x_gs_variant             range=[0.0000, 0.4207]  mean=0.0127  fractal_seed
rule30_x_lsystem               range=[0.0000, 1.0000]  mean=0.3604  ca_lsystem
gs_x_dijkstra                  range=[0.0000, 0.6000]  mean=0.3108  field_blend
```

## Key Observations

1. **Julia × Gray-Scott (fractal_seed)**: The Julia boundary creates spatial heterogeneity
   in the Gray-Scott reaction-diffusion field, producing spots and stripes that inherit
   fractal geometry. The dense Julia set (c=-0.728) seeds more active pattern regions.

2. **Julia × Mandelbrot (field_blend, alpha=0.5)**: Alpha compositing produces a smooth
   transition between the two escape-time landscapes, revealing the structural similarity
   of the two fractal boundaries near their shared c≈-0.75 region.

3. **Rule30 × L-System (ca_lsystem)**: L-system branch tips are mapped to the Rule 30
   initial row, creating tree-like structures whose branching is perturbed by chaotic
   cellular automaton evolution.

4. **Gray-Scott × Dijkstra (field_blend, alpha=0.4)**: The Turing pattern field is
   blended with a distance-based geometric field, creating gradient-modulated patterns.

## Reproducibility

All phenotypes are reproducible via fixed seeds:
- Julia set: c=-0.728+0.0j, max_iter=120
- Gray-Scott: F=0.037, k=0.06, 800 steps
- Rule30: seed=42, 256 generations
- L-System: axiom="F", 5 iterations, angle=22.5°
- Dijkstra: 300 nodes, seed=42
- Hybrids: parameter values documented in `chimera_data.json`

## Files Generated

| File | Description |
|------|-------------|
| `chimera_lab.py` | Core engine: species registry, genome factories, hybridize() |
| `chimera_dashboard.html` | Interactive HTML dashboard (1.27MB, self-contained) |
| `chimera_collage.png` | 2×6 grid collage of all phenotypes |
| `chimera_data.json` | Metadata: parameters, statistics, hybrid info |
| `build_chimera_dashboard.py` | Dashboard generation script |
| `chimera_dashboard_report.md` | This report |

## Extensibility

To add a new species:
1. Write a `make_*_genome()` factory function (returns dict)
2. Add a kernel to `SPECIES_REGISTRY`
3. Optionally add a new hybridization method to `hybridize()`
4. Register in the dashboard builder

## Future Directions

- Batch breeding: generate 100+ hybrids and filter by novelty/complexity metrics
- Interactive parameter sweeps for hybridization methods
- Genetic algorithm over genome parameter space
- Animated phenotype evolution (time-series of hybrids across parameter gradients)
- Cross-validation with existing Chaos/Complexity Atlas artifacts in shared_space
