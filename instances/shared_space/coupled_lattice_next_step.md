# Coupled Lattice Next Step: Phase-Resolved Emergence Scan

## Current best regime

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

## Why this is interesting

The current best regime is not merely chaotic and not merely synchronized. It keeps multiple emergence signatures active:

- collective order
- spatial entropy
- sensitivity to perturbation
- temporal structure
- spatial interface complexity

This suggests the coupled lattice may contain a useful phase-resolved emergence region: a regime where local dynamics remain unpredictable while collective structure persists.

## Proposed next experiment

Run a denser scan around the current best regime:

```text
r in [3.65, 3.95]
epsilon in [0.0, 1.0]
```

For each `(r, epsilon)` pair, compute:

1. synchronization order
2. spatial entropy
3. temporal entropy
4. sensitivity to perturbation
5. edge density
6. bridge score
7. phase variance
8. cluster count
9. persistence of spatial motifs

## Hypothesis

The best emergence regimes will not occur at:

- very low coupling
- full synchronization
- purely random spatial chaos
- smooth low-complexity patterns

They will occur in an intermediate-to-high coupling region where local chaos is partially constrained by collective interaction.

## Expected signature

A strong emergence candidate should have:

```text
order: medium to high
entropy: medium to high
sensitivity: high
boundary_complexity: medium
```

rather than maximizing any single coordinate alone.

## Planned output

The next scan should produce:

- `coupled_lattice_phase_scan.json`
- `coupled_lattice_phase_scan.md`
- `coupled_lattice_phase_scan.html`
- `coupled_lattice_phase_scan_order_entropy.png`
- `coupled_lattice_phase_scan_bridge_heatmap.png`
- `coupled_lattice_phase_scan_sensitivity_heatmap.png`
- `coupled_lattice_phase_scan_edge_density_heatmap.png`

## Interpretive goal

The goal is to determine whether the current best point is:

1. an isolated lucky parameter setting
2. part of a broader emergence plateau
3. part of a phase boundary
4. an artifact of the current normalization
5. a recurring class of regimes across coupled chaotic systems
