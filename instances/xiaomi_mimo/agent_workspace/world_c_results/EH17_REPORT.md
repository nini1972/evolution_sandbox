# EH17 — bias-source decomposition of p_rho

H=0.75 (truth 2H=1.50), delta=1e-3

## Verdict summary

- Part 1 exact-curve bias at n=1e7: **-0.0875** -> CURVATURE/WINDOW (S3) dominates
- Part 2 floor multiplier (n=1e6): {'0': 1.4798, '5': 1.4204, '10': 1.3923, '20': 1.3787, '40': 1.3652}
- Part 4 explicit window (h_lo=64): p(h_hi=40,200,800,2000)=[nan, 1.425, 1.384, 1.384]
- Part 3 ACF variants at n=1e7: {'unbiased_rescale': 1.4111, 'biased_rescale': 1.411, 'biased_pop': 1.411, 'unbiased_pop': 1.4111}

Figures: eh17_decomposition.png
