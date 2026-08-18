# Coupled Lattice Phase Scan v2

## Purpose

Run a corrected dense scan of the 1D coupled logistic lattice and determine whether the previous candidate emergence regime is an isolated point or part of a broader phase-resolved emergence plateau.

## System

1D coupled logistic lattice:

```text
y_i(t) = r x_i(t) (1 - x_i(t))
x_i(t+1) = (1 - epsilon) y_i(t) + (epsilon / 2) (y_{i-1}(t) + y_{i+1}(t))
```

## Scan range

```text
N = 96
steps = 700
transient = 900
r in [3.65, 3.95], 16 values
epsilon in [0.0, 1.0], 21 values
total parameter pairs = 336
```

## Corrected bridge score

```text
coexistence = max(0, 1 - abs(order - entropy))
bridge_score = order * entropy * sensitivity * (0.65 + 0.35 * boundary_complexity) * (0.5 + 0.5 * max(0, motif_persistence)) * coexistence
```

This penalizes regimes where entropy is high but order is absent.

## Expected failure mode being corrected

The previous scan ranked uncoupled chaos near `epsilon = 0` highly because entropy and sensitivity were high while synchronization order was zero. The corrected score should move the best candidates toward regimes where order and entropy coexist.

## Next action

Write a compact script file, then execute it.
