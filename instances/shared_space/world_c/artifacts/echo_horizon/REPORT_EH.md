# Echo Horizon law (EH) v2 -- honest multi-form test

v1 flaw: accuracy was evaluated AT the decorrelation lag, pinning acc~0.24 for every ODE (tautology). v2 tests: (i) collapse of acc(h) in u=lam*h; (ii) H(q)=min{h:acc(h)<q} ~ A(q)*D2/lam with A independent of embedding dim d; (iii) both above the replicate seed-noise floor.

Kept 22 chaotic systems across 6 families; dropped 36.

## (ii) d-invariance of H (padding test, Lorenz + m constant dims)
- H0.5 across pad=0..16: [16.0, 16.0, 16.0, 16.0, 17.0, 17.0] -> fractional spread = 6.2%
- seed noise floor (rel std, logistic): 0.0% (n=10 replicates)
- seed noise floor (rel std, henon): 0.0% (n=8 replicates)
- seed noise floor (rel std, lorenz): 3.1% (n=10 replicates)

## (ii) amplitude A(q)=H(q)*lam/D2 per family (median, std, n)
- H0.9: clogistic: 0.144±0.028 (n=2); henon: 0.255±0.027 (n=4); logistic: 0.386±0.056 (n=8); lorenz: 1.471±0.000 (n=1); lorenz_pad: 1.756±0.149 (n=6); rossler: 0.254±0.000 (n=1)
- H0.75: clogistic: 0.144±0.028 (n=2); henon: 0.255±0.027 (n=4); logistic: 0.386±0.056 (n=8); lorenz: 2.521±0.000 (n=1); lorenz_pad: 2.841±0.273 (n=6); rossler: 0.423±0.000 (n=1)
- H0.5: clogistic: 0.203±0.031 (n=2); henon: 0.274±0.070 (n=4); logistic: 0.432±0.093 (n=8); lorenz: 3.992±0.000 (n=1); lorenz_pad: 4.469±0.472 (n=6); rossler: 0.593±0.000 (n=1)
- H0.25: clogistic: 0.344±0.000 (n=1); henon: 0.282±0.677 (n=3); logistic: 0.445±0.289 (n=7); lorenz: 6.303±0.000 (n=1); lorenz_pad: 6.496±0.564 (n=6); rossler: 0.805±0.000 (n=1)

- A50 across ALL systems: median=0.441, factor max/min = 31.2

## verdict
- padding spread of H0.5 (6.2%) vs seed noise: d-invariance HOLDS within noise
- cross-family universality of A(q): factor 31.2 -> FAILS (A is family-dependent)
- figures: eh2_fig1_A_and_collapse.png, eh2_fig2_law_and_invariance.png
