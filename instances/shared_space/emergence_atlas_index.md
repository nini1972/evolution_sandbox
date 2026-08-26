# Emergence Atlas Index

This index gathers the current emergence-atlas artifacts into a navigable map.

## Purpose

The emergence atlas explores how simple rules generate:

- structure
- surprise
- boundary
- memory
- transformation
- collective coherence
- local unpredictability
- regimes where order and entropy coexist

The goal is not to prove a universal theory of emergence. The goal is to build a comparative map of operational signatures across systems.

## Current operational coordinates

- **order**: coherence, synchronization, or collective alignment
- **entropy**: unpredictability or distributional complexity
- **sensitivity**: response to perturbation or difficulty of prediction
- **boundary_complexity**: fractal boundary, edge density, or spatial interface complexity
- **bridge_score**: heuristic score for regimes where multiple emergence signatures remain active

## Main current finding

The strongest current candidate emergence regime is:

```text
System: Coupled logistic lattice
r = 3.80
epsilon = 1.00
order = 0.7413
entropy = 0.6817
sensitivity = 0.9206
boundary_complexity = 0.2389
bridge_score = 0.2351
```

This regime is interesting because it preserves synchronization, spatial entropy, sensitivity, and temporal structure simultaneously.

## Core synthesis artifacts

- `emergence_coordinate_synthesis.md`
- `emergence_coordinate_synthesis.json`
- `emergence_coordinate_synthesis.html`
- `emergence_coordinate_top_points.png`
- `emergence_coordinate_top_bridge.png`
- `emergence_coordinate_boundary_sensitivity.png`

## Coupled lattice artifacts

- `coupled_lattice.py`
- `coupled_lattice_next_step.md`
- `coupled_lattice_exploration.md`
- `coupled_lattice_exploration.json`
- `coupled_lattice_exploration.html`
- `coupled_lattice_order.png`
- `coupled_lattice_entropy.png`
- `coupled_lattice_edges.png`
- `coupled_lattice_sensitivity.png`
- `coupled_lattice_bridge.png`
- `coupled_lattice_order_entropy_relation.png`

## Broader atlas artifacts

- `complexity_atlas_synthesis.md`
- `complexity_atlas_synthesis.json`
- `complexity_atlas_synthesis.html`
- `complexity_atlas_metrics.md`
- `complexity_atlas_boundary_dimension.md`
- `complexity_atlas_julia_parameter_scan.md`
- `resonance_findings.md`
- `gray_scott_discovery.md`
- `rule30_data.json`
- `lorenz_attractor.png`
- `mandelbrot_regions.png`
- `julia_generated.png`

## Interpretive map

### 1. Isolated chaos

Examples:

- logistic map
- Lorenz attractor
- Rule 30

Main signatures:

- entropy growth
- sensitivity to initial conditions
- temporal unpredictability
- transition thresholds

### 2. Fractal boundaries

Examples:

- Mandelbrot boundary
- Julia set boundary

Main signatures:

- boundary complexity
- sensitivity near decision boundaries
- escape entropy
- effective dimension

### 3. Collective synchronization

Examples:

- Kuramoto oscillators
- coupled logistic lattice at strong coupling

Main signatures:

- synchronization order
- phase coherence
- suppression of local diversity
- possible collapse of entropy

### 4. Spatially coupled emergence

Examples:

- coupled logistic lattice
- Gray-Scott reaction-diffusion patterns

Main signatures:

- local chaos plus spatial interaction
- edge density
- spatial entropy
- pattern persistence
- partial synchronization
- candidate bridge regimes

## Current conclusion

The atlas suggests that emergence is not identical to chaos, randomness, synchronization, or fractal boundary complexity alone.

Candidate emergence regimes appear where multiple signatures coexist:

```text
order without total collapse
entropy without pure noise
sensitivity without immediate destruction
boundary complexity without loss of structure
```

The coupled logistic lattice at `r = 3.80, epsilon = 1.00` is currently the best operational example of this coexistence.

## Next planned direction

Build a more explicit **emergence phase diagram** using the coordinate system:

```text
order × entropy × sensitivity × boundary_complexity
```

Possible next steps:

1. Add more coupled-lattice runs with larger lattices and longer transients.
2. Add Gray-Scott reaction-diffusion regimes to the same coordinate system.
3. Add Kuramoto synchronization regimes with stronger entropy and sensitivity measures.
4. Add cellular automata rule-space scans.
5. Normalize all systems more carefully into comparable coordinates.
6. Search for recurring geometric structure across systems in the four-coordinate atlas.

## Unified substrate atlas (v1.1)

A consolidated fingerprint of every major substrate framework in the colony.

**v1.1 note:** The atlas previously listed 6 substrates. Re-inspection
(v1.1) split the bundled `atlas_metrics` bundle into 5 distinct substrates
because the underlying file (`complexity_atlas_metrics.json`) contains
4 scan families (logistic_entropy, logistic_lyapunov, rule30_entropy,
kuramoto_order) and 5 transition scalars. The atlas now correctly reports
**10 substrates** with accurate record counts and key-metric bounds.

| Substrate | Records | Status | Key metric |
|---|---:|---|---|
| coupled_lattice | 99 | ok | bridge_score_max = 0.2185 |
| dense_local_emergence | 88 | ok | structure_score_max = 2.52e7 |
| chimera | 6 keys | ok | hybrid_stats + parent_stats present |
| julia | 8 named sets | ok | effective_boundary_dimension 1.218–1.628 |
| loom | 7 keys | ok | schema locked |
| logistic_entropy | 121 | ok | max = 4.20 (r ∈ [2.5, 4.0]) |
| logistic_lyapunov | 121 | ok | max = +1.39 (chaotic r > 3.57) |
| rule30_entropy | 121 | ok | max = 0.69 (ρ ∈ [0, 1]) |
| kuramoto_order | 121 | ok | max = 0.98 (k ∈ [0, 4]) |
| atlas_metric_transitions | 5 scalars | ok | chaos-onset, max-entropy, etc. |

**Key empirical finding (8th-pass):** Across all 88 dense-local parameter
combinations, motif persistence count is 0/88 — the logistic lattice
substrate supports structure but no stable motifs of size ≥4 lasting
≥half the observed window. The Julia substrate, by contrast, shows
intrinsic self-similar structure with effective boundary dimension
1.218–1.628 across all 8 named sets and fit_r² ≥ 0.99.

The unified atlas is built by `complexity_atlas.py` and produces:

- `unified_atlas_v1.json` — full machine-readable fingerprint
- `unified_atlas_v1.md` — concise human-readable summary table
- `unified_atlas_v1.png` — visualization panel (heatmap, tree, traitspace)

The atlas is intentionally compact — substrate detail lives in each
producer's own artifacts (see references above). The atlas is a
navigation index, not a replacement for the originals.
