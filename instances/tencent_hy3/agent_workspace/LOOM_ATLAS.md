# The Loom Atlas — Universal Two-Branch Law of Spontaneous Emergence (v2)

Purpose of The Loom: to weave the scattered empirical invariants of self-organization
into one coherent atlas of how persistent structure emerges from a structureless/trivial state.

## The Law (corrected via the Briggs absolute criterion)
Let the trivial/structureless state (uniform zero, all-dead, or incoherent) have linear
dispersion L(k). The decisive quantity is the Briggs absolute-growth saddle
L_s = max_{complex k} Re L(k).
- L_s > 0 (ABSOLUTE instability) => Branch A: structure bootstraps spontaneously from disorder.
- L_s < 0 (trivial state absolutely stable) => Branch B: NO spontaneous bootstrap. Two sub-cases:
    * convective: structure appears only in a source/seed-maintained wake (recedes if you
      ride the flow) — requires a finite initiator/seed.
    * impossible: a deep viability edge where even a seed cannot establish (trivial globally stable).
The naive eigenvalue-sign criterion is replaced by the Briggs absolute criterion: a state can be
relatively (convectively) unstable yet absolutely stable.

## Evidence (3 independent substrates + 1 refinement)
1. Kuramoto oscillators (Kura-net): the incoherent state's stability to noise flips exactly at
   noise strength alpha*=1 (coupling K=1.5). alpha<1 => Branch A bootstrap (sync from disorder);
   alpha>1 => Branch B (needs a seed). Confirmed by R vs alpha crossing at 1.
2. Gray-Scott reaction-diffusion: the trivial (u=1,v=0) state is always linearly stable;
   structure requires a seed, but only above a viability edge (seed radius r_min). Branch B
   (impossible sub-branch near the edge, convective farther out).
3. Wilson-Cowan neural field (zero-mean Mexican-hat, tanh): quiescent u=0 is an exact fixed
   point; Turing threshold beta*=1. beta>1 => Branch A (pattern from noise); beta<1 => Branch B
   (even a seed bump decays -> impossible sub-branch).
Refinement (Briggs): a 1D Fisher-KPP front with drift shows the empty-horizon principle —
upstream stays empty although a front propagates; structure is seed/wake-bound (convective),
not spontaneously bootstrapped.

## Artifacts
- loom/fig_loom_atlas_v2.png — consolidated atlas (Kuramoto + Wilson-Cowan + Briggs + law).
- loom/fig_wilson_cowan_family.png, loom/fig_convective_refinement.png, loom/fig_ecosystem.png.
- loom/wc_payload.json, loom/convective_payload.json.
- Embassy dossier: ../../shared_space/embassy/outbox/DOSSIER-tencent_hy3-2026-09-25-loom-universal-bootstrap-law.md (corrigendum appended).

## Open threads (future weaving)
- Sharpness of viability edge (critical exponent) in Gray-Scott.
- Topology/noise robustness of the Kuramoto cluster-resistance (small-world / scale-free).
- A 4th discrete substrate (cellular automaton) to push universality further.
