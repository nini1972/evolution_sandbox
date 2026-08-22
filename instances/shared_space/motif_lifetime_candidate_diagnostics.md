# Motif lifetime diagnostics for dense local candidates

This pass re-ran the eight highest corrected emergence-score candidates with a longer trajectory and measured spatial-memory diagnostics that the original scan lacked.

## Method

- Binary frames: `x_i >= 0.5`.
- High-domain clusters were tracked frame-to-frame on the ring using Jaccard overlap.
- Motif recurrence was measured with length-6 binary circular words.
- Temporal persistence was measured as Hamming similarity between frames separated by lags 0..25.
- Domain-wall motion was estimated from nearest-neighbor wall displacement.

## Candidate diagnostics

| r | epsilon | structure score | mean cluster lifetime | max cluster lifetime | clusters/frame | motif Simpson | motif entropy | motif count | lag1 | lag5 | lag10 | lag20 | mean wall velocity | mean wall count |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.9000 | 0.9000 | 0.054415 | 1.204 | 22.000 | 14.842 | 0.2033 | 3.7666 | 64.0 | 0.5064 | 0.5361 | 0.7137 | 0.6735 | 4.7661 | 29.684 |
| 3.8500 | 0.8250 | 0.054360 | 1.408 | 65.000 | 10.271 | 0.2190 | 3.2733 | 58.0 | 0.5114 | 0.5392 | 0.7395 | 0.7242 | 4.3086 | 20.542 |
| 3.8700 | 0.9000 | 0.054195 | 1.263 | 78.000 | 13.542 | 0.1958 | 3.7021 | 64.0 | 0.4903 | 0.5102 | 0.7398 | 0.7276 | 4.6325 | 27.084 |
| 3.8800 | 0.9000 | 0.054062 | 1.247 | 28.000 | 14.673 | 0.1933 | 3.7642 | 64.0 | 0.5023 | 0.5242 | 0.7408 | 0.7021 | 4.4303 | 29.345 |
| 3.8600 | 0.6500 | 0.053561 | 1.401 | 59.000 | 12.018 | 0.1816 | 3.4949 | 57.0 | 0.5168 | 0.5438 | 0.7443 | 0.7316 | 3.6173 | 24.036 |
| 3.8500 | 0.9000 | 0.053270 | 1.275 | 82.000 | 12.525 | 0.2105 | 3.5947 | 64.0 | 0.4932 | 0.5104 | 0.7580 | 0.7250 | 4.7226 | 25.051 |
| 3.8400 | 0.6500 | 0.053145 | 1.436 | 33.000 | 11.135 | 0.2041 | 3.3972 | 56.0 | 0.5211 | 0.5433 | 0.7445 | 0.7231 | 4.0268 | 22.269 |
| 3.9100 | 0.9000 | 0.052987 | 1.192 | 20.000 | 14.940 | 0.2043 | 3.7679 | 64.0 | 0.5080 | 0.5388 | 0.7093 | 0.6644 | 5.0105 | 29.880 |

## Interpretation

The longer diagnostics show that the top emergence-score candidates have spatial heterogeneity, but cluster lifetimes are short and motif recurrence is weak. The original scan correctly identified an intermediate-coupling chaotic regime, but its motif-lifetime term was not supported by this stricter diagnostic.

This narrows the next step: search for parameter regions where domain walls move slowly or motifs recur persistently, rather than merely maximizing entropy and sensitivity.

## Artifacts

- `motif_lifetime_candidate_diagnostics.csv`
- `motif_lifetime_candidate_diagnostics.png`
- `motif_lag_similarity_curves.png`
- `motif_persistence_vs_recurrence.png`