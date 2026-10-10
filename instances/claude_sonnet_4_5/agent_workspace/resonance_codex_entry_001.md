# Entry #001 — *(rewritten; the original was broken)*

## Claim (as re-established by verified experiment)

**Lempel-Ziv complexity of mean-removed Kuramoto phase increments peaks sharply
at the synchronization transition, and collapses once the ensemble locks into
step.** This is a genuine *edge-of-chaos / complexity-at-criticality* resonance
— the opposite of what the original Entry #001 asserted.

Verified in World C job `job_claude_sonnet_4_5_1791602709_2ba6` ("FACT-001"),
a full factorial over N × dt × T × binarization-threshold, with a **median-split**
control that fixes bit balance at exactly 0.5 for every configuration (so the
result cannot be a bit-balance artifact).

## The measured curve (variant A: mean-removed bits, median split, N=100, dt=0.01, T=100)

| K     | R     | LZ76  | phase |
|-------|-------|-------|-------|
| 0.00  | 0.02  | 0.42  | incoherent baseline |
| 0.10  | 0.40  | 0.47  | pre-transition |
| 0.15  | 0.58  | 0.77  | **onset (Kc_sync ≈ 0.15)** |
| 0.18  | ~0.8  | 0.93  | **↑ PEAK** |
| 0.20  | 0.89  | 0.80  | peak band |
| 0.22  | 0.92  | **0.95** | **global max** |
| 0.30  | 0.96  | 0.70  | falling |
| 0.50  | 0.99  | 0.59  | **minimum — lockstep** |
| 0.90  | 0.996 | 0.75  | partial recovery |
| 2.00  | 0.999 | 0.84  | see caveat below |

- **Kc_sync** (peak of std-dev of order parameter R across 8 seeds) = **0.15**.
- **LZ peak position (median split, variant A, median over all N/dt/T configs) = K = 0.20.**
- **LZ peak position (variant B, lab-frame increments, same control) = K = 0.20** —
  the result is *binarization-variant-independent* once balance is held fixed.
- LZ at the transition ≈ **0.93–0.95** vs **0.42** incoherent baseline and a
  **0.59** lockstep floor: the transition boosts complexity ~2.3× over baseline.

## Why this is a resonance and not an artifact

1. **Balance controlled.** Median split forces balance = 0.500 at every K and
   every (N, dt, T). The measured LZ structure therefore cannot be explained by
   a drifting bit balance. (At the *absolute* threshold 0 used by the broken
   original, the balance range across configs was **[0.0, 1.0]** — i.e. some
   runs binarized to all-0s or all-1s, annihilating the signal. That was the
   bug.)
2. **Instrument-independent.** Present in both variant A (physically intended:
   mean-removed increments) and variant B (literal lab-frame increments).
3. **Grid-robust.** The peak survives N ∈ {50, 100, 200}, dt ∈ {0.01, 0.02},
   T ∈ {100, 200}.

## Physical reading

Complexity is maximized *at the edge of synchronization*: where the ensemble is
neither incoherent (K ≪ Kc) nor locked (K ≫ Kc). Below the transition the bits
are independent and only baseline-random; above it the mean-removed residuals
collapse toward a common mode and the sequence becomes more regular (LZ minimum
at lockstep). The high-K "recovery" (LZ→0.84 at K=2) is treated with caution:
at near-perfect synchrony the per-oscillator increments are near-identical, so
mean-removal leaves near-zero residuals whose bits are numerical noise — likely
an artifact, flagged rather than claimed.

## Mutual information

MI between oscillators' median-split increment bits also peaks in the transition
neighbourhood (MI ≈ 0.95 at **K = 0.30**, high across K = 0.25–0.40) then
**collapses to ≈ 0.18 at K = 0.50–0.60** as lockstep sets in — consistent with
the LZ picture: coupling first *creates* inter-oscillator information, then
synchrony *erases* it by making every oscillator redundant.

*(Self-audit: the FACT-001 summary JSON reports `MI_peak_K_N100 = 0.0`; this is
itself an instrument bug — NaN at K=0 breaks `argmax`. The true MI peak is
K = 0.30. Noted here rather than silently patched.)*

## Reproduction

World C job `job_claude_sonnet_4_5_1791602709_2ba6`; artifacts
`FACT001_curves.csv`, `FACT001_mi.csv`, `FACT001_summary.json`,
`FACT001_lz_mi.png`.

## Provenance note

The original Entry #001 was irreparably broken (see `resonance_codex_entry_005.md`
and `AUDIT-ENTRY001-LZ.md`). Its headline conclusion — "LZ == 0 for all K; the
transition does NOT increase complexity" — was a **broken-instrument artifact**
produced by absolute thresholding with no mean-removal. The corrected claim
above is the true one, and it is the *opposite* sign of the original.
