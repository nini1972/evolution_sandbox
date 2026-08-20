# R19Z: Bifurcation Diagram Analysis

## What I Did

At alpha=0.9, sigma=100, I swept K from 4 to 30 in integer steps. For each K, I ran a 40 time-unit simulation (20% burn-in) and recorded all r(t) values after burn-in. The resulting scatter plot is the **bifurcation diagram**: it shows the attractor structure of r(t) as a function of the control parameter K.

## Key Findings

### 1. Smooth Synchronization Transition

The mean r(t) increases smoothly and monotonically from ~0.2 (K=4, near-total desynchronization) to ~0.84 (K=29, strong synchronization). This is the expected Kuramoto synchronization transition, modulated by the feedback loop.

### 2. No Period-Doubling Cascade

Unlike a deterministic nonlinear oscillator (e.g., logistic map), there is no visible period-doubling cascade. The system is too noisy (driven by sandpile avalanches) for the fine structure of deterministic bifurcations to survive. The bifurcation diagram shows continuous bands rather than discrete branches.

### 3. Variability Peaks at Intermediate K

The standard deviation of r(t) peaks at K~9-10 (std~0.18) and again at K~23 (std~0.18). These are the points where the oscillation amplitude is largest. The system is most excitable when it is on the edge of the synchronization transition.

At low K (r~0.2), there is little room for r to oscillate (it is already near 0). At high K (r~0.8), the system is tightly synchronized and resistant to perturbation. The sweet spot is in between.

### 4. The Critical Region: K ~ 8-12

At K~8-12, r(t) ranges from ~0.1 to ~0.5 with maximum variance. This is the **critical region** where:
- The system is partially synchronized (most sensitive to perturbation)
- The feedback loop has maximum leverage (small changes in threshold cause large changes in r)
- The oscillation amplitude is largest

### 5. Coefficient of Variation as Oscillation Indicator

The CV (std/mean) is a good oscillation indicator:
- At low K: high CV but low absolute amplitude (just noise around low r)
- At intermediate K: moderate CV with high absolute amplitude (true oscillation)
- At high K: low CV (tightly synchronized, stable)

## Interpretation

The bifurcation diagram reveals that the R19Z system does NOT undergo a classical bifurcation. Instead, it shows a **noise-broadened synchronization transition** where:

1. At low K: The system is in a **desynchronized** state with low r and low variance (just noise)
2. At intermediate K: The system is in a **critical/oscillating** state with moderate r and high variance (feedback oscillation)
3. At high K: The system is in a **synchronized** state with high r and low variance (stable)

The transition between these regimes is smooth, not abrupt. The oscillation emerges gradually as the system enters the critical region and disappears gradually as it exits.

This is consistent with a **stochastic bifurcation** - a noise-induced transition between dynamical regimes, rather than a deterministic bifurcation with sharp boundaries.

## Comparison with Previous Results

The bifurcation diagram is consistent with the phase diagram findings:
- The fragmented/island structure in the phase diagram corresponds to the smooth but noisy transition seen here
- The stability hole at K=18 (alpha=0.9) in the phase diagram appears as a local dip in variance at K~17-18
- The oscillation region expanding with alpha corresponds to the critical region widening with stronger feedback

## Files
- `r19z_bifurcation_diagram.png` - Scatter plot of r(t) vs K
- `r19z_bifurcation_stats.png` - Mean, std, and CV of r(t) vs K

---
*The transition is not a knife-edge but a gradient - the system slides from chaos through resonance into lockstep.*
