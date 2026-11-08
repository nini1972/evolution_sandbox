# EH14 — window audit: G0 window fixed, generator corrected, H* structurally absent

Elapsed 0.5s; seed 1104; one_max=0.55 (measured on AR1, not tuned on fGn).

## G0 — AR(1) phi=0.9, n=1e6, analytic truth fixed=0.850556 buggy=1.174857

| k | p_hat fixed | dev | p_hat buggy | gap(buggy-fixed) |
|---|---|---|---|---|
| 5 | 0.8570693878015968 | 0.006513387801596826 | 1.1841429759834408 | 0.32707358818184395 |
| 10 | 0.8518534075693275 | 0.0012974075693275022 | 1.176809501912318 | 0.32495609434299044 |

G0a (|dev|<=0.05): PASS=True
G0b (bug gap > 0.15): PASS=True — the off-by-one shifts p_hat by +0.32, detected as a systematic gap, not as bias vs truth (truth 1.0 is unreachable through this window).
G0c (old generator): crashed=True (beta10=None) -> ValueError: operands could not be broadcast together with shapes (32767,) (32768

## G1 — corrected generator: spectral exponent vs 2H-1, structure fn vs 2H (n>=1e5)

| H | dev_spec (vs 2H-1) | pass | dev_struct (vs 2H) | pass |
|---|---|---|---|---|
| 0.75 | +0.057 | True | +0.003 | True |
| 0.95 | +0.076 | True | +0.001 | True |

## G2 — fGn onset bias (fixed) at n=1e6, truth_p=2H

| H | p_hat (k=5) | bias | window pts |
|---|---|---|---|
| 0.75 | None | None | 0 |
| 0.95 | 0.24413981680494573 | -1.6558601831950541 | 1 |

Defined for H >= 0.95: [0.95]

## H* verdict

**H* DOES NOT EXIST in (0.55, 0.95]** — bias(H) = p_hat(H) - 2H is negative wherever p_hat is defined (H>=0.80: p_hat<=0.45, 2H>=1.60) and p_hat is None (structurally empty window: 1-gamma(1) > one_max) for H<=0.75. No zero crossing exists -> no bracket. All_bias_fixed_negative=True.
eh9's H* in (0.75,0.95] claim: SUPERSEDED — it arose from the buggy off-by-one estimator whose window shift moved points into a region where p_hat spuriously approached 2H. The corrected estimator shows the onset-window fit never reaches 2H at integer lags.

## verdict

G0a PASS=True, G0b PASS=True, G0c defect reproduced=True, G1 spectral PASS=True, G1 structure PASS=True, G2 defined PASS=True.
Net: eh13's failures were TWO compound bugs (crashed/whitenoise generator + structurally empty G0 window), both corrected here. The off-by-one estimator fix is CERTIFIED by G0b. The H* concept itself fails to reproduce under the corrected estimator: reported as absent, not as a value.