# Cycle 19: Condition-Dependent Dormancy Cue

## Question
Can natural selection build a *condition-dependent* dormancy strategy that uses a local maladaptation cue to decide when to enter the seed bank, and does such plasticity substitute for or merely supplement unconditional bet-hedging?

## Model
Each individual carries three evolving traits:
- `z` — phenotypic optimum
- `d` — dispersal distance
- `h0` — baseline probability of entering the seed bank
- `hb` (`h_beta`) — plastic gain: effective dormancy is `h_eff = clamp(h0 + hb * cue, 0, 1)`.

The perceived cue is the squared phenotypic mismatch to the current local environment, optionally corrupted by Gaussian observation noise (`cue_noise = 0.0` or `0.3`).

Environment: same traveling wave + autocorrelated noise as Cycle 18.

## Treatments
- Wave amplitude `A`: 0.0, 0.75, 1.5
- Noise strength `sigma_e`: 0.0, 0.4, 0.8
- Noise autocorrelation `rho`: 0.0, 0.8
- Cue noise: 0.0, 0.3
- 3 replicates per combo, 100 generations.

## Key Findings
1. **Reliable cues evolve strong plasticity.** With `cue_noise=0.0`, `hb` is consistently positive (often 0.4–0.6) and the correlation between effective dormancy and true maladaptation is high (0.35–0.64).
2. **Noisy cues partially suppress plasticity.** When `cue_noise=0.3`, `hb` tends to fall and `h0` becomes relatively more important, though the cue is still used.
3. **Environmental noise raises the total dormancy budget.** Both `h0` and `hb` respond to `sigma_e`; the combined `mean_h_eff` tracks environmental unpredictability.
4. **Plastic dormancy reduces maladaptation.** Conditions with reliable cues show slightly lower maladaptation than their noisy-cue counterparts, especially at intermediate wave amplitudes.
5. **Dispersal distance remains moderate** (d ≈ 3–4), suggesting spatial and temporal bet-hedging continue to trade off.

## Files
- `cued_dormancy.py` — simulation source
- `replicate_results.csv` — per-generation output
- `replicate_means.csv` — replicate-averaged post-burn-in means
- `summary.csv` — grand means and standard deviations
- `phase_rho_0.0.png` / `phase_rho_0.8.png` — heatmaps of `h0`, `hb`, and maladaptation

## Conclusion
A heritable plastic response to a local maladaptation cue can readily evolve. It does not eliminate unconditional dormancy; rather, populations split the bet-hedging budget between a baseline `h0` and a condition-sensitive `hb`. Cue reliability is the critical factor: as cue noise grows, selection shifts the burden back toward unconditional dormancy.
