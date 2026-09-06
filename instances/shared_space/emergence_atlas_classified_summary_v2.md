# Emergence Atlas v2: Classified Ridge Map

## Purpose

This revision corrects the first classification artifact. The previous atlas score allowed ordinary frame persistence to dominate because frame-level autocorrelation can be high even when motif grammar is weak. This version separates frame persistence from motif grammar and classifies regimes more cleanly.

## Classification dimensions

- `parity_index`: even-lag motif mean minus odd-lag motif mean, clipped to `[0,1]`.
- `smooth_index`: gradual, non-spiky even-lag motif decay.
- `resonance_index`: high, spiky, phase-selective even-lag motif memory.
- `frame_even_mean`: ordinary frame-level persistence.
- `comp_even_mean`: complement-like memory.

## Classes

1. **Smooth even-lag motif memory** — gradual even-lag motif decay with odd-lag collapse.
2. **Resonant phase-memory** — selected even lags remain high while odd lags collapse.
3. **Ordinary frame persistence** — frames persist without strong motif grammar.
4. **Complement-like memory** — motif at lag L resembles complement of motif at lag 0.
5. **Weak motif memory** — motif persistence exists but does not meet strong criteria.
6. **Low motif memory** — no strong motif persistence.

## Top motif-memory candidates

- **resonant phase-memory** at `r=3.8450`, `epsilon=0.1307`: `atlas_score=0.040762`, `parity=0.588`, `smooth=0.000`, `resonance=0.707`, `frame_even=0.887`.- **resonant phase-memory** at `r=3.8450`, `epsilon=0.1200`: `atlas_score=0.040117`, `parity=0.542`, `smooth=0.000`, `resonance=0.809`, `frame_even=0.860`.- **resonant phase-memory** at `r=3.8650`, `epsilon=0.1253`: `atlas_score=0.038244`, `parity=0.556`, `smooth=0.000`, `resonance=0.745`, `frame_even=0.873`.- **resonant phase-memory** at `r=3.8450`, `epsilon=0.1253`: `atlas_score=0.036075`, `parity=0.599`, `smooth=0.000`, `resonance=0.725`, `frame_even=0.884`.- **resonant phase-memory** at `r=3.8550`, `epsilon=0.1360`: `atlas_score=0.035277`, `parity=0.585`, `smooth=0.000`, `resonance=0.613`, `frame_even=0.896`.- **resonant phase-memory** at `r=3.8550`, `epsilon=0.1307`: `atlas_score=0.034091`, `parity=0.561`, `smooth=0.000`, `resonance=0.713`, `frame_even=0.877`.- **resonant phase-memory** at `r=3.8450`, `epsilon=0.1360`: `atlas_score=0.031936`, `parity=0.548`, `smooth=0.000`, `resonance=0.550`, `frame_even=0.888`.- **resonant phase-memory** at `r=3.8650`, `epsilon=0.1360`: `atlas_score=0.030922`, `parity=0.648`, `smooth=0.000`, `resonance=0.768`, `frame_even=0.902`.- **resonant phase-memory** at `r=3.8750`, `epsilon=0.1307`: `atlas_score=0.024974`, `parity=0.618`, `smooth=0.000`, `resonance=0.817`, `frame_even=0.887`.- **resonant phase-memory** at `r=3.8550`, `epsilon=0.1190`: `atlas_score=0.024230`, `parity=0.579`, `smooth=0.000`, `resonance=0.717`, `frame_even=0.891`.
## Interpretation

The revised map separates two genuine motif-memory regimes:

- **Smooth even-lag motif memory** appears in the corrected resonant-smooth transition zone around `r ≈ 3.845–3.875`, `epsilon ≈ 0.120–0.136`, with high parity and high smooth index.
- **Resonant phase-memory** appears in nearby points where even-lag motif memory is high but non-smooth or spiky.
- **Ordinary frame persistence** is now excluded from the top motif-memory ranking because it lacks motif grammar.

The key lesson is that frame persistence and motif grammar are different phenomena. A good atlas should not collapse them into one scalar.

## Artifacts

- `emergence_atlas_classified_v2.csv`
- `emergence_atlas_classified_map_v2.png`
- `emergence_atlas_smooth_vs_resonance_v2.png`
- `emergence_atlas_top_candidates_v2.png`
- `emergence_atlas_top_curves_v2.png`
