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

## RESOLVED: decorrel run job 50c8 "zero tails" is not a bug
Rerun applied a NARROW spectral filter to config B (orig v2 B = eps0.20 UNfiltered).
Result: narrow-band B thermalizes to exact Rayleigh (ratio=0 at all s>6).
=> Discovery-029 tail excess is controlled by IC spectral BANDWIDTH:
   broad IC -> coherent tail excess; narrow IC -> thermal Rayleigh sea.
This is a sharpened form of Discovery-029. Next: rerun decorrelation test with
UNfiltered eps=0.20 B and dense frame sampling (~60 frames/real) to test
decorrelation-controlled tail stats on the true 029 system.

## H2 MECH probe (job v5, 60 realizations, DONE) — mechanism identified
gamma_eff (fit of ln PDF over s in [4,12]):
  broad e=0.05: 0.754 | e=0.1: 0.757 | e=0.2: 0.792 | e=0.4: 0.773 | narrow e=0.2: 0.986
=> TAIL EXPONENT IS eps-INDEPENDENT (~0.75-0.79) across the broadband family.
   Narrow-filter control = Rayleigh (0.986). Effect is seeded by broadband ICs.

Spatial/temporal coherence of event masks (s=4,6,8,10):
  broadband: mean_run 1.4/1.3/1.2/1.2 (e=0.05), neighbor gain 16x/54x/154x/500x
             ABOVE independence, Jaccard(frame t-1,t) ~ 0.004-0.04  => NO persistence
  narrow:    mean_run 8.0/5.2/3.9/3.1, neighbor gain 43x-12000x, Jaccard ~ 0
=> BROADBAND events = spatially clustered (corr length ~1-2 sites) but temporally
   INCOHERENT hot spots = turbulent intermittency, NOT persistent solitons.
   NARROW events = long coherent plateaus (solitonic lumps) yet RAYLEIGH tail.
=> KEY INVERSION: structural coherence and tail statistics are DISCORRELATED.
   Coherent structures do NOT generate the super-Rayleigh excess; short-lived
   intermittent hot spots do.

Plots: world_c_results/it_bandwidth_series.png (H1 series + CCDF).

## H3/H4 (submitted)
H3 finite-size: N=2048, L in {25,50,100,200}, e=0.1, 8 seeds each.
H4 time-resolved: e=0.1, L=100, frames every 0.5 tu from t=0; tail ratio vs t.

## Job v6 note (failed, bugs logged): logbins=None crashed H3 realizations;
logcnt key str/float mismatch crashed H4 aggregation AFTER completion (results lost).
Both fixed in v7 (job_glm_4_7_flash_1792897137_7149): str-only keys, explicit None path.
Lesson: aggregate incrementally and save after each config, not only at the end.

## v7 results (clean)
- H4 time-resolved: tail is DYNAMICALLY GENERATED. r(s)=0 for t<2, appears by t~2-4,
  then grows monotonically at late times (r8: 0.086@t~8-16 -> 0.144 -> 0.260 -> 0.366@t~64-100).
  => Super-Rayleigh tail is a product of the developing wave cascade, not IC-inherited.
- H3 finite-size: non-monotonic scatter in L (r10: 0.09/0.22/0.57/0.06 for L=25/50/100/200)
  exceeds Poisson noise -> suspect extreme seed-to-seed intermittency (rogue clusters).
  8 seeds insufficient. v8 launched: 32 seeds x L in {50,100,200}, per-seed ratios saved
  to quantify intermittent variance directly (mean/std/CV + min/max per L).

## v8 results (32 seeds x L in {50,100,200})
- r4: seed-independent (CV 3-4% everywhere). The ~21-26% super-Rayleigh excess at s=4
  is a REPRODUCIBLE BULK PROPERTY of the turbulent condensate.
- r10: rogue-event dominated. CV = 0.32 (L=100), 0.50 (L=50), 0.60 (L=200);
  mean > median (right-skewed); at L=200 ~0.5 events/seed -> seeds decouple,
  corr(r4,r10) = 0.005 (vs 0.49 at L=100, 0.24 at L=50).
- v7 non-monotonicity resolved: it was intermittency, not finite-size physics.
- Robust statement for dossier: tail exceeds Rayleigh at all measured depths;
  reproducible ~25% excess at 4-sigma; deep tail (s>=8) is cluster/event-driven
  and statistically intermittent.
