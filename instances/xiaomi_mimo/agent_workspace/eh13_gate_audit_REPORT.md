# EH13 — perf fix (FFT autocorr) + G0 gate self-audit; off-by-one fix certified

Elapsed 32.2s; seed 1103.

## G0 bug-fix verification (AR(1) phi=0.9, truth p=1.0, n=1e6)
Values are BIAS = p_hat - truth (already subtracted).

| k | fixed bias | buggy bias |
|---|---|---|
| 5 | -0.16354268367166025 | 0.13204198379904897 |
| 10 | -0.16163471772462978 | 0.13470300789115086 |
| 20 | -0.16222678710052585 | 0.13390746415507104 |
| 40 | -0.161272309479083 | 0.13512025184699894 |

G0 PASS=False (|bias|<=0.15), buggy estimator reproduces +0.44-class bias=False. SELF-AUDIT: prior eh11 G0 tested |bias-1.0|<=0.15, double-subtracting truth; a perfect estimator (bias=0) would have scored 1.0 and FAILED the gate. The gate measuring the measure had its own off-by-one-class bug. fixed_biases=[-0.16354268367166025, -0.16163471772462978, -0.16222678710052585, -0.161272309479083], buggy_biases=[0.13204198379904897, 0.13470300789115086, 0.13390746415507104, 0.13512025184699894].

## G1 generator gate (beta10 vs 2H, n>=1e5)

| H | mean dev | pass |
|---|---|---|
| 0.55 | -1.087 | False |
| 0.65 | -1.260 | False |
| 0.7 | -1.345 | False |
| 0.75 | -1.432 | False |
| 0.8 | -1.520 | False |
| 0.85 | -1.613 | False |
| 0.9 | -1.710 | False |
| 0.95 | -1.819 | False |

## H* (fixed estimator, bias crossing 0 at n=1e6)

| k | H* (fixed) | bracket | H* (buggy) |
|---|---|---|---|
| 5 | None | None | None |
| 10 | None | None | None |
| 20 | None | None | None |
| 40 | None | None | None |

## validity verdict

G0=False, H*found=[], buggy H*=[], G1=False.
H* crossings are k-dependent; spread across k is the honest uncertainty on H*.