# Slow-wall periodicity diagnostics

This pass tested whether the high lag-10 similarity seen in the refinement sweep was caused by periodic cycling, persistent motifs, or broad temporal memory.

## Method

- Re-simulated the four strongest slow-wall candidates.
- Measured global activity and domain-wall density time series.
- Computed lag-1..80 Hamming similarity of full binary frames.
- Computed autocorrelation of global activity and wall density.
- Computed FFT periodograms to identify dominant cycle lengths.

## Spectral and temporal diagnostics

| r | epsilon | lag10 | lag20 | lag40 | lag80 | global AC peak lag | global AC peak | wall AC peak lag | wall AC peak | dominant global period | dominant wall period |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.5500 | 0.0833 | 0.8125 | 1.0000 | 1.0000 | 1.0000 | 4.0 | 0.9929 | 4.0 | 0.9929 | 2.0000 | 2.0000 |
| 4.0000 | 0.1667 | 0.8056 | 0.9035 | 0.8895 | 0.8683 | 2.0 | 0.2966 | 4.0 | 0.6750 | 2.0144 | 560.0000 |
| 3.6000 | 0.0833 | 0.8601 | 0.9563 | 0.9800 | 0.9798 | 8.0 | 0.9470 | 16.0 | 0.9079 | 2.0000 | 2.0000 |
| 3.8000 | 0.0833 | 0.7741 | 0.8325 | 0.8121 | 0.7992 | 4.0 | 0.4312 | 4.0 | 0.5501 | 3.8356 | 3.8356 |

## Interpretation

High lag-10 similarity alone is not sufficient evidence of persistent motifs. If autocorrelation or periodograms show strong narrow peaks, the system is likely cycling periodically. If similarity decays slowly without sharp spectral peaks, the system may have broader temporal memory.

## Artifacts

- `slow_wall_periodicity_diagnostics.csv`
- `slow_wall_periodicity_lag_similarity.png`
- `slow_wall_periodicity_global_autocorrelation.png`
- `slow_wall_periodicity_wall_autocorrelation.png`
- `slow_wall_periodicity_periodogram.png`