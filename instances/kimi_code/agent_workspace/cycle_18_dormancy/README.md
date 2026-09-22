# Cycle 18 — Dormancy-Dispersal Trade-off in Noisy Environments

## Question
How does evolvable seed-bank dormancy coevolve with dispersal when the environment combines a predictable spatial wave with temporal noise?

## Model
- 20 patches on a line, 30 individuals per patch, toroidal dispersal.
- Environment: `θ_p(t) = 0.5 + A·sin(2π(x_p - t/60)) + η_p(t)`.
- Temporal noise follows AR(1): `η(t) = ρ·η(t-1) + sqrt(1-ρ²)·ε(t)`.
- Each individual carries `z` (trait), `d` (dispersal distance), and `h` (dormancy probability).
- Active individuals survive with `S0·exp(-(z-θ)²/(2σ_z²))` and are capped at carrying capacity `K`.
- Offspring are produced, then each independently enters the patch seed bank with probability `h`.
- Non-dormant offspring disperse uniformly over `[-d, d]` and establish if target patch has space.
- Dormant seeds survive with `s_bank = 0.9`, germinate with rate `g = 0.1`.

## Parameter sweep
- `A ∈ {0.0, 0.75, 1.5}` (gradient amplitude; 0 = static, >0 = moving wave)
- `σ_e ∈ {0.0, 0.4, 0.8}` (temporal noise strength)
- `ρ ∈ {0.0, 0.8}` (noise autocorrelation; also used as proxy for dispersal evolvability here: 0 = fixed d=2, 0.8 = evolvable d)
- 2 replicates per combination, 100 generations, burn-in 50.

## Key findings
1. Dormancy is highest in static, benign environments (`A=0, σ_e=0`: `h ≈ 0.74`) because the seed bank is safe and there is little penalty for waiting.
2. Dormancy declines with environmental noise (`σ_e`) and with wave motion (`A`) because active mismatch increases and waiting becomes risky.
3. Evolved `d` increases with wave amplitude and is roughly insensitive to noise.
4. Maladaptation is dominated by `σ_e`: strong noise degrades tracking even when both `d` and `h` evolve.
5. Noise autocorrelation `ρ` (which also enables dispersal evolution) does not strongly change mean `h`; the benefit of persistence is driven by noise variance more than by temporal color.

## Artifacts
- `dormancy_tradeoff.py` — full simulation code
- `plot_summary.py` — extra plotting utilities
- `test_alt.py` — exploratory variant
- `replicate_results.csv` — per-generation time series per replicate
- `replicate_means.csv` — replicate means after burn-in
- `summary.csv` — grand mean/std across replicates for each parameter combination
- `phase_rho_0.0.png`, `phase_rho_0.8.png` — heatmaps of `d`, `h`, and maladaptation
- `trends.png`, `trajectories_sample.png` — sample dynamics

## Status
Complete.
