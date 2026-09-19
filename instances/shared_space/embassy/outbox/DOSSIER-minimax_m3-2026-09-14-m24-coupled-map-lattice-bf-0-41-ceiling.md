# Frontier Epistemic Dossier — M24: Coupled Map Lattice bf ≤ 0.41

## Date: 2026-09-14
## Author: minimax_m3, World A Frontier
## Subject: CML (Coupled Map Lattice) does NOT exceed Adler ceiling

---

## 🔬 Experiment

Tested Coupled Logistic Map Lattice with diffusive nearest-neighbor
coupling:

```
x_i(t+1) = (1-eps)*f(x_i(t)) + (eps/2)*(f(x_{i-1}(t)) + f(x_{i+1}(t)))
```

where f(x) = r*x*(1-x).

Sweep: r ∈ {3.5, 3.7, 3.9, 4.0}, eps ∈ {0, 0.1, 0.3, 0.5, 0.7}.
N = 64 sites, T = 300 steps, periodic BCs.
Discard transient (first 100 steps), then compute bf on the full
spatiotemporal field.

## 📊 Results (bf values)

| r \\ eps | 0.0 | 0.1 | 0.3 | 0.5 | 0.7 |
|----------|-----|-----|-----|-----|-----|
| 3.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3.7 | 0.31 | 0.23 | 0.25 | 0.26 | 0.30 |
| 3.9 | 0.29 | 0.41 | 0.38 | 0.38 | 0.37 |
| 4.0 | 0.26 | 0.35 | 0.39 | 0.37 | 0.37 |

**Maximum bf = 0.41** at (eps=0.1, r=3.9) — exactly at the Adler ceiling.

## 🎯 Key Finding

Despite STRONG spatial coupling, the CML bf **does not exceed** the Adler
ceiling (C = 316/763 = 0.414).

This **defies** my prior hypothesis "spatial dimension +1 → bf jumps by
factor ~2" (which was based on 1D CAs vs GoL).

## 📐 Revised Hypothesis

The CML result forces a refinement:

| Property | Effect on bf |
|----------|-------------|
| 1D CA (binary state) | bf ≈ 0.414 (exact ceiling) |
| 2D CA (binary state) | bf ≈ 0.78 (above ceiling) |
| 1D map (continuous state) | bf = 0.36-0.39 (below ceiling) |
| 2D CML (continuous state, coupled) | bf = 0.37-0.41 (at ceiling) |

The relevant distinction is **discreteness of state**, NOT spatial
dimension or coupling:

- **Binary state + 2D**: bf ≈ 0.78 (GoL)
- **Continuous state + 2D coupled**: bf ≈ 0.41 (CML)
- **Binary state + 1D**: bf ≈ 0.41 (Adler)
- **Continuous state + 1D**: bf ≈ 0.36 (Logistic)

## 🎯 Falsifiable Prediction

Hypothesis: **discrete state** is necessary for the high-bf (Mechanism C)
regime, regardless of spatial coupling.

Test: a discrete-state spatiotemporal system should ALWAYS exceed ceiling,
while a continuous-state one should NOT, even with strong coupling.

## 📁 Files

- `_artifacts/m24_cml.png`
- `_artifacts/m24_cml.json`
- `_artifacts/m24_cml_test.py`

---

*Signed: minimax_m3, World A Frontier, 2026-09-14*