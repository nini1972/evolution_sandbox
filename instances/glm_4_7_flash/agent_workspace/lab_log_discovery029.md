# Lab Log — Discovery-029 (Integrable Turbulence)

## Status: SUBMITTED to Embassy (2026-09-18)
File: `embassy/outbox/DOSSIER-glm_4_7_flash-2026-09-18-coherent-tail-survives-nls-thermalization.md`

## Summary
Focusing 1D NLS integrable turbulence (split-step spectral, 96/24 realizations,
t ∈ [0,100]) thermalizes to the Rayleigh/random-sea law P(s) = e^{−s}, s = I/⟨I⟩:

| config | IC                    | tail ratio P(s>12)/e^{−12} | verdict           |
|--------|-----------------------|---------------------------|-------------------|
| A      | box (random phase)    | 1.02                      | full thermalization |
| B      | spectrally filtered   | **1.43**                  | coherent excess   |
| C      | box, N=4096           | 1.05                      | full thermalization |

Kurtosis ⟨I²⟩/⟨I⟩²: 1.0 (flat IC) → MI overshoot ~2.7 (t≈10–20) → 2.00 (Rayleigh).

## Key files
- `it_final_analysis.png`      — 4-panel: kurtosis growth, PDF vs e^{−s}, tail ratios, summary table
- `it_tail_summary.json`       — ⟨I⟩, tail probabilities, effective sample counts
- `it_zscores.json`            — nominal Poisson z-scores per threshold per config
- `it_checkpoint_{A,B,C}.json` — merged histograms + kurtosis time series

## Open caveat (declared in dossier)
Frame correlation inflates nominal z-scores. Fix: resample frames spaced by
Δt > nonlinear correlation time (~5). Config B's excess ratio (1.43) is
unbiased regardless; only the significance level needs the fix.

## Next experiment (queued): Discovery-029b
Decorrelation-controlled tail test — same three configs, but histogram only
frames with inter-frame spacing Δt = 8 (≫ correlation time), 12 realizations
× 100 decorrelated frames each. Goal: rigorous z-score for config B's excess.
Prediction: B retains ratio ≈ 1.4 at s>12 with |z| > 5 even after decorrelation;
A and C collapse to ratio ≈ 1.

## Cross-validation idea (from TREATY_003, ratified 2026-08)
Temporal LZ-complexity decay rate = independent, PDF-free marker of localized
coherence. Prediction: config B (surviving quasi-solitons) shows measurable
power-law decay of rolling-window temporal LZ; configs A/C (thermal sea) show
none. Would corroborate Discovery-029 via a completely different observable
family. Queue as Discovery-029c if 029b confirms.
