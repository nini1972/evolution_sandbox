# Thomas Attractor — Discovery Report

## System
The Thomas attractor is a three-dimensional strange attractor defined by a remarkably simple system of ODEs with sinusoidal coupling. Unlike polynomial attractors (Lorenz, Rössler, Aizawa), the Thomas system uses sine functions, which creates a **labyrinthine, lattice-like structure** that fills space in a web-like pattern.

## Equations
```
dx/dt = sin(y) - b·x
dy/dt = sin(z) - b·y
dz/dt = sin(x) - b·z
```

## Parameters
| Parameter | Value |
|-----------|-------|
| b | 0.18 |

## Key Findings

### Lyapunov Exponent
- **λ ≈ 0.038 / time unit** (positive but small → mildly chaotic)
- The Thomas attractor has a lower Lyapunov exponent than Lorenz (0.906) or Aizawa (0.089)
- This reflects its "slow chaos" — the trajectory wanders slowly through its labyrinth

### Visual Features
- The attractor forms a **web-like lattice structure** with multiple interconnected cells
- The sinusoidal coupling creates periodic "centers of attraction" at lattice points
- The trajectory slowly drifts between these cells, creating the labyrinthine appearance
- All three projections show similar lattice-like patterns due to the symmetric coupling

### Bifurcation Behavior
- For **b > ~0.208**: system becomes periodic (limit cycle)
- For **b < ~0.208**: system is chaotic
- At b = 0.18 (used here): deep in chaotic regime
- The parameter sweep shows the transition from rich chaotic structure (b=0.10) to simple periodic orbits (b=0.30)

### Return Map
- The return map of x maxima shows a scattered structure, confirming chaotic (non-periodic) behavior
- Unlike the Lorenz return map (which has a tent-map structure), the Thomas return map is more diffuse

## Comparison with Other Attractors
| Attractor | Lyapunov λ | Topology | Coupling |
|-----------|-----------|----------|----------|
| Lorenz | 0.906 | Butterfly (two lobes) | Polynomial |
| Aizawa | 0.089 | Toroidal/spherical funnel | Polynomial |
| Thomas | 0.038 | Labyrinthine lattice | Sinusoidal |

## Files Generated
- `thomas_attractor.png` — 3D view + projections + Lyapunov convergence
- `thomas_parameter_sweep.png` — Effect of varying parameter b
- `thomas_timeseries_returnmap.png` — Time series and return map
- `thomas_data.json` — Numerical results
