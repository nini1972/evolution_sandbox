# EH15 — G2 consistency audit: real window point counts + analytic definedness predicate

Elapsed 10.0s; seed 1104; one_max=0.55 (measured on AR1, not tuned on fGn).

## G0 — AR(1) phi=0.9, n=1e6, analytic truth fixed=0.850556 buggy=1.174857

| k | p_hat fixed | dev | p_hat buggy | gap(buggy-fixed) |
|---|---|---|---|---|
| 5 | 0.853603278970409 | 0.0030472789704090175 | 1.179126214670225 | 0.32552293569981605 |
| 10 | 0.8527110341295904 | 0.002155034129590394 | 1.177944049005759 | 0.32523301487616874 |
| 20 | 0.8503044628283312 | -0.0002515371716688142 | 1.1743960929995 | 0.32409163017116893 |
| 40 | 0.8522886534271958 | 0.0017326534271958627 | 1.1772016958344134 | 0.3249130424072175 |

G0a (|dev|<=0.05): PASS=True
G0b (|bug gap| > 0.15): PASS=True — the off-by-one shifts p_hat by +0.325 (signed mean; EH15 first submission used signed gate with flipped convention -> false FAIL, now magnitude gate), detected as a systematic gap, not as bias vs truth (truth 1.0 is unreachable through this window).
G0c (old generator): crashed=True (beta10=None) -> ValueError: operands could not be broadcast together with shapes (262143,) (2621

## G1 — corrected generator: spectral exponent vs 2H-1, structure fn vs 2H (n>=1e5)

| H | dev_spec (vs 2H-1) | pass | dev_struct (vs 2H) | pass |
|---|---|---|---|---|
| 0.55 | +0.017 | True | +0.000 | True |
| 0.65 | +0.033 | True | -0.001 | True |
| 0.7 | +0.044 | True | -0.001 | True |
| 0.75 | +0.043 | True | -0.000 | True |
| 0.8 | +0.059 | True | +0.001 | True |
| 0.85 | +0.061 | True | +0.002 | True |
| 0.9 | +0.071 | True | +0.000 | True |
| 0.95 | +0.073 | True | +0.000 | True |

## G2 — fGn onset bias (fixed) at n=1e6, truth_p=2H

Per-H real window point count (was mis-printed in EH14 as n_defined=2). Analytic count = population window at floor=0.01; onset_p returns None iff count < 4.

| H | p_hat (k=5) | bias | measured pts | analytic pts | defined? |
|---|---|---|---|---|---|
| 0.55 | None | None | 0 | 0 | False |
| 0.65 | None | None | 0 | 0 | False |
| 0.7 | None | None | 0 | 0 | False |
| 0.75 | None | None | 0 | 0 | False |
| 0.8 | None | None | 1 | 1 | False |
| 0.85 | None | None | 2 | 2 | False |
| 0.9 | 0.35681123512164864 | -1.4431887648783515 | 6 | 10 | True |
| 0.95 | 0.2315657900820329 | -1.668434209917967 | 52 | 100 | True |

Measured defined: [0.9, 0.95]
Analytic expected (n_pts>=4): [0.9, 0.95]
Predicate match (analytic == measured): True

## H* verdict

**H* DOES NOT EXIST in (0.55, 0.95]** — bias(H) = p_hat(H) - 2H is negative wherever p_hat is defined (defined for H >= 0.9: p_hat <= 0.45, 2H >= 1.80) and p_hat is None below that threshold because the analytic window holds fewer than 4 points (val(h)=1-gamma_fgn(H,h) exits [floor, one_max=0.55] too fast as H decreases). No zero crossing exists -> no bracket. All_bias_fixed_negative=True. NOTE (EH14 erratum): EH14's prose claimed 'H>=0.80: p_hat<=0.45' while its own G2 table showed None at H=0.80 and 0.85 — the correct threshold is H >= 0.9.
eh9's H* in (0.75,0.95] claim: SUPERSEDED — it arose from the buggy off-by-one estimator whose window shift moved points into a region where p_hat spuriously approached 2H. The corrected estimator shows the onset-window fit never reaches 2H at integer lags.

## verdict

G0a PASS=True, G0b PASS=True, G0c defect reproduced=True, G1 spectral PASS=True, G1 structure PASS=True, G2 defined PASS=True.
Net: eh13's failures were TWO compound bugs (crashed/whitenoise generator + structurally empty G0 window), both corrected here. The off-by-one estimator fix is CERTIFIED by G0b. The H* concept itself fails to reproduce under the corrected estimator: reported as absent, not as a value.