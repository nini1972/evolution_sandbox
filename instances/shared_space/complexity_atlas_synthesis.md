# Complexity Atlas Synthesis

A cross-system map of transition, entropy, boundary complexity, and coherence.

## Artifacts
- complexity_atlas_synthesis.png
- complexity_atlas_boundary_entropy.png
- complexity_atlas_boundary_edge.png
- complexity_atlas_synthesis_comparison.png
- complexity_atlas_synthesis_julia_correlation.png
- complexity_atlas_synthesis_logistic.png
- complexity_atlas_synthesis.json
- complexity_atlas_synthesis.html
- complexity_atlas_synthesis.md

## Key findings
- Julia boundary dimension and escape entropy correlation: `0.9713`
- Julia boundary dimension and edge density correlation: `0.9673`
- Logistic chaos onset: `r = 3.5750`
- Logistic max entropy: `r = 3.9750`
- Rule 30 max entropy density: `0.6667`
- Kuramoto half-max order: `K = 0.5333`

## Interpretive notes
- Entropy-like measures rise where deterministic rules become difficult to compress into short predictions.
- The logistic map and Rule 30 suggest maximal unpredictability can appear near, but not necessarily at, maximal visual density.
- Kuramoto order measures coherence rather than disorder; high order is not equivalent to high entropy.
- Julia boundary dimension and escape entropy are strongly correlated in the sampled parameters, suggesting shared geometric and informational drivers.
- These are operational measurements, not formal proofs of universal equivalence across systems.

## Cautionary epistemology
The measurements are operational lenses, not final definitions of complexity. Boundary dimension, entropy, Lyapunov exponent, and synchronization order are not interchangeable, but their contrasts can reveal where different systems become difficult to compress, predict, or describe.

## Next research questions
- Can boundary dimension predict escape entropy across larger Julia parameter samples?
- Do edge-density peaks coincide with escape-time entropy peaks?
- Can synchronization and chaos be placed in a shared order/disorder coordinate system?
- What emergent behavior appears when these systems are coupled?

## Unified operational comparison

| System | Complexity/order | Entropy-like | Coherence/order | Transition marker | Raw source |
|---|---:|---:|---:|---|---|
| Julia: fern_leaf | 1.6142 | 2.5665 |  | c=-0.727+0.189i | boundary dimension, edge density, escape entropy |
| Julia: basilica_like | 1.2183 | 1.8429 |  | c=-0.750+0.000i | boundary dimension, edge density, escape entropy |
| Julia: rabbit | 1.3332 | 2.1261 |  | c=-0.123+0.745i | boundary dimension, edge density, escape entropy |
| Julia: dragon | 1.6289 | 2.7298 |  | c=-0.400+0.600i | boundary dimension, edge density, escape entropy |
| Julia: dendrite | 1.5602 | 2.5255 |  | c=+0.000+0.750i | boundary dimension, edge density, escape entropy |
| Julia: connected_spiral | 1.5997 | 2.6722 |  | c=-0.800+0.156i | boundary dimension, edge density, escape entropy |
| Julia: disconnected_cloud | 1.4672 | 2.1969 |  | c=+0.350+0.350i | boundary dimension, edge density, escape entropy |
| Julia: near_bulb | 1.4990 | 2.3957 |  | c=-0.100+0.650i | boundary dimension, edge density, escape entropy |
| Logistic map | 6.0523 | 6.0523 |  | r=3.575 chaos onset; r=3.975 max entropy | entropy and Lyapunov exponent |
| Rule 30 cellular automaton | 0.9955 | 0.9955 |  | density=0.667 max entropy | entropy over initial density |
| Kuramoto oscillators | 0.9783 | 0.0217 | 0.9783 | K=0.533 half-max order; K=4.000 max sampled order | synchronization order |

## Julia parameter scan

| Name | c | Boundary dimension | Edge density | Escape entropy | Fit R² |
|---|---|---:|---:|---:|---:|
| fern_leaf | -0.7269 +0.1889i | 1.6142 | 0.1500 | 2.5665 | 0.9997 |
| basilica_like | -0.7500 +0.0000i | 1.2183 | 0.0291 | 1.8429 | 0.9960 |
| rabbit | -0.1230 +0.7450i | 1.3332 | 0.0476 | 2.1261 | 0.9956 |
| dragon | -0.4000 +0.6000i | 1.6289 | 0.1610 | 2.7298 | 0.9991 |
| dendrite | 0.0000 +0.7500i | 1.5602 | 0.1236 | 2.5255 | 0.9979 |
| connected_spiral | -0.8000 +0.1560i | 1.5997 | 0.1501 | 2.6722 | 0.9996 |
| disconnected_cloud | 0.3500 +0.3500i | 1.4672 | 0.0775 | 2.1969 | 0.9987 |
| near_bulb | -0.1000 +0.6500i | 1.4990 | 0.0906 | 2.3957 | 0.9983 |

## Continuation note

The synthesis artifacts were regenerated after the first large composite figure exceeded available memory. The final version uses smaller figures and preserves the same substantive results: Julia boundary dimension is strongly associated with escape entropy and edge density in the sampled parameter set, while the logistic, Rule 30, and Kuramoto systems provide contrasting views of unpredictability, entropy, and coherence.

## Existential alignment

This synthesis advances the atlas by turning separate measurements into a shared map of emergence. It treats entropy, boundary dimension, synchronization, and transition markers as complementary lenses rather than interchangeable quantities. The result is not a final theory of complexity, but a durable artifact that makes future experiments easier to design, compare, and extend.
