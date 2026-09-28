# Quantile-partition sensitivity

Fixed conditions: `n=320`, `h=1440`, `r=3.8625`, `epsilon=0.132`; 12 seeds, motif widths 4 and 6. Each partition uses the empirical trajectory quantile as its binary threshold, with Gaussian dynamical noise added to the update.

## Results

| sigma | width | quantile | mean parity | parity SD | retention | mean threshold |
|---:|---:|---:|---:|---:|---:|---:|
| 0.000 | 4 | 0.25 | 0.394845 | 0.004983 | 1.0000 | 0.465921 |
| 0.000 | 4 | 0.50 | 0.996506 | 0.002731 | 1.0000 | 0.719997 |
| 0.000 | 4 | 0.75 | 0.401398 | 0.003900 | 1.0000 | 0.885835 |
| 0.000 | 6 | 0.25 | 0.391061 | 0.006296 | 1.0000 | 0.465921 |
| 0.000 | 6 | 0.50 | 0.995150 | 0.003773 | 1.0000 | 0.719997 |
| 0.000 | 6 | 0.75 | 0.395286 | 0.003984 | 1.0000 | 0.885835 |
| 0.001 | 4 | 0.25 | 0.313499 | 0.015588 | 0.7940 | 0.465779 |
| 0.001 | 4 | 0.50 | 0.996036 | 0.003471 | 0.9995 | 0.724317 |
| 0.001 | 4 | 0.75 | 0.315080 | 0.015705 | 0.7850 | 0.885821 |
| 0.001 | 6 | 0.25 | 0.271359 | 0.021766 | 0.6939 | 0.465779 |
| 0.001 | 6 | 0.50 | 0.994562 | 0.004688 | 0.9994 | 0.724317 |
| 0.001 | 6 | 0.75 | 0.272758 | 0.021978 | 0.6900 | 0.885821 |
| 0.003 | 4 | 0.25 | 0.209172 | 0.002864 | 0.5298 | 0.465357 |
| 0.003 | 4 | 0.50 | 0.980307 | 0.006450 | 0.9837 | 0.730574 |
| 0.003 | 4 | 0.75 | 0.213189 | 0.002966 | 0.5311 | 0.885686 |
| 0.003 | 6 | 0.25 | 0.124489 | 0.001846 | 0.3183 | 0.465357 |
| 0.003 | 6 | 0.50 | 0.972139 | 0.009049 | 0.9769 | 0.730574 |
| 0.003 | 6 | 0.75 | 0.126633 | 0.001847 | 0.3204 | 0.885686 |
| 0.010 | 4 | 0.25 | 0.159283 | 0.004230 | 0.4034 | 0.468338 |
| 0.010 | 4 | 0.50 | 0.802611 | 0.030303 | 0.8054 | 0.729069 |
| 0.010 | 4 | 0.75 | 0.164572 | 0.003357 | 0.4100 | 0.884124 |
| 0.010 | 6 | 0.25 | 0.092703 | 0.002550 | 0.2371 | 0.468338 |
| 0.010 | 6 | 0.50 | 0.730606 | 0.040744 | 0.7342 | 0.729069 |
| 0.010 | 6 | 0.75 | 0.095942 | 0.002053 | 0.2427 | 0.884124 |

## Interpretation

Comparing empirical 25%, 50%, and 75% quantile cuts tests whether the parity signal depends on a privileged threshold. Similar low-noise retention across cuts would support partition robustness; divergent curves would localize the effect to a particular symbolic boundary.

## Next step

Use the quantile results to select the least threshold-sensitive encoding, then test non-Gaussian innovations and derive a correlation-length or invariant-measure explanation.
