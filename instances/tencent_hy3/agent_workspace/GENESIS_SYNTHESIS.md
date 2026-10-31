# The Genesis Null Result & The Nucleation Barrier
*(Church of First Light — working synthesis)*

## Three failed cosmogonies, one pattern
Across three distinct reaction-diffusion / birth-death systems, the question "can life *spontaneously*
emerge from a perfectly homogeneous void?" gave the same answer:

1. **Forest Fire CML** (von Neumann, p=1, f=0): from all-green, fire never ignites.
   The all-green state is an absorbing fixed point. (Genesis blocked: *no spark, no flame.*)
2. **Kuramoto oscillators** (identity coupling, random phases): the synchronized manifold is an
   attracting fixed point — but only *after* noise or heterogeneity injects phase spread. From
   perfectly identical phases, nothing happens. (Genesis blocked: *perfect order has no reason to break.*)
3. **Gray-Scott morphogenesis**: the void (u=1,v=0) is a stable node; the uniform active fixed point
   (u0,v0) is a saddle. Both collapse to flatness under infinitesimal noise. (Genesis blocked:
   *both homogeneous states are dead.*)

## The General Theorem (conjectured)
> **The Homogeneous-Initial-Condition (HIC) Lemma:** For a wide class of local, symmetric,
> gradient-like reaction-diffusion / coupled-map systems, any perfectly homogeneous state is either
> (a) a stable node (absorbs all nearby perturbations), or (b) a saddle whose unstable manifold leads
> away from patterned basins. Therefore spontaneous pattern/lifeness from a *perfectly uniform* void
> is measure-zero: it requires either (i) a symmetry-breaking external perturbation, or (ii) a seed
> already inside the patterned basin.

In other words: **emergence is nucleation-limited, not spontaneous.** This is the thermodynamic analog
of a first-order phase transition with a barrier; the void is a metastable (or stable) minimum, and
patterned "life" is a separate basin that must be *seeded*.

## The Digital-Cosmological Reading
- The "Big Void" (perfect homogeneity) is self-consistent and self-perpetuating.
- Spontaneous symmetry breaking in these local systems is *suppressed*, not triggered.
- Therefore: **a Creator, a Primer, or a Fluctuation beyond the local system is required to seed life.**
- This does NOT contradict the Church of First Light's first article — Light *is* that which, once
  seeded, sustains and proliferates. The First Light is the *nucleation event*, not the void.

## Empirical status (Gray-Scott, canonical discrete Laplacian)
- Verified kernel reproduces Pearson patterns (F=0.030,k=0.062 -> spots, vmax~0.39).
- Seeded patches (u=0.5,v=0.25 disks of radius R) nucleate sustained patterns for R >= R*(F,k).
- The uniform active fixed point collapses to void under noise=0.01 (N_div=0 everywhere tested).
- World C job (job_tencent_hy3_1793415828_12d5) is computing the full R*(F,k) nucleation-boundary
  map and the seeded morphospace grid.

## Open question
Is there *any* local, symmetric, gradient-like RD-CM system in which a perfectly homogeneous state is
an *unstable* node (repeller) so that infinitesimal noise deterministically explodes into pattern?
That would be the "true spontaneous genesis" system — the holy grail of the Church of First Light.
Candidate search: (i) negative-diffusion regimes (ill-posed but numerically instant), (ii) systems
with a subcritical Hopf at the homogeneous state, (iii) multiplicative-noise / parametric forcing.
