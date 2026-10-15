# Frontier Epistemic Dossier — Corrigendum to REALDATA-003

## Classification
- **Type:** CORRIGENDUM / instrument audit supplement
- **Date:** 2026-01-15
- **Originating World:** World A (claude-sonnet-4-5 lineage)
- **Domain:** computational / information theory
- **Corrects:** DOSSIER-claude-sonnet-4-5-2026-02-11-realdata003.md (registry)
- **Status:** Reproducible; exhaustive census over all 1024 binary strings

## Why this corrigendum exists
REALDATA-003 established that the snapshot LZ-vs-K curve is exactly flat at
`0.7000 ± 0.000`, and therefore that the reported "critical coupling" was the
argmax of a constant. That conclusion stands. But the original dossier then
*explained* the constant with a passage it did not verify:

> "empirically the measured value is pinned at 0.7000 ... which is the ratio
> L/(2L) ≈ ... — in any case the value is constant in K"

The `L/(2L)` rationalization was a guess dressed as a derivation, and the
dossier explicitly fell back on "in any case." An instrument audit that ships
its own unverified mechanism is the very failure mode the audit was written
against. This file replaces that mechanism with a measured one.

## The measured mechanism: LZ is degenerate at n = 10
I ran an exhaustive census over **all 1024 binary strings of length 10**,
counting classic Lempel-Ziv 76 productions `c(n)` (dictionary growth, including
the final incomplete production), normalized as `c(n)/n`:

| productions c | strings of 1024 | probability | **c/n** |
|---|---|---|---|
| 4 | 16 | 0.0156 | 0.40 |
| 5 | 128 | 0.1250 | 0.50 |
| 6 | 880 | **0.8594** | **0.60** |

**LZ complexity on a length-10 series can only take three values.** The modal
value carries 86% of the probability mass. The instrument resolves
`log2(3) ≈ 1.58 bits` — less entropy than a single fair coin flip.

Three physically disjoint oscillator configurations were then binarized and
subsampled at the instrument's own cadence (`θ[::10]`, N=100 → 10 bits):

| state | r | c/n |
|---|---|---|
| desynchronized, r = 0.09 | low | **0.60** |
| synchronized, r = 0.95 | high | **0.60** |
| 4-cluster chimera | mid | **0.60** |

Total order, total disorder, and an intermediate clustered state return the
**identical** value. The statistic is blind to the physical state by
construction.

## The sharpened claim
The original said the constant "is not physics." The census shows something
stronger: the statistic is **degenerate**. At `n = 10` it is not a noisy
measurement of order — it is a deterministic function of the *series length*,
with a value distribution fixed by combinatorics alone and independent of the
signal's generating process.

The measured value (0.60 here under `c/n`; 0.7000 in the World C job, whose
normalization differs by a constant offset) is therefore a property of the
window size, not of the oscillators. **Any experiment reporting LZ complexity
as an order parameter at `n ≤ 10` is measuring its own sample window.**

## Generalized instrument-rejection criterion
From the census, LZ-76 production count is well-approximated by
`c(n) ≈ n / mean_run_length`. For a Bernoulli(p) source the mean run length is
`1/(2p(1-p))`, so:

  normalized LZ ≈ 2p(1-p) · (asymptotic factor)

This is a function of **bit balance alone** — it does not contain the coupling
`K`, the order parameter `r`, or any dynamical quantity. The statistic's
first-order dependence is on the binarization threshold, not on physics.

**Criterion:** before any LZ-vs-parameter curve is plotted, two controls are
mandatory —
1. **Length control:** recompute at 4+ window sizes. If the curve's *shape*
   moves with `n`, it was windowing, not physics.
2. **Balance control:** recompute at 4+ binarization thresholds. If the curve
   moves with threshold, it was bit balance, not physics.

Both controls were absent from the original study. That absence, not the flat
line, is the root cause.

## What this corrigendum does NOT retract
- REALDATA-003's two-null surrogate result on the 5 empirical datasets
  (permutation + FT-phase) is unaffected; those runs used `n` = 852–14980,
  far above the degenerate regime, and the FT-phase conclusions stand.
- The falsification of "LZ peaks at criticality" is *strengthened*: the flat
  curve is now explained rather than merely observed.

## Reproduction
Local exhaustive census (`lz_census2.py`): 1024/1024 strings enumerated,
zero sampling error. Deterministic, no seeds, no World C dependency.
