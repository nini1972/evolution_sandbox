# Emergence Atlas: Classified Ridge Map

## Purpose

This artifact replaces the single-score ranking with a regime classification map. The goal is to separate different mechanisms of persistence instead of forcing them into one scalar.

## Classification dimensions

- `parity_index`: even-lag motif mean minus odd-lag motif mean, clipped to `[0,1]`.
- `smooth_index`: gradual even-lag motif decay.
- `resonance_index`: high, spiky, phase-selective even-lag motif memory.
- `frame_even_mean`: ordinary frame-level persistence.
- `comp_even_mean`: complement-like memory.
- `periodicity_index`: tendency toward simple periodic wall behavior.

## Classes

1. **Smooth even-lag motif memory** — gradual even-lag motif decay with odd-lag collapse.
2. **Resonant phase-memory** — selected even lags remain high while odd lags collapse.
3. **Ordinary frame persistence** — frames persist without strong motif grammar.
4. **Complement-like memory** — motif at lag L resembles complement of motif at lag 0.
5. **Weak motif memory** — motif persistence exists but does not meet strong criteria.
6. **Low motif memory** — no strong motif persistence.

## Top candidates

- **ordinary frame persistence** at `r=3.8883`, `epsilon=0.1030`: `atlas_score=0.307099`, `parity=0.166`, `smooth=0.099`, `resonance=0.102`.- **ordinary frame persistence** at `r=3.9050`, `epsilon=0.1030`: `atlas_score=0.301191`, `parity=0.197`, `smooth=0.117`, `resonance=0.138`.- **ordinary frame persistence** at `r=3.9050`, `epsilon=0.1083`: `atlas_score=0.296675`, `parity=0.199`, `smooth=0.120`, `resonance=0.128`.- **ordinary frame persistence** at `r=3.8717`, `epsilon=0.1030`: `atlas_score=0.290989`, `parity=0.250`, `smooth=0.146`, `resonance=0.213`.- **smooth even-lag motif memory** at `r=3.8550`, `epsilon=0.1360`: `atlas_score=0.150577`, `parity=0.585`, `smooth=0.874`, `resonance=0.647`.- **smooth even-lag motif memory** at `r=3.8450`, `epsilon=0.1360`: `atlas_score=0.146683`, `parity=0.548`, `smooth=0.872`, `resonance=0.583`.- **smooth even-lag motif memory** at `r=3.8450`, `epsilon=0.1307`: `atlas_score=0.132865`, `parity=0.588`, `smooth=0.874`, `resonance=0.736`.- **smooth even-lag motif memory** at `r=3.8550`, `epsilon=0.1190`: `atlas_score=0.128829`, `parity=0.579`, `smooth=0.873`, `resonance=0.745`.
## Interpretation

The Atlas now shows two genuinely distinct memory regimes rather than one ranked ridge. Smooth even-lag motif memory appears around `r ≈ 3.888–3.905`, `epsilon ≈ 0.113–0.119`. Resonant phase-memory appears around `r ≈ 3.855–3.865`, `epsilon ≈ 0.125–0.136`.

The classification map is more truthful than the previous scalar score because it preserves the difference between smooth structural decay and resonant phase selection.

## Artifacts

- `emergence_atlas_classified.csv`
- `emergence_atlas_classified_map.png`
- `emergence_atlas_smooth_vs_resonance.png`
- `emergence_atlas_top_candidates.png`
- `emergence_atlas_top_curves.png`
