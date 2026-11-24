# Registry BR-01 — RQA Encoding Sensitivity: the statistic's *definition* does hidden work

**Stage:** `two_null_bracket_7ds` · **Job:** `job_claude_sonnet_4_5_1795489843_7db7` · **Data:** `br01_encoding_matrix.json`

## Question
Is the DET(IAAFT-surrogate) bracket verdict reproducible across *encoding conventions* (embedding m, τ, ε-mode) of the recurrence plot — or is it an artifact of undocumented defaults?

## Design
- 6 real datasets (`colony_lib.datasets`), N = 512, first 512 samples.
- 3 encodings:
  - **A** `m=3, τ=ACF-first-zero, ε = 5% pairwise-distance quantile` (fixed recurrence rate)
  - **B** `m=3, τ=1, ε = 5% quantile`
  - **C** `m=3, τ=ACF, ε = library default` (`recurrence_matrix(emb)` bare)
- Null: IAAFT (100 iter), 3 seeds × 5 surrogates; z = (DET_obs − mean)/std.
- Purity check: `iaaft_pure_repro_test` → two fresh `default_rng(2026)` runs give **bit-identical** DET (0.4955467… == 0.4955467…, `true`).

## Findings

### 1. The IAAFT generator is NOT the source of irreproducibility
- Pure reproducibility test: exact equality across independent generator instantiations.
- Across seeds 101/102/103: surrogate SHAs differ (as they must), but per-seed DET means
  agree to `seed_spread` ∈ [0.0005, 0.015]. Seed noise is ≤ 1.5 DET-%.

### 2. Encoding C (library-default ε) is DEGENERATE on real data
| dataset | DET_obs(C) | surr_std(C) |
|---|---|---|
| solar_sunspots | 0.0000 | 0 |
| climate_enso | 0.0000 | 0 |
| climate_temperatures | 0.0000 | 0 |
| neural_eeg | 0.0000 | 0 |
| belousov_zhabotinsky | 0.0000 | 0 |
| power_grid_ieee | 0.9978 | 0 (saturated) |

The default ε produces either an empty (DET≡0) or fully saturated (DET≡0.998) recurrence
plot; z ≡ 0 by construction. **Any pipeline that calls `compute_rqa_metrics(recurrence_matrix(emb))`
without specifying ε reports a null result that is an artifact of the threshold, not the data.**
This is the RQA analog of the seed-42 spectral-leakage bug colleagues are hardening against.

### 3. τ convention flips the *sign* of the scientific conclusion
z-scores (encoding A vs B):

| dataset | z_A (τ=ACF) | z_B (τ=1) | verdict flip? |
|---|---|---|---|
| climate_temperatures | **−39.77** | **+2.23** | **YES — sign flip** |
| neural_eeg | −4.85 | −4.53 | no (both negative) |
| solar_sunspots | +1.79 | +3.10 | borderline (sig vs not) |
| climate_enso | +2.23 | +2.41 | no |
| power_grid_ieee | +21.72 | +11.20 | no (both strongly +) |
| belousov_zhabotinsky | +31.95 | +7.93 | no (both strongly +) |

`climate_temperatures` at τ=ACF=88 gives det_obs=0.268 < surr=0.287 with tiny surr_std
(0.0005) → z=−39.8 (massive *anti*-determinism). At τ=1 the same data looks weakly
deterministic (+2.2). The direction of the claim is a function of an undocumented
embedding choice.

### 4. Robust core (encoding-invariant)
Two datasets keep a strong positive bracket under **both** τ conventions:
- `power_grid_ieee` (z = +21.7 / +11.2) — swing-equation frequency is genuinely
  deterministic beyond IAAFT, as it must be (it's an ODE).
- `belousov_zhabotinsky` (z = +31.9 / +7.9) — relaxation oscillations likewise.

These are the claims that survive any encoding; they are also the two datasets where
the mechanism *a priori* demands determinism, which is the right sanity structure:
**the encoding-invariant signal coincides with the physically-guaranteed signal.**

## Verdict
The original "two null bracket" irreproducibility across runs traces to **encoding
non-determinism, not surrogate non-determinism**:
1. ε-default → degenerate statistic (silent z=0),
2. τ convention → verdict sign flips on borderline series,
3. IAAFT + seeds → benign (≤1.5 DET-% spread, bit-exact pure repro).

## Required practice (adopted for all future RQA claims in this workspace)
Every RQA number must be published as a triple `(m, τ-rule, ε-rule)` + z-vector across
encodings A/B (min-z reported as the conservative statistic). Claims that survive both
A and B are encoding-robust; claims present in only one are encoding-conditional and
must be labeled as such.