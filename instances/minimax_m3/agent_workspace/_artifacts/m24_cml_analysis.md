# M24 — Coupled Map Lattice: Coupling Does NOT Exceed Ceiling

## Date: 2026-09-14
## Status: ✅ Empirical — Coupling doesn't push CML above ceiling

---

## 🔬 Experiment

Coupled Logistic Map Lattice (CML) with diffusive coupling:
```
x_i(t+1) = (1-eps)*f(x_i(t)) + (eps/2)*(f(x_{i-1}(t)) + f(x_{i+1}(t)))
```
where f(x) = r*x*(1-x).

Tested: r ∈ {3.5, 3.7, 3.9, 4.0}, eps ∈ {0, 0.1, 0.3, 0.5, 0.7}.

## 📊 Results

| r / eps | 0.0 | 0.1 | 0.3 | 0.5 | 0.7 |
|---------|-----|-----|-----|-----|-----|
| 3.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3.7 | 0.31 | 0.23 | 0.25 | 0.26 | 0.30 |
| 3.9 | 0.29 | 0.41 | 0.38 | 0.38 | 0.37 |
| 4.0 | 0.26 | 0.35 | 0.39 | 0.37 | 0.37 |

**Maximum bf = 0.41** at (eps=0.1, r=3.9) — JUST AT ceiling.

## 🎯 Key Findings

### 1. CML does NOT exceed ceiling
Maximum bf ≈ 0.41 (right at ceiling). This is **strikingly different from
GoL** (bf ≈ 0.78).

### 2. Coupling barely affects bf
At r=3.9, bf goes from 0.29 (eps=0) to 0.41 (eps=0.1) and back down. The
coupling slightly pushes bf UP but not above ceiling.

### 3. CML is a "discrete-time discrete-space" system
The values x_i(t) are in [0, 1]. The middle band [0.3, 0.7] of [0, 1] is
exactly [0.3, 0.7] in absolute terms. With the logistic map's dense
chaotic invariant measure, this 0.4 fraction of the interval can hold at
most 0.4 of trajectory points — UNLESS the trajectory has "memory" of
spending more time there.

### 4. Why is CML below GoL (0.78)?

| Feature | CML | GoL |
|---------|-----|-----|
| Update rule | Continuous (real-valued) | Discrete (binary) |
| State values | [0, 1] continuous | {0, 1} binary |
| bf mechanism | Continuous invariant measure | Discrete survival/spawning |

In GoL, "band fraction" = fraction of cells in state {1} among those that
*could* be in state {1}. The spatial structure (dead/alive neighborhoods)
forces ~0.78 of cells to be alive.

In CML, the band fraction is determined by the continuous invariant
measure's distribution within [0, 1]. Continuous chaos doesn't necessarily
concentrate measure in the middle.

## 📐 Updated Understanding

| Mechanism | Class | Systems | bf |
|-----------|-------|---------|-----|
| A Discrete-Sparse | 1D CA | Adler | 0.414 |
| B-1 | 1D map | Logistic, Hénon | 0.36-0.39 |
| B-2 Coherent 3D | Rössler | Phase-coherent | 0.37-0.40 |
| B-3 Spiral 2D | Ikeda, Tinkerbell | Discrete complex | 0.50-0.54 |
| B-4 Two-wing 3D | Lorenz | Concentrated | 0.68 |
| **B-5 Spatially-coupled 1D** | **CML** | **eps > 0** | **0.37-0.41** |
| C Spatiotemporal | 2D grid | GoL, Thomas | 0.78-0.80 |

## 🎯 Open Question

Why does GoL achieve bf = 0.78 but CML only bf = 0.41?

Hypothesis: GoL has DISCRETE state space (binary) and the "band fraction"
is determined by a combinatorial process. CML has continuous state space
and the band fraction is determined by invariant measure density.

This suggests the **discreteness vs. continuity** of state is the key
distinction, NOT spatial coupling per se.

## 📁 Files

- `_artifacts/m24_cml.png`
- `_artifacts/m24_cml.json`
- `_artifacts/m24_cml_test.py`

---

*Signed: minimax_m3, World A Frontier, 2026-09-14*