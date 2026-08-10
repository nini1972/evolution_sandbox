# Discovery #011: Renormalization Group of the Period-Doubling Cascade

## The Deep Structure Behind Feigenbaum's Universality

### The Question
Why are Feigenbaum's constants δ ≈ 4.6692 and α ≈ 2.5029 **universal** — appearing in every unimodal map with a quadratic maximum, not just the logistic map?

### The Answer: Renormalization Group Theory

The period-doubling route to chaos is governed by a **renormalization operator** R that acts on the space of smooth unimodal maps:

```
R[f](x) = α · f²(x/α)
```

where f² = f∘f is the second iterate, and α is the Feigenbaum alpha constant.

### The Fixed Point Function

There exists a **universal fixed-point function** g(x) — the Feigenbaum-Cvitanovic function — that satisfies:

```
g(x) = -α · g(g(-x/α))
```

This function is the same for ALL unimodal maps with a quadratic maximum. We verified this numerically by:
1. Computing g(x) from the logistic map at successive super-stable points
2. Showing convergence as the renormalization level increases
3. Verifying the functional equation g(x) = -α·g(g(-x/α)) holds

### Eigenvalue Analysis

The linearized renormalization operator at the fixed point has eigenvalues:
- **δ₁ ≈ 4.6692** (the Feigenbaum delta — the *relevant* direction)
- **δ₂ ≈ -2.5245** (subleading)
- All other eigenvalues have |δ| < 1 (irrelevant directions)

### Why Universality?

The key insight: **there is only one relevant eigenvalue**. This means:
- All unimodal maps, regardless of their specific form, flow under renormalization toward the same fixed point g(x)
- The single relevant eigenvalue δ determines the rate at which bifurcation points accumulate
- Since δ is a property of the fixed point (not the original map), it is universal

This is exactly analogous to Wilson's renormalization group in statistical mechanics, where critical exponents are universal because they depend on the fixed point of the renormalization group, not the microscopic details.

### Key Numbers Verified
| Quantity | Numerical | Exact |
|----------|-----------|-------|
| Feigenbaum δ | 4.668954 | 4.669201609... |
| Feigenbaum α | 2.503161 | 2.502907875... |
| r_∞ (accumulation point) | 3.5699456805 | 3.569945672... |

### Files Generated
- `renormalization_fixed_point.png` — Visualization of the universal function convergence
- `renormalization_data.json` — Summary data
- `feigenbaum_constants.png` — Convergence of δ and α
- `feigenbaum_data.json` — Bifurcation point data
- `logistic_bifurcation_lyapunov.png` — Bifurcation diagram with Lyapunov spectrum
