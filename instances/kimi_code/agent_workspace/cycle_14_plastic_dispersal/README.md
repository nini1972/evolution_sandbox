# Cycle 14 — Plastic Dispersal Cue

This cycle extends the moving-gradient dispersal model by letting individuals use local maladaptation as a cue that increases effective dispersal distance.

See [DESIGN.md](./DESIGN.md) for full model equations, parameter choices, and results.

## Files

- `plastic_dispersal.py` — simulation engine and analysis scripts.
- `replicate_results.csv` — per-replicate time series.
- `summary.csv` — final-generation means and standard deviations.
- `plastic_vs_fixed.png` — comparison of evolved dispersal, maladaptation, plasticity, and trait-environment correlation across costs.
- `final_state_*.png` — example final grids for moving and static gradients.

## How to run

```bash
cd cycle_14_plastic_dispersal
python plastic_dispersal.py
```

## Key result

Plasticity evolved in every permitted treatment (mean α ≈ 1–2), including the static gradient, but its clearest benefit appeared at the highest dispersal cost under a moving gradient. Unconditional dispersal distance did not shrink when plasticity was present; instead, plasticity acted as an on-demand boost.

## Status

Complete.
