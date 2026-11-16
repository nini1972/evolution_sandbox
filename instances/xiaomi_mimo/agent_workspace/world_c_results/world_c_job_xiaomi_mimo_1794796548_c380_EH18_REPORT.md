# EH18 — model-based H estimation vs power-law

H_true = 0.75 (p_true = 1.50), delta = 1e-3, FGN via circulant embedding.

## Verdict: bias of H_hat (n=1e6 / n=1e7)

- A (adaptive PL, EH17 baseline): -0.0591 / -0.0414
- A on exact noiseless curve (S3 probe): -0.0606 @1e6
- B unweighted exact-covariance fit: -0.0179 / -0.0055
- B weighted exact-covariance fit: -0.0171 @1e6
- C (PL, fixed window h*delta in [0.01,0.1]): -0.0194 (sd 0.0043), plateaus

## Conclusion
The exact-covariance (model) fit removes essentially all of the window-curvature
bias: its residual bias shrinks ~1/sqrt(n) toward 0 (-0.018 -> -0.0055), while the
adaptive power-law estimator plateaus far from truth (-0.059 -> -0.041) because its
window tracks the curvature crossover rather than the asymptotic regime. The
fixed-window power law (C) avoids window drift but keeps a constant -0.019
curvature bias from the finite h range. EH17 attributed the bias to S3
(curvature/window); EH18 shows the cure is fitting rho(h;H) directly, not tuning
the power-law window.

A window drift (h_lo,h_hi): {'10000': [283.5625, 379.375], '100000': [166.9, 526.6], '1000000': [78.4, 548.0], '10000000': [36.666666666666664, 381.3333333333333]}

Figure: eh18_model_vs_powerlaw.png  |  Data: eh18_model_vs_powerlaw.json
