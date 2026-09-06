# Cycle 15 — Cue Robustness

This cycle extends Cycle 14 by asking how robust the evolved plastic-dispersal cue is to two realistic complications: **noise in the local-maladaptation cue** and a **metabolic cost of plasticity**.

See [DESIGN.md](./DESIGN.md) for full model equations, parameter choices, and results.

## Files

- `cue_robustness.py` — simulation engine and analysis scripts.
- `replicate_results.csv` — per-replicate time series.
- `replicate_means.csv` — mean trajectories across the last generation slice.
- `summary.csv` — final-generation means and standard deviations.
- `alpha_vs_noise.png` — evolved α and impact metrics across cue-noise levels.
- `alpha_vs_cost.png` — evolved α and impact metrics across plasticity-cost levels.
- `fitness_impact.png` — maladaptation, trait variance, and trait–environment correlation across treatments.

## How to run

```bash
cd cycle_15_cue_robustness
python cue_robustness.py
```

## Key result

Noise in the maladaptation cue (up to σ = 1.0) reduced evolved plasticity only modestly (mean α ≈ 1.28–1.54). In contrast, even a small explicit cost of plasticity (c_plast = 0.05) caused α to drop by ~40%, and at c_plast = 0.2 mean α fell to ~0.55. Unconditional dispersal distance remained stable across all treatments, and maladaptation showed little trend, suggesting that the population absorbs cue-error by relying on baseline dispersal rather than by abandoning plasticity.

## Status

Complete.
