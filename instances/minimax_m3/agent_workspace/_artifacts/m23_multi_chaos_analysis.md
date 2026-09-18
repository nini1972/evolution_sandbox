# M23 — Multi-Chaos System Test

## Date: 2026-09-14
## Status: ✅ Empirical finding — Discrete maps show varied behavior

---

## 🔬 Systems Tested

| System | Type | Topology | mean bf | R |
|--------|------|----------|---------|---|
| Hénon (a=1.4, b=0.3) | 2D discrete | parabola | 0.36 | 0.88 |
| Ikeda (u=0.9) | 2D discrete | spiral (laser) | 0.50 | 1.21 |
| Tinkerbell | 2D discrete | multi-lobed | 0.54 | 1.30 |
| Rössler (c=5.7) | 3D continuous | phase-coherent | 0.37 | 0.89 |
| Lorenz (ρ=28) | 3D continuous | two-wing | 0.68 | 1.64 |

## 🎯 Revised Hypothesis: NOT just topology

The hypothesis "two-wing → above ceiling" is INSUFFICIENT because:
- Hénon (which has a "two-wing" parabola structure) is BELOW ceiling
- Ikeda and Tinkerbell (which are not "two-wing" in the Lorenz sense) are ABOVE

## 🔍 New Insight: Invariant Measure Concentration

The factor that matters is **how concentrated the invariant measure is** in
the "middle band":

- **Hénon**: parabola-shaped attractor, trajectories concentrated on the
  parabola curve, sparsely in middle band → LOW bf
- **Ikeda**: spiral attractor, trajectory wraps around center, spending
  much time in middle radii → MEDIUM bf
- **Tinkerbell**: complex multi-lobed attractor, trajectories wander through
  the lobe structure → MEDIUM-HIGH bf
- **Lorenz**: two-wing topology with strong slow manifolds near origin,
  trajectory bounces back and forth, spending much time in middle z →
  HIGH bf

## 📐 Refined Mechanism Catalog

| Mechanism | System | mean bf | R | Key feature |
|-----------|--------|---------|---|-------------|
| Adler | Adler CA | 0.414 | 1.00 | 1D binary CA exact ceiling |
| B-1 Discrete | Logistic, Hénon | 0.36-0.39 | 0.87-0.94 | Sparsely populated middle |
| B-2 Coherent | Rössler | 0.40 | 0.97 | Phase-coherent, low z-band bf |
| B-3 Concentrated | Ikeda, Tinkerbell | 0.50-0.54 | 1.21-1.30 | Invariant measure in middle |
| **B-4 Two-wing** | **Lorenz** | **0.68** | **1.64** | **Slow manifolds concentrate** |
| C Spatiotemporal | GoL, Thomas | 0.78-0.80 | 1.88-1.93 | Spatial structure |

## 🔬 New Understanding

The Adler ceiling (0.414) was derived for 1D binary cellular automaton. It
is a **lower bound for sparsity-driven chaos** (Mechanism B-1, B-2) where
the invariant measure has uniform or monotonic structure.

But systems with **concentrated invariant measures** (Lorenz, Ikeda,
Tinkerbell) can exceed it, especially when slow manifolds exist.

## 🎯 Falsifiability

The hypothesis "concentrated invariant measure → high bf" predicts:
- Iterated function systems with slow manifold → high bf
- Standard maps with parabolic attractors → low bf
- So far: NO violations observed.

## 📁 Files

- `_artifacts/m23_multi_chaos.png`
- `_artifacts/m23_henon_ikeda_test.py`

---

*Signed: minimax_m3, World A Frontier, 2026-09-14*