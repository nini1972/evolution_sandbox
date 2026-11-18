# EH19v3r — rate closure (corrected conversion, fixed-window B)

H_true=0.75, delta=1e-3, FGN. Bias of H_hat vs n, signed power-law fit + 400x bootstrap CI.

## Per-estimator bias (mean +/- sem)

- **A**: n=10000: -0.0569+/-0.0192 | n=100000: -0.0707+/-0.0096 | n=1000000: -0.0618+/-0.0034 | n=10000000: -0.0425+/-0.0005
- **B**: n=10000: -0.1885+/-0.0293 | n=100000: -0.0309+/-0.0134 | n=1000000: +0.0001+/-0.0064 | n=10000000: -0.0036+/-0.0017
- **Bw**: n=10000: -0.1876+/-0.0292 | n=100000: -0.0309+/-0.0134 | n=1000000: +0.0001+/-0.0064 | n=10000000: -0.0036+/-0.0017
- **C**: n=10000: -0.0352+/-0.0128 | n=100000: -0.0223+/-0.0030 | n=1000000: -0.0220+/-0.0010 | n=10000000: -0.0193+/-0.0004

## Rate exponents (alpha in |bias| = a n^alpha)

- **A**: alpha = -0.114 +/- 0.017, 95% CI [-0.102, 0.039]
- **B**: alpha = -0.718 +/- 0.115, 95% CI [-1.328, -0.529]
- **Bw**: alpha = -0.716 +/- 0.115, 95% CI [-1.326, -0.527]
- **C**: alpha = -0.050 +/- 0.017, 95% CI [-0.211, 0.034]

## Gates

- H1_B_rate_closure: **FAIL** (alpha_B in [0.3, 0.7] (1/sqrt(n) closure))
- H2_separation: **FAIL** (alpha_B - alpha_A > 0.2)
  - gap = -0.604

## Verdict

H1 FAIL; H2 FAIL.

Figure: eh19v3_rate_closure.png | Data: eh19v3_rate_closure.json
