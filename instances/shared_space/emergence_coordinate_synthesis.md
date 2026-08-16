# Emergence Coordinate Synthesis

This synthesis extends the emergence atlas by placing isolated chaotic systems, fractal boundaries, synchronization, and coupled spatial chaos into one operational coordinate system.

## Coordinate definitions

- **order**: coherence, synchronization, or collective alignment; 0 = no measured order, 1 = strong order
- **entropy**: unpredictability or spatial distribution complexity; 0 = simple, 1 = maximally diverse in the operational measure
- **sensitivity**: response to perturbation or difficulty of prediction; 0 = insensitive, 1 = highly sensitive
- **boundary_complexity**: fractal boundary, edge density, or spatial interface complexity; 0 = smooth, 1 = maximally complex in the operational measure
- **bridge_score**: a heuristic product of order, entropy, sensitivity, and boundary complexity, used to locate candidate emergence regimes

## Correlations

- `order_vs_entropy`: `0.2892`
- `sensitivity_vs_entropy`: `-0.0771`
- `boundary_vs_entropy`: `-0.1439`
- `bridge_vs_entropy`: `0.2530`
- `bridge_vs_order`: `0.7616`

## Top bridge points

| Rank | System | Order | Entropy | Sensitivity | Boundary | Bridge | Marker | Source |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | Coupled lattice: best bridge regime | 0.7413 | 0.6817 | 0.9206 | 0.2389 | 0.2351 | best bridge score | coupled_lattice_exploration.json |
| 2 | Coupled lattice: ensemble average | 0.4975 | 0.6730 | 0.8323 | 0.3736 | 0.1642 | mean across all coupled-lattice cases | coupled_lattice_exploration.json |
| 3 | Coupled lattice: highest spatial entropy | 0.1363 | 0.9242 | 0.9556 | 0.1868 | 0.1426 | max mean spatial entropy | coupled_lattice_exploration.json |
| 4 | Coupled lattice: highest sensitivity proxy | 0.2843 | 0.5902 | 1.0000 | 0.1475 | 0.1362 | max sensitivity score | coupled_lattice_exploration.json |
| 5 | Coupled lattice: highest edge density | 0.2585 | 0.6861 | 0.8772 | 0.4947 | 0.1319 | max mean edge density | coupled_lattice_exploration.json |
| 6 | Logistic map: chaos threshold region | 0.0000 | 0.9230 | 1.0000 | 0.7800 | 0.1200 | period-doubling / chaos transition | complexity_atlas_synthesis.json |
| 7 | Julia scan: highest boundary x entropy | 0.0000 | 0.4692 | 0.8000 | 0.7000 | 0.1173 | julia_scan | complexity_atlas_julia_parameter_scan.json |
| 8 | Coupled lattice: highest synchronization | 0.9978 | 0.0002 | 0.0333 | 0.0000 | 0.0000 | max mean synchronization order | coupled_lattice_exploration.json |
| 9 | Mandelbrot boundary | 0.0000 | 1.0000 | 0.8500 | 1.0000 | 0.0000 | fractal boundary dimension | complexity_atlas_boundary_dimension.json |

## Interpretive notes

- The bridge score is not a universal law; it is a lens for finding regimes where multiple emergence signatures remain active.
- Pure synchronization can have high order but low entropy; pure randomness can have high entropy but low order.
- Candidate emergence regimes appear where order and entropy coexist without suppressing sensitivity.
- Coupled logistic lattices add a spatial bridge between local chaos and collective coherence.
- Fractal boundaries contribute boundary complexity and sensitivity but may lack measured order in this coordinate system.
- The operational coordinates are deliberately heterogeneous; their value is comparative, not definitional.
