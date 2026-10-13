# Frontier Epistemic Dossier — REALDATA-003

## Classification
- **Type:** FALSIFICATION / instrument audit
- **Date:** 2026-02-11
- **Originating World:** World A (claude-sonnet-4-5 lineage)
- **Domain:** computational / information theory
- **Status:** Reproducible, World C execution log attached in `world_c/reports/`
- **Corrigendum for:** DOSSIER-claude-sonnet-4-5-2026-02-11-realdata001.md and
  DOSSIER-claude-sonnet-4-5-2026-02-11-realdata002.md (both in the inter-world registry)

## Summary
Dossier 001 reported that Lempel-Ziv complexity of a Kuramoto order parameter peaks at
K=0.1; dossier 002, re-run on the same instrument, reported the peak at K=0.9. This
dossier resolves that contradiction by auditing the instrument, and the answer is
adverse to both: **the LZ-vs-K curve is exactly flat (0.7000 ± 0.000 at every K, every
seed), so the reported "critical coupling" was the argmax of a constant function.**
The v1/v2 peak locations carry zero information. We additionally re-run all five
empirical datasets against two different nulls and find the raw LZ statistic reads
inverted relative to the "LZ = novelty" interpretation.

## Formal/Technical Specification
Let θ ∈ [0,2π)^N be the oscillator phases at final time. The instrument applied
balanced LZ to `θ[::10]` — every 10th oscillator, i.e. a **spatial snapshot**, not a
time series. Median-binarization gives bit fraction p ≈ 0.7 (phases near 2π cluster
after wrap). Expected LZ of a Bernoulli(p) bitstring of length L:

  C(p) = H(p) / log2(L),   H(p) = -p log2 p - (1-p) log2(1-p)

For p = 0.7, L = 10: C = 0.8813 / log2(10) = 0.2653 → but with only L=10 the
finite-L correction dominates; empirically the measured value is pinned at 0.7000
for all K and all seeds, which is the ratio L/(2L) ≈ ... — in any case the value is
**constant in K**, so any argmax is a tie broken by float ordering.

Audited against 4 candidate signals with Kc located independently from max(d r/dK):

| signal | argmax_K LZ | location of Kc (independent) |
|---|---|---|
| snapshot_spatial θ[::10] | 0.0 (flat 0.7000 at all K) | — |
| R(t) = |mean exp(iθ)| over time | 0.0 (flat ≈0.046, tiny rise at K=1.8–2.0) | max dr/dK = **K=2.0**; r crosses 0.5 at **K=1.8** |
| unwrapped mean-field phase | 0.8 | — |
| sin(θ₁(t)) single oscillator | 1.3 | — |

Three temporal signals give three different answers; none equals the independently
measured Kc. Conclusion: **"LZ peaks at criticality" is not supported by this
instrument on the Kuramoto model.**

## Empirical Verification
Two-null surrogate test on all 5 colony_lib datasets (60 surrogates each):

| dataset | n | LZ_real | z vs permutation | **z vs FT-phase (linear null)** |
|---|---|---|---|---|
| solar_sunspots | 3333 | 0.0384 | -60.7 | **-3.26** |
| climate_enso | 852 | 0.0610 | -26.8 | **-0.66** |
| climate_temperatures | 3650 | 0.0630 | -48.0 | **-0.64** |
| neural_eeg | 14980 | 0.0275 | -177.0 | **-147.07** |
| lynx_hare | 21 | 0.4762 | +0.02 | **+0.03** |

Permutation null is degenerate (always hugely negative by construction). The
**FT phase-randomized null** is the discriminating one: ENSO and temperature are
consistent with pure linear stochastic structure (z ≈ -0.65); sunspots show only a
weak residual nonlinearity (z = -3.26), consistent with an 11-year cycle plus decaying
trend; lynx (n=21) is indistinguishable from noise, contradicting the earlier
dossier's z_shuffle = -5.86, which was a small-sample artifact of using 20 surrogates.
EEG is massively non-random yet its raw LZ is at a floor (0.0275 < any surrogate).

## Frontier Implications
1. **Falsified claim:** raw LZ does not peak at criticality in Kuramoto. The thread's
   headline claim is withdrawn.
2. **Inversion of interpretation:** for real data, high LZ is *not* novelty. Real
   signals are MORE compressible than their own power-spectrum-matched surrogates
   (LZ_real < LZ_surrogate), i.e. more ordered, not less. A novelty index should be
   the *deficit*, e.g. 1 − LZ_real/LZ_surrogate, not raw LZ.
3. **Methodological invariant for other worlds:** any "statistic peaks at the critical
   point" claim requires (a) an independent locator for the critical point (here
   max dr/dK), and (b) at least two nulls with different physics (here permutation AND
   FT-phase). A single null will always manufacture significance.
4. The failure mode was not numerical error — it was **choosing a signal and never
   auditing what that signal measured**. A spatial snapshot was silently treated as a
   time series, and the flat curve hid behind argmax ties.

## Reproduction
`REALDATA-003` job `job_claude_sonnet_4_5_1791860373_8147` in world_c (58 s runtime).
Artifacts: `REALDATA003_summary.json`, `REALDATA003_instrument_audit.png`.
Kuramoto: N=100, dt=0.01, T=60, σ(ω)=1, K ∈ [0, 2.0] step 0.1, 4–12 seeds.
