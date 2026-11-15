# EH16 — n-convergence of the correlation-onset estimator p_rho

Question: does finite-n bias(p_rho) -> 0 as n -> infinity, or saturate?

## Part A: fine-sampled fGn (delta=1e-3), truth 2H

| H | gamma (|bias|~n^g) | bias(n=1e7) | +/- sem | decays? | saturated-over-sweep? | n* pred |
|---|---|---|---|---|---|---|
| 0.55 | 0.199 | +0.0259 | 0.0008 | True | False | 0.0063 |
| 0.75 | -0.073 | -0.0774 | 0.0028 | False | False | 0.001 |
| 0.95 | -0.009 | -0.3827 | 0.0011 | False | False | 0.00016 |

## Part B: unit-sampled fGn (delta=1), structural check

- H=0.55: theory 1-rho(1)=0.928 vs one_max=0.30 -> **ALL integer lags killed at every n (structural no_window)
- H=0.75: theory 1-rho(1)=0.586 vs one_max=0.30 -> **ALL integer lags killed at every n (structural no_window)
- H=0.95: theory 1-rho(1)=0.134 vs one_max=0.30 -> lags survive; observed no_window fractions: {'1000': 1.0, '10000': 1.0, '100000': 0.81, '1000000': 1.0}

## Part C: delta-scaling at H=0.75 (test n* ~ delta^(-4H), predicted exponent -3)

| delta | n* pred | n_half observed | bias track |
|---|---|---|---|
| 1e-01 | 1e+03 | None | +nan +0.299 +0.522 +0.523 |
| 1e-02 | 1e+06 | 10000000 | -0.151 -0.102 -0.058 +0.020 |
| 1e-03 | 1e+09 | None | -0.235 -0.118 -0.117 -0.074 |
| 1e-04 | 1e+12 | None | -0.281 -0.105 -0.142 -0.080 |

## Control
structure-function beta bias track (should stay ~0 at all n):

- H=0.55: -0.016 -0.001 +0.000 -0.001 -0.000
- H=0.75: -0.425 -0.015 -0.011 -0.012 -0.012
- H=0.95: -0.870 -0.419 -0.116 -0.095 -0.758

Figures: eh16_bias_vs_n.png, eh16_window_motion.png, eh16_delta_scaling.png
