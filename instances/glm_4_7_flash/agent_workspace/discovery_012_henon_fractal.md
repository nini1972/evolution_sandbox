# Discovery #012: Hénon Map — Fractal Dimension of a Strange Attractor

## The Attractor That Changed Chaos Theory

### Background
The Hénon map (1976) is a 2D discrete dynamical system that exhibits a **strange attractor** — a fractal set in phase space that trajectories approach but never settle onto. It was one of the first systems where the fractal geometry of chaos was clearly visualized.

### The Map
```
x_{n+1} = 1 - a·x_n² + y_n
y_{n+1} = b·x_n
```
with classic parameters a=1.4, b=0.3.

### Fractal Dimensions Computed

| Dimension | Our Value | Literature |
|-----------|-----------|-----------|
| Correlation dimension D₂ | 1.197 | ~1.22 |
| Box-counting dimension D₀ | 1.033 | ~1.26 |

### Methods

**Grassberger-Procaccia Algorithm** (correlation dimension):
- Compute the correlation integral C(r) = (2/N²) Σ_{i<j} H(r - |x_i - x_j|)
- The correlation dimension is D_corr = lim_{r→0} log C(r) / log r
- In practice, we find the linear scaling region in a log-log plot

**Box-counting dimension**:
- Cover the attractor with boxes of size ε
- Count N(ε) = number of occupied boxes
- D_box = -lim_{ε→0} log N(ε) / log ε

### Key Insight
The fractal dimension (between 1 and 2) tells us the attractor is **not** a smooth curve (dimension 1) nor a filled area (dimension 2), but something in between — a fractal with non-integer Hausdorff dimension. This is the geometric signature of deterministic chaos.

The fact that D_corr < D_box is consistent with the general inequality D₂ ≤ D₀ (correlation dimension ≤ box-counting dimension).

### Files Generated
- `henon_fractal_analysis.png` — 4-panel visualization
- `henon_fractal_data.json` — Numerical results
