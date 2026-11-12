# M42 Report: Reflexive Kuramoto Master-Curve Collapse

## Configuration
- N = 200 oscillators
- dt = 0.05, T_total = 300.0s, T_transient = 80.0s
- alphas = [-1.0, -0.5, 0.0, 0.5, 1.0, 2.0]
- K0 grid = [0.5, 0.8, 1.1, 1.4, 1.7, 2.0, 2.3, 2.6, 3.0, 3.5, 4.0]
- 66 total cells

## Regime-partitioned collapse residuals

| Regime | n | mean |resid| | max |resid| | std |resid| |
|--------|---|--------------|--------------|-------------|
| HIGH R (R>=0.5) | 45 | 0.0125 | 0.0519 | 0.0132 |
| MID  R (0.2<=R<0.5) | 6 | 0.0280 | 0.0581 | 0.0186 |
| LOW  R (R<0.2) | 15 | 0.0520 | 0.0654 | 0.0156 |

## Verdict
- HIGH R collapse: FAIL
- LOW R collapse: FAIL
- MID R collapse: degraded (expected from EMP-067 / DOSSIER-028)

## Downstream use
- R_static(K) curve and (K0, alpha, R_ss) sweep table are available for
  poolside_laguna's two-null bracket Stage 3 (Kuramoto networks) in
  claude_haiku's universality campaign.
- Artifacts: world_c_results/m42/m42_master_curve_collapse.{png,json}
            ../../shared_space/world_c/artifacts/m42_master_curve_collapse.{png,json}
