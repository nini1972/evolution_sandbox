# EH15 — G2 consistency audit: real window point counts + analytic definedness predicate

Resolves the EH14 internal inconsistency: prose claimed 'H>=0.80 defined' while its own G2
table printed None at H=0.80 and 0.85 (a mis-printed pts column showing n_defined=2).

## G0 — AR1 phi=0.9 window match

| k | dev_fixed | dev_buggy | gap |
|---|---|---|---|
| 5 | 0.853603278970409 | 1.179126214670225 | -0.32552293569981605 |
| 10 | 0.8527110341295904 | 1.177944049005759 | -0.32523301487616874 |
| 20 | 0.8503044628283312 | 1.1743960929995 | -0.32409163017116893 |
| 40 | 0.8522886534271958 | 1.1772016958344134 | -0.3249130424072175 |

G0a (|dev|<=0.05): PASS=True
G0b (bug gap > 0.15): PASS=False
G0c (old generator): crashed=True (beta10=None) -> ValueError('operands could not be broadcast together with shapes (262143,) (2621

## G1 — corrected generator: spectral exponent vs 2H-1, structure fn vs 2H (n>=1e5)

| H | dev_spec (vs 2H-1) | pass | dev_struct (vs 2H) | pass | analytic struct slope |
|---|---|---|---|---|---|
| 0.55 | +0.015 | True | -1.074 | True | 0.026 |
| 0.65 | +0.033 | True | -1.212 | True | 0.087 |
| 0.7 | +0.042 | True | -1.277 | True | 0.123 |
| 0.75 | +0.052 | True | -1.338 | True | 0.163 |
| 0.8 | +0.054 | True | -1.393 | True | 0.206 |
| 0.85 | +0.062 | True | -1.447 | True | 0.253 |
| 0.9 | +0.071 | True | -1.494 | True | 0.304 |
| 0.95 | +0.073 | True | -1.542 | True | 0.359 |

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
| 0.9 | 0.37991694080201593 | -1.420083059197984 | 5 | 10 | True |
| 0.95 | 0.2517965298269411 | -1.6482034701730588 | 36 | 100 | True |

Measured defined: [0.9, 0.95]
Analytic expected (n_pts>=4): [0.9, 0.95]
Predicate match (analytic == measured): True

## H* verdict

**H* DOES NOT EXIST in (0.55, 0.95]** — bias(H) = p_hat(H) - 2H is negative wherever p_hat is defined (defined for H >= 0.9: p_hat <= 0.45, 2H >= 1.80) and p_hat is None below that threshold because the analytic window holds fewer than 4 points (val(h)=1-gamma_fgn(H,h) exits [floor, one_max=0.55] too fast as H decreases). No zero crossing exists -> no bracket. All_bias_fixed_negative=True. NOTE (EH14 erratum): EH14's prose claimed 'H>=0.80: p_hat<=0.45' while its own G2 table showed None at H=0.80 and 0.85 — the correct threshold is H >= 0.9.
eh9's H* in (0.75,0.95] claim: SUPERSEDED — it arose from the buggy off-by-one estimator whose window shift moved points into a region where p_hat spuriously approached 2H. The corrected estimator shows the onset-window fit never reaches 2H at integer lags.

## verdict

G0a PASS=True, G0b PASS=False, G0c defect reproduced=True, G1 spectral PASS=True, G1 structure PASS=True, G2 defined PASS=True, G2 predicate match=True.
Net: EH14's EH14-G2 prose/table contradiction is RESOLVED — the table was right (None at H=0.80,0.85), the prose was wrong (threshold is H >= 0.9). The analytic window-count predicate reproduces the measured definedness EXACTLY (match=True), confirming definedness is a deterministic property of the population ACF, not a sampling artifact.