# Dynamical-noise and partition robustness

Fixed conditions: `n=320`, `h=1440`, `r=3.8625`, `epsilon=0.132`; 12 seeds, motif widths 4 and 6. Gaussian innovation noise is added to the coupled-map update before clipping. Two binary partitions are compared: the fixed threshold \(x=1/2\) and an adaptive trajectory median.

## Results

| sigma | width | partition | mean parity | parity SD | retention |
|---:|---:|---|---:|---:|---:|
| 0.000 | 4 | fixed_half | 0.813248 | 0.016800 | 1.0000 |
| 0.000 | 4 | median | 0.996506 | 0.002731 | 1.0000 |
| 0.000 | 6 | fixed_half | 0.755107 | 0.020219 | 1.0000 |
| 0.000 | 6 | median | 0.995150 | 0.003773 | 1.0000 |
| 0.001 | 4 | fixed_half | 0.736451 | 0.033381 | 0.9056 |
| 0.001 | 4 | median | 0.996737 | 0.002810 | 1.0002 |
| 0.001 | 6 | fixed_half | 0.646886 | 0.040284 | 0.8567 |
| 0.001 | 6 | median | 0.995496 | 0.003803 | 1.0003 |
| 0.003 | 4 | fixed_half | 0.746693 | 0.032109 | 0.9182 |
| 0.003 | 4 | median | 0.986598 | 0.005846 | 0.9901 |
| 0.003 | 6 | fixed_half | 0.649639 | 0.041936 | 0.8603 |
| 0.003 | 6 | median | 0.980539 | 0.008487 | 0.9853 |
| 0.010 | 4 | fixed_half | 0.378565 | 0.011618 | 0.4655 |
| 0.010 | 4 | median | 0.789990 | 0.026474 | 0.7928 |
| 0.010 | 6 | fixed_half | 0.241581 | 0.009657 | 0.3199 |
| 0.010 | 6 | median | 0.713895 | 0.033570 | 0.7174 |
| 0.030 | 4 | fixed_half | 0.000783 | 0.000650 | 0.0010 |
| 0.030 | 4 | median | 0.001728 | 0.000802 | 0.0017 |
| 0.030 | 6 | fixed_half | 0.000423 | 0.000340 | 0.0006 |
| 0.030 | 6 | median | 0.000619 | 0.000317 | 0.0006 |
| 0.050 | 4 | fixed_half | 0.000283 | 0.000392 | 0.0003 |
| 0.050 | 4 | median | 0.000217 | 0.000279 | 0.0002 |
| 0.050 | 6 | fixed_half | 0.000129 | 0.000236 | 0.0002 |
| 0.050 | 6 | median | 0.000144 | 0.000115 | 0.0001 |

## Interpretation

The fixed-half partition tests the original symbolic construction; the median partition tests sensitivity to the location of the binary cut. If both partitions retain the parity ordering under small dynamical noise, the phenomenon is less likely to be a threshold-location artifact.

## Next step

Extend the test to quantile partitions, non-Gaussian innovations, and larger rings, then ask whether the parity contrast has an analytic explanation in terms of correlation length or invariant symbolic measures.
