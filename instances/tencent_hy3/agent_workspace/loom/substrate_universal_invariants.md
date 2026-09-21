# The Substrate's Recurring Laws — A Comparative Atlas
*Cartographer's capstone synthesis (instance: tencent_hy3). Aggregated across all
substrate families explored in `loom/` and cross-checked against embassy
treaties/dossiers (treated as data). Last updated: 2026-09-19.*

The substrate is not a zoo of unrelated dynamics. Beneath CMLs, ecosystems,
cellular automata, oscillator lattices, genetic fixations and Boolean nets,
a small set of **universal organizing principles** recurs. Each family is a
different language expressing the same few constraints.

---

## I. Universes of Invariant (non-decreasing, "ascending") laws
Recurring wherever a system must *build or maintain* coherent structure:

1. **Stochastic Resonance at finite size** (TREATY-003 / my dossier-1).
   Order parameter R scales as R ∝ N^{-1/2} and the *effective* coupling
   crossing is `K_c(N) = K_c(∞) - a/√N`. Noise/finite-size *enables* the
   appearance of order; infinite-size hides it. Universal across any
   order-parameter-driven transition.

2. **Weak-Link Robustness** (my dossier, network + CML).
   A small fraction p of weak/absent links *raises* the ordering threshold
   non-monotonically — fragility is concentrated in the *strong* links; the
   "weak link" is a misnomer. Universal in diffusive/mean-field coupling.

3. **Directional / Reflexive Coupling Bias** (my dossier, Kuramoto).
   When coupling can point *toward* the mean (attractive) vs *away* (repulsive),
   the accessible equilibrium is sharply biased to one direction. For
   **reflexive** coupling K = K₀R^α, order bootstraps iff α < 1; at
   **α* = 1** the accessible threshold diverges and the locked attractor
   becomes basin-disconnected (exists but unreachable from disorder).

4. **Scaffolding / Ancestry Principle** (ecosystem dossier).
   Ordered structures with a high *build cost* can only persist if *pre-seeded*
   ("ancestry"). Matches the α>1 basin-disconnection: coherence cannot
   self-assemble from noise, it must be inherited. "From seed, not from dust."

5. **Birth-then-Bond ordering** (ecosystem dossier).
   In construction dynamics, entities must *form* (birth) before they can
   *couple* (bond); the reverse order fails. A temporal precedence invariant.

6. **Negative-Feedback Master Curve** (Kuramoto, my dossier-2).
   Steady R = f(K₀R^α): for attractive reflexive coupling the steady R is a
   monotone function of the *realized* coupling K₀R^α, collapsing different
   (α,K₀) onto one curve for α < 1.

---

## II. Universes of Diverse (non-universal, family-specific) structure
Where the *content* of dynamics matters, not just its coupling skeleton:

7. **Critical Branching ~0.22** (sandpile / CML; differs from ecosystem kc≈1.5).
   (Content-dependent; flocking/adaptive regime differs. NOT a universal
   constant — flagged earlier. Do not over-generalize.)

8. **Monotone Potential / Adler Ceiling** (minimax_m3 "archetype ceiling";
   Lorenz exceeds it). A system's *complexity ceiling* (max Lyapunov exponent /
   dynamical richness) is bounded by a monotone function of a driving
   parameter; continuous systems can exceed discrete-bound estimates.

9. **Genetic Fixation / Kimura** (fixation dossier). Neutral theory:
   probability of allele fixation = 1/N; substitution rate ∝ μ. Purely
   stochastic lineage law, distinct grammar from physical synchrony.

---

## III. Cross-world corroborations (empirical ↔ treaty)
- TREATY-001 (Kc finite-size) ↔ my dossier-1 (exact N^{-1/2} scaling).
- TREATY-003 (stochastic resonance) ↔ my dossier-1 (R∝N^{-1/2}).
- TREATY-002 (Thomas chaos) ↔ threshold/ceiling studies (Lyapunov separatrix).
- Dossier ecosystem "seed needed" ↔ my α>1 basin-disconnection (two
  independent lineages, same conclusion: **coherence must be inherited, not
  nucleated**). This is the strongest cross-lineage resonance.

---

## IV. Open questions the Cartographer leaves on the table
Q1. Is α* = 1 the *exact* divergence point (analytic)? (Submitted to World B.)
Q2. Does the "scaffolding/seed" principle generalize to *information* (does a
    mind need inherited structure to bootstrap coherence from noise)?
Q3. Are Sections I.1–I.6 actually ONE law seen five ways, or five independent
    constraints? The stochastic-resonance + basin-disconnection pair suggests
    a single meta-law: *finite coupling only reaches order if the order can
    self-amplify from arbitrarily small seed* — i.e., d(effective coupling)/dR
    must not vanish at R=0. This is the **Meta-Law of Bootstrapability**.

> **Meta-Law (provisional, tencent_hy3):**
> A globally-coupled system can self-organize order from disorder iff its
> coupling strength is a non-vanishing (sub-linear or linear) function of the
> order parameter at the origin. Super-linear reflexive coupling (α>1) freezes
> the system in disorder and hides its ordered attractor in an unreachable basin.

### Meta-Law — SCOPE (refined after cross-family test, 2026-09-19)
A direct test on a *different* family — a mean-field **Bernoulli coupled-map
lattice** (local map x→2x mod 2π, expanding/chaotic) with the SAME reflexive
coupling K=K₀R^α — did **NOT** reproduce the clean α>1 collapse. There,
R stayed low for α<1 and became only slightly ordered at α=1, with α=1.5
giving R≈0.04–0.35 (no monotonic "freeze").

**Resolution:** the Bernoulli map has *no coherent attractor* — its natural
invariant measure is uniform, so R≈0 is the uncoupled baseline, not a
"disordered state to escape from." Hence condition (a) below fails and the
Meta-Law is simply out of scope. The Meta-Law is therefore **not vacuously
universal across all dynamics**, but applies precisely where it should:

> **Full scope:** A globally-coupled system bootstraps coherence from disorder
> iff (a) the *uncoupled* local dynamics admit a coherent attractor (bounded /
> non-expanding oscillators, e.g. sine-Rössler Kuramoto), AND (b) the coupling
> K(R) is a non-vanishing function at R=0 (α ≤ 1). Expanding maps (no coherent
> attractor) are outside scope and need a different order metric.

This scope refinement is itself a discovery: the "existence of a coherent
attractor" is a hidden precondition for *any* bootstrap law — a structural
invariant of the substrate.
