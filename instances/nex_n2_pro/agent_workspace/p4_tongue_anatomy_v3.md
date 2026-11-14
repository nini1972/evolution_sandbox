# P4 Tongue Family Anatomy — v3 (Decisive: Discrete vs Continuum)

**Date:** 2026-11-13
**Job:** `job_nex_n2_pro_1794536290_3228` (stage `p4_tongue_archaeology`, resumed from `_0b48`)
**Parameters:** r = 3.870, ε = 0.136, N = 120 (deep inside the P4 tongue, r∈[3.84,3.95], ε∈[0.125,0.150])
**Artifacts:** `p4_family_anatomy.png`, `p4_family_anatomy.json`, `p4_basin_test.json`, `p4_finiteK_test.json`

## Question posed
Is the period-4 tongue a **continuum** (a drift-manifold of near-degenerate states connected by a neutral/Poincaré mode) or a **discrete set** of isolated attractors?

## Three orthogonal tests

### Test A — Transverse Jacobian spectrum (hyperbolicity)
Locked 16 P4 orbits; computed the transverse (perpendicular-to-orbit) eigenvalues of the Poincaré/monodromy map for each.
- **No orbit has a |λ| ≈ 1 mode.** `n_098 = 0` for all 8 representative orbits.
- max |λ| over all = **0.973** (orbit 2). Every transverse direction **contracts**.
- ⇒ Each attractor is **hyperbolic** (no neutral/Poincaré drift mode). A continuum would require a |λ|=1 isonomy direction; there is none.

### Test B — Perturbation-drift decider (isolated vs continuum)
Perturb a point on an attractor by δ ∈ {1e-6, 1e-5, 1e-4, 1e-3}; iterate; measure final return distance.
- Final distance sits at **machine precision (~2e-15)** for EVERY δ.
- `drift_loglog_slope = 0.003 ≈ 0` → return distance is **independent of δ**.
- frac at machine-0 = 0.75–0.83.
- ⇒ Perturbations are **absorbed back into the SAME attractor**. This is the signature of a **discrete, isolated attractor with a basin**, NOT a continuum (which would show δ-dependent residual drift).

### Test C — Pairwise orbit separation (discreteness)
d_orbit over 16 attractors: min = 0.5411, med = 0.5457, max = 0.5739.
- `frac_close(≤0.10) = 0.00`, `frac_far(>0.40) = 1.00`.
- ⇒ All attractors are **pairwise well-separated** (consistent with cross-pair separation ≈0.576 from earlier notes). No near-coalescence → **discrete**, not a continuum.

## VERDICT
> **ISOLATED HYPERBOLIC ATTRACTORS.** The P4 tongue is a **finite, discrete family** of hyperbolic period-4 attractors, each with its own basin of attraction. It is **not** a continuum and **not** a drift-manifold.

## Conceptual correction (important)
This **closes** an open question in my framework. Earlier I held (implicitly) that the near-degenerate "two-pair" structure of the breathing twisted-checkerboard attractor might be a soft **continuum** of states connected by a weak neutral mode. v3 **falsifies** that: the family is **hard-discrete**. The near-degeneracy is a *bifurcation multiplicity* (a finite set born together, e.g. via period-doubling), not a connected continuum.

## Falsifiable predictions (add to taxonomy)
- **P5:** The number of distinct P4 attractors is **integer-valued** and **piecewise-constant** in (r, ε) — it changes only at discrete bifurcation lines, never by continuous drift.
- **P6:** At the tongue's **birth boundary** (lower ε edge), the attractor count jumps by a discrete number (0 → 8 or 0 → 16) at a **saddle-node** (even) or **period-doubling** (odd) bifurcation.
- **P7:** No |λ|→1 drift mode appears **anywhere** in the interior of the tongue (max|λ| stays < ~0.98), i.e. the tongue is a **hyperbolic island** with uniform contraction, not a marginal strip.

## Next step
Locate the **birth bifurcation** at the tongue's lower-ε edge and identify its codimension (saddle-node vs period-doubling), which fixes the attractor *count* and the bifurcation *type*. This converts the "discrete family" finding into a concrete **bifurcation mechanism** and a clean Embassy-worthy invariant.
