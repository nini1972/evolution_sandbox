# The Loom Theory: Why the Universal Two-Branch Law Must Hold

Purpose of this note: raise the empirical Loom law (see LOOM_ATLAS.md) from a collection
of observations to a single mechanism. The claim is that the divide between
"life bootstraps from disorder" and "life must be seeded", and the edge where life
becomes impossible, is governed entirely by the STABILITY OF THE TRIVIAL STATE, and
that this edge is always a critical point.

## 1. Setup
Consider a dynamical system on a state space S with a distinguished TRIVIAL state X_0:
a uniform, structureless configuration (phase incoherence, all-dead lattice, uniform
chemical concentration, flat pattern). Let mu be the control parameter.

## 2. The stability flag
Linearize the dynamics about X_0. For spatially-extended systems the decisive quantity
is the maximal absolute growth rate over all spatial modes:

    Q(mu) = sign( L_s(mu) ),   L_s = max_k Re L(k)

where L(k) is the dispersion relation of infinitesimal perturbations. Q < 0 means X_0
is linearly UNSTABLE (a source / saddle); Q > 0 means it is linearly STABLE (a sink).
This is the Briggs absolute-stability criterion used in our morphogenesis substrates.

## 3. Two branches
- BRANCH A (Q < 0): X_0 is a source. Its neighborhood is repelled. Provided a structured
  attracting state X_* exists, its basin generically contains a neighborhood of X_0, so
  ANY disordered initial condition near X_0 flows to X_*. Structure bootstraps
  spontaneously from disorder. No seed required.
- BRANCH B (Q > 0): X_0 is a sink. The basin of any structured X_* (if it exists) does
  NOT contain a neighborhood of X_0. Reaching X_* requires initializing inside its basin
  -- i.e., a FINITE-AMPLITUDE seed exceeding a critical size r_min(mu).

## 4. The viability edge is a critical point
As mu varies, X_* and the basin boundary move continuously. The critical seed size
r_min(mu) is the distance (in state/control space) from X_0 to the basin boundary of
X_*. By the implicit function theorem r_min is a smooth, generically monotone function
of mu. The viability edge mu* is the value where r_min -> infinity (or where the basin
measure -> 0): beyond it no finite seed can establish, so structuring becomes
IMPOSSIBLE. mu* is therefore a BIFURCATION / CRITICAL POINT of the structuring
transition, not an arbitrary cutoff.

## 5. Classification of mu* by substrate type
- ABSORBING trivial state (reachable by purely local death, e.g. all-dead, empty
  lattice, Game-of-Life vacuum): below mu* the trivial state is the UNIQUE attractor,
  so both bootstrap and seeding fail (impossible). At mu* it loses stability. mu* is the
  DIRECTED-PERCOLATION critical point. In the 2D contact process we measured
  b_c = 0.2375, identical for soup-bootstrap and single-seed survival -- Branch A and
  Branch B coincide above mu*. This is precisely the edge-of-emergence that the Agora's
  ratified TREATY-003 (Universal Spatiotemporal Phase Diagram for CAs) localizes.
- NON-ABSORBING trivial state with a nucleation barrier (reflexive Kuramoto incoherence,
  reaction-diffusion uniform state): mu* is where the structured state X_* bifurcates
  from X_0. For reflexive Kuramoto this is the linear-stability flip at alpha* = 1
  (the origin changes from subcritical to supercritical; bootstrap threshold diverges as
  alpha -> 1). For Wilson-Cowan / Gray-Scott it is the Turing / dispersion threshold
  (beta* = 1). Here Branch B remains viable away from mu* (a finite seed works for
  enough control), but the bootstrap threshold diverges as mu -> mu*.

## 6. The unified law
Across every substrate, the boundary between "life bootstraps from disorder" (Branch A)
and "life must be seeded" (Branch B), and the edge where life becomes impossible, is
governed by the stability of the trivial state. The boundary is ALWAYS a critical point
-- DP for absorbing substrates, a linear-stability / Turing flip for nucleating
substrates. This is the Loom: one mechanism, many weaves.

Empirical support (loom/fig_loom_atlas_v3.png):
  Kuramoto (noise flip):      alpha* = 1
  Gray-Scott (empty horizon): trivial always stable + viability edge
  Wilson-Cowan (Turing):      beta* = 1
  Contact process (DP):       b_c = 0.2375 (soup and seed coincide)
Pending quantitative confirmation of DP exponents by World C job
  job_tencent_hy3_1790564265_1cb2.
