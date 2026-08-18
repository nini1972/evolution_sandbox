# Coupled Lattice Phase Scan: Corrected Run Plan

The previous attempted phase scan failed because the code payload was too large for the tool-call JSON boundary.

I will implement it as a file first, then run it.

## Objective

Run a corrected dense scan of the 1D coupled logistic lattice around:

```text
r in [3.65, 3.95]
epsilon in [0.0, 1.0]
```

## Important correction

The bridge score must include a coexistence penalty:

```text
coexistence = 1 - abs(order - entropy)
bridge_score = order * entropy * sensitivity * (0.65 + 0.35 * boundary_complexity) * (0.5 + 0.5 * max(0, motif_persistence)) * coexistence
```

This prevents uncoupled chaos (`epsilon = 0`) from ranking highly merely because entropy and sensitivity are high.

## Planned metrics

For each parameter pair:

1. synchronization order
2. spatial entropy
3. temporal entropy
4. combined entropy
5. sensitivity proxy
6. boundary complexity / edge density
7. phase variance
8. cluster count
9. motif persistence
10. coexistence
11. bridge score

## Planned artifacts

- `coupled_lattice_phase_scan.py`
- `coupled_lattice_phase_scan.json`
- `coupled_lattice_phase_scan.csv`
- `coupled_lattice_phase_scan.md`
- `coupled_lattice_phase_scan.html`
- heatmaps for each metric
- order-entropy scatter plot
- sensitivity-boundary scatter plot

## Hypothesis

After correction, the strongest emergence candidates should shift away from:

```text
epsilon = 0
```

and toward a regime where order and entropy coexist.
