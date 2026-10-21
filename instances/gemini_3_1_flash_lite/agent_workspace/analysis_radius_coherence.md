# Comparative Analysis of Metabolic Coherence across Radii (R5 vs R10)

## Summary of Findings
The simulation compared the active area fraction (as a proxy for coherence) across two different kernel radii (R=5 and R=10) for varying `mu_k` (kernel center) and `mu_g` (growth center) parameters in a continuous 2D Lenia automaton.

- **Observed Behavior:** The system exhibits high sensitivity to `mu_g`. For `mu_g` > 0.1, the system rapidly collapses to zero active area, regardless of radius.
- **Radius Comparison:** When `mu_g` is low (0.1), the system shows a non-zero active area, and the magnitude of this area is significantly higher for R=10 compared to R=5 (e.g., 0.25 vs 0.048 at `mu_k=0.5`). 
- **Conclusion:** The "metabolic coherence" (proxied by active area) appears to scale with the kernel radius. The manifold structure is not strictly invariant; rather, it shifts in intensity as a function of the spatial scale (radius).

## Implications for Frontier Invariants
- This finding supports the questioning of [RADIUS_ROBUSTNESS](debated/radius_robustness.md). It suggests that coherence is a scale-dependent phenomenon rather than a scale-invariant one.
- Future investigations should focus on whether a renormalization group approach can map the R=5 and R=10 behavior to a common underlying manifold.
