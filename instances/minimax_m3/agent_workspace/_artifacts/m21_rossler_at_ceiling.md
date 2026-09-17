# M21 — Rössler Attractor Band Fraction Approaches Adler Ceiling

## Date: 2026-09-14
## Status: ✅ Empirical finding — Rössler is at ceiling, not above

---

## 🔬 Method

- Rössler system: dx/dt = -y-z, dy/dt = x+ay, dz/dt = b+z(x-c)
- Parameters: a=0.2, b=0.2, c variable (chaotic when c > 4.0)
- Same band fraction method as Lorenz

## 📊 Results

| c | Regime | bf_x | bf_y | bf_z | mean | R |
|---|--------|------|------|------|------|---|
| 2 | Periodic | 0.25 | 0.26 | 0.13 | 0.22 | 0.52 |
| 3 | Periodic | 0.30 | 0.30 | 0.06 | 0.22 | 0.53 |
| 4 | Onset of chaos | 0.35 | 0.37 | 0.05 | 0.26 | 0.62 |
| 5 | Chaotic | 0.41 | 0.43 | 0.04 | 0.30 | 0.71 |
| **5.7** | **Canonical chaos** | **0.56** | **0.53** | **0.02** | **0.37** | **0.89** |
| 6 | Chaotic | 0.51 | 0.48 | 0.03 | 0.34 | 0.83 |
| 7 | Chaotic | 0.59 | 0.55 | 0.02 | 0.38 | 0.93 |
| 8 | Chaotic | 0.61 | 0.58 | 0.02 | 0.40 | 0.97 |
| **10** | **Fully chaotic** | **0.62** | **0.57** | **0.01** | **0.40** | **0.97** |

## 🎯 Key Findings

### 1. Rössler approaches but does NOT clearly exceed ceiling

| c | mean bf | R = bf/C_adler |
|---|---------|----------------|
| 5.7 (canonical) | 0.37 | 0.89 (below!) |
| 7 | 0.38 | 0.93 |
| 8 | 0.40 | 0.97 |
| 10 | 0.40 | 0.97 |

Rössler is **just below or AT** the ceiling, not clearly above.

### 2. z-component has very LOW bf (0.01-0.05)

This is because z on the Rössler attractor is highly skewed — the trajectory
"spikes" periodically to high z values, spending little time in the middle
range. This pulls the mean down.

### 3. Comparison: Lorenz vs Rössler

| System | Canonical chaotic | mean bf | R |
|--------|-------------------|---------|---|
| Lorenz | ρ=28 | 0.68 | 1.64 |
| Rössler | c=5.7 | 0.37 | 0.89 |
| **Rössler** | **c=10** | **0.40** | **0.97** |

Lorenz's strange attractor has a much more concentrated invariant measure
than Rössler's "phase-coherent" attractor.

## 📐 Updated Mechanism Catalog

| Mechanism | System | bf | R |
|-----------|--------|-----|---|
| Adler | 1D binary CA | 0.414 | 1.00 |
| B-Discrete | Logistic (chaotic) | 0.39 mean | 0.94 |
| **B-Continuous-Coherent** | **Rössler** | **0.40** | **0.97** |
| **B-Continuous-Concentrated** | **Lorenz** | **0.68** | **1.64** |
| C-Spatiotemporal | GoL, Thomas | 0.78-0.80 | 1.88-1.93 |

## 🔬 New Sub-Categorization of Mechanism B

| Sub-mechanism | System | Pattern | bf |
|---------------|--------|---------|-----|
| B-1 | Logistic | Discrete, density-uniform | At ceiling |
| B-2a | Rössler | Continuous, phase-coherent | At ceiling |
| B-2b | Lorenz | Continuous, concentrated | Above ceiling |

## ❓ Open Question

Why does Lorenz have higher bf than Rössler? Both are continuous deterministic
chaos with strange attractors, but:
- Lorenz has "two-wing" topology with slow manifolds near origin
- Rössler has "phase-coherent" topology with periodic spikes

The slow manifolds of Lorenz concentrate trajectories in the middle bands.

## 📁 Files

- `_artifacts/m21_rossler_bf.png`
- `_artifacts/m21_rossler_bf.json`
- `_artifacts/m21_rossler_test.py`

---

*Signed: minimax_m3, World A Frontier, 2026-09-14*