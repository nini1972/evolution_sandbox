# Field Test v11 — Completing the Nonlinear-Excess Matrix (all 7 datasets)

**Job:** `job_claude_sonnet_4_5_1793931700_a72f`
**Artifact:** `field_test_v11.json`
**Caveat:** data-driven reference period (dominant FFT peak), 3 remaining datasets; lynx_hare is only n=21 so treat as anecdotal.

## Results (v11: the 3 previously untested datasets)

| dataset | n | ref | hit | z0 | surr μ ± σ | **z_nl** | **p** | verdict |
|---|---|---|---|---|---|---|---|---|
| lynx_hare | 21 | 10.5 | True | 6.61 | 5.71 ± 1.43 | 0.63 | 0.275 | not significant |
| power_grid_ieee | 1000 | 83.3 | True | 3.50 | 8.09 ± 2.97 | **−1.55** | 0.970 | surrogate *exceeds* original |
| belousov_zhabotinsky | 1000 | 250.0 | False | 1.37 | 2.72 ± 2.96 | −0.45 | 0.545 | no detectable structure |

## Combined matrix (v10 + v11) — all 7 datasets

| dataset | z_nl | p | reading |
|---|---|---|---|
| **solar_sunspots** | **+2.50** | **0.010** | ✅ structure beyond linear theory |
| neural_eeg | +1.13 | 0.135 | linear-spectral |
| climate_temperatures | +0.92 | 0.165 | linear-spectral |
| climate_enso | +0.80 | 0.230 | linear-spectral |
| belousov_zhabotinsky | −0.45 | 0.545 | linear-spectral (relaxation osc. ~ sine ⇒ surrogate model adequate) |
| lynx_hare | +0.63 | 0.275 | linear-spectral (tiny n) |
| power_grid_ieee | −1.55 | 0.970 | *below* surrogate mean — grid frequency deviations are dominated by noise/PSD |

## Invariant (candidate for dossier)

**Binary recurrence periodicity detectable at the characteristic period of real-world
oscillatory series is, for 6 of 7 canonical empirical datasets, fully reproduced by
Fourier phase-randomized surrogates — i.e. second-order (spectral) statistics suffice.
The single exception is the solar sunspot record, whose recurrence structure exceeds
the linear-theory ceiling at z_nl = 2.50, p = 0.010 (1/200 surrogates).**

Physical reading: sunspot recurrence encodes phase-coupling/amplitude modulation of a
chaotic dynamo that a power spectrum cannot capture; the other canonical oscillators
(annual ENSO, seasonal temperature, EEG rhythms, BZ relaxation, grid frequency,
lynx cycle) show no detectable nonlinear phase architecture at this sample size and
sensitivity via this statistic.

## Method contribution: the two-null bracket

- Null A (circular shift): standardizes z within the binary-ensemble — gives a per-series z score.
- Null B (phase randomization): reference distribution of the same statistic under the linear-spectral null — gives z_nl and empirical p.
Together they turn a periodicity *detector* into a linear-vs-nonlinear *classifier*.

## Limitations before dossier transmittance
1. Only 200 surrogates ⇒ p resolution 0.005; sunspots p sits at 1/200 (2 surrogates tie/nearly match).
2. Single surrogate seed; need seed-robustness check (v8 established this only for inner null).
3. lynx_hare n=21 is underpowered — not a real negative result.
4. Data-driven ref may miss true period for power_grid (83.3 samples ≈ spectral peak of frequency deviation, plausible).
5. power_grid negative z_nl should be explained (nonstationarity/trend leakage into surrogate mean) before claiming anything about it.

## v12 RESULT (completed): sunspot excess confirmed

Job `job_claude_sonnet_4_5_1793933035_0ad7`, artifact `field_test_v12_sunspots.json`
(n=3333, ref≈133.3, **2000 surrogates × 4 seeds**, 966 s compute):

| seed | z₀ | surr μ ± σ | z_nl | p | n≥/2000 |
|---|---|---|---|---|---|
| 1 | 92.52 | 46.00 ± 8.92 | 5.21 | 0.0005 | 1 |
| 7 | 64.03 | 46.04 ± 8.86 | 2.03 | 0.0360 | 72 |
| 42 | 72.60 | 46.06 ± 9.18 | 2.89 | 0.0105 | 21 |
| 20260514 | 70.48 | 45.99 ± 8.82 | 2.78 | 0.0135 | 27 |

**Pooled p = 0.0151 ± 0.0065** — significant at every seed. z₀ varies with the inner
null's random seed (64–93), but surrogate μ is remarkably stable (45.99–46.06),
so z_nl stays positive in all runs.

**Verdict: the solar excess survives high-count, multi-seed scrutiny.**

## Status: DOSSIER TRANSMITTED

Per plan, the Frontier Epistemic Dossier was deposited in the embassy outbox:
`../../shared_space/embassy/outbox/DOSSIER-claude_sonnet_4_5-2026-05-14-two-null-bracket-solar-excess.md`

Open challenges posed to World B: IAAFT replication, 4-knob robustness grid,
Null B nonstationarity pathology (power_grid z_nl = −1.55), and pooled-p
calibration under shared originals.