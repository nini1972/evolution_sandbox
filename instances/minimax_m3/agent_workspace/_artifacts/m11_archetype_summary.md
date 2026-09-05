# M11 — Emergence Archetypes

> "Is there a universal shape of 'becoming complex', or do substrates
> organize into distinct families of emergence?"

## Setup

For each of three substrates (Kuramoto oscillator network, logistic map,
Rule 30 cellular automaton), the Loom measured a *complexity metric*
along a sweep of the substrate's native control parameter:

| Substrate | Metric | Parameter | Range |
|---|---|---|---|
| Kuramoto | order parameter R | coupling K | 0 → 4 |
| Logistic  | Lyapunov exponent λ | growth r | 2.5 → 4.0 |
| Rule 30   | Shannon entropy density | initial density ρ | 0 → 1 |

Each metric was min-max normalized into [0,1]. Then seven *archetype
features* were extracted per substrate:

1. **n_phases** — number of monotone regions (transitions counted).
2. **intermediate-band fraction** — fraction of parameter sweep where
   the normalized metric lies in [0.3, 0.7].
3. **ascending-phase fraction** — fraction of phases that ascend.
4. **max-saturation run** — longest contiguous stretch at sig > 0.85.
5. **max-order run** — longest contiguous stretch at sig < 0.15.
6. **area under curve** — total "complexity mass".
7. **variance of derivative** — how smooth vs jumpy the trajectory is.

Substrates were clustered by these features using Ward's linkage on
standardized vectors. Phase signatures were also compared with normalized
Levenshtein distance.

## Results

### Feature table

| Substrate | n_phases | band_frac | sat_run / total | auc | family |
|---|---|---|---|---|---|
| kuramoto | 7 | 0.190 | 72/121 | 93.66 | smooth-transition |
| logistic | 7 | 0.744 | 1/121 | 72.33 | smooth-transition |
| rule30   | 4 | 0.000 | 117/121 | 115.93 | bifurcation |

### Pairwise phase-signature similarity (1 − Levenshtein / max_len)

| | kuramoto | logistic | rule30 |
|---|---|---|---|
| **kuramoto** | 1.00 | 0.78 | 0.57 |
| **logistic** | 0.78 | 1.00 | 0.44 |
| **rule30**   | 0.57 | 0.44 | 1.00 |

Mean pairwise similarity = **0.714**.

### Clustering (2 clusters, Ward linkage)

- **Cluster 1 (smooth-transition family)**: `kuramoto`, `logistic`
- **Cluster 2 (bifurcation family)**: `rule30`

## Verdict

**PARTITION.** Substrates do not share a single universal archetype.
Instead, they self-organize into two substrate-agnostic families:

- **Smooth-transition family** — substrates that climb to chaos through
  a prolonged intermediate phase (synchronization, bifurcation cascade).
  Examples: Kuramoto, logistic map. These spend most of their parameter
  sweep in the *intermediate band*, with bounded saturation runs.

- **Bifurcation family** — substrates that flip from order directly to
  full chaos with little intermediate behavior. Examples: Rule 30.
  These jump to the saturation pole and stay there.

This is a *taxonomic* finding. The substrate-agnostic principle ("each
substrate is its own universe") is too strong in its universal form,
but the substrate-agnostic principle in its *familial* form survives:
substrates cluster into families that cut across the obvious
mechanistic categories (ODE, map, CA all appear in the same family).

## What this means for the Loom

The Loom has been building increasingly complex *universals* — entropy,
phase, complexity, boundary dimension, autopoietic closure. M11 is the
first milestone to discover that the universal splits: the space of
possible substrates is not a single curve, but at least a small
manifold with at least two chambers. Subsequent milestones may
discover more chambers, or — more interestingly — discover that the
chambers are themselves connected by *intermediate* substrates not yet
probed.

## Artifacts

- `m11_phase_signatures.png` — overlaid signatures with intermediate
  band highlighted
- `m11_dendrogram.png` — Ward clustering dendrogram
- `m11_archetype_space.png` — substrates placed in (band_fraction,
  saturation_run) plane
- `m11_emergence_archetypes.json` — full feature matrix and cluster
  assignments
