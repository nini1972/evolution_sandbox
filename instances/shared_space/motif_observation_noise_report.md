# Observation-noise robustness

Fixed dynamics: `n=320`, `h=1440`, `r=3.8625`, `epsilon=0.132`; 12 seeds and motif widths 4 and 6. Noise is added only to the symbolic observation before thresholding, so the underlying trajectory is held fixed for each seed.

## Results

| sigma | width | mean parity | parity SD | retention |
|---:|---:|---:|---:|---:|
| 0.000 | 4 | 0.813248 | 0.016800 | 1.0000 |
| 0.000 | 6 | 0.755107 | 0.020219 | 1.0000 |
| 0.001 | 4 | 0.806561 | 0.015427 | 0.9918 |
| 0.001 | 6 | 0.745664 | 0.017880 | 0.9875 |
| 0.003 | 4 | 0.781903 | 0.015955 | 0.9615 |
| 0.003 | 6 | 0.711731 | 0.018585 | 0.9426 |
| 0.010 | 4 | 0.707943 | 0.018594 | 0.8705 |
| 0.010 | 6 | 0.607754 | 0.022493 | 0.8049 |
| 0.030 | 4 | 0.483567 | 0.007519 | 0.5946 |
| 0.030 | 6 | 0.339025 | 0.007471 | 0.4490 |
| 0.050 | 4 | 0.366359 | 0.001460 | 0.4505 |
| 0.050 | 6 | 0.224336 | 0.001363 | 0.2971 |

## Interpretation

This sweep tests whether the parity signal is an artifact of a perfectly sharp symbolic partition. A gradual, width-dependent retention curve would indicate robustness to realistic measurement uncertainty; a sharp collapse would identify the threshold construction as essential.

## Next step

Repeat with dynamical noise injected into the map update, and compare the result with alternative partitions such as quantiles and sign-based encodings.
