# Echo Horizon law (EH) v2 -- honest multi-form test

v1 flaw: accuracy was evaluated AT the decorrelation lag, pinning acc~0.24 for every ODE (tautology). v2 tests: (i) collapse of acc(h) in u=lam*h; (ii) H(q)=min{h:acc(h)<q} ~ A(q)*D2/lam with A independent of embedding dim d; (iii) both above the replicate seed-noise floor.

Kept 10 chaotic systems across 4 families; dropped 17.

## (ii) d-invariance of H (padding test, Lorenz + m constant dims)
- H0.5 across pad=0..16: [16.0, 16.0, 16.0, 16.0, 17.0, 17.0] -> fractional spread = 6.2%
- seed noise floor (rel std, logistic): 0.0% (n=10 replicates)
- seed noise floor (rel std, henon): 0.0% (n=8 replicates)
- seed noise floor (rel std, lorenz): 3.1% (n=10 replicates)

## (ii) amplitude A(q)=H(q)*lam/D2 per family (median, std, n)
- H0.9: logistic: 0.409±0.023 (n=2); lorenz: 1.696±0.000 (n=1); lorenz_pad: 1.686±0.232 (n=6); rossler: 0.284±0.000 (n=1)
- H0.75: logistic: 0.409±0.023 (n=2); lorenz: 2.665±0.000 (n=1); lorenz_pad: 2.811±0.438 (n=6); rossler: 0.473±0.000 (n=1)
- H0.5: logistic: 0.409±0.023 (n=2); lorenz: 4.119±0.000 (n=1); lorenz_pad: 4.497±0.748 (n=6); rossler: 0.662±0.000 (n=1)
- H0.25: logistic: 0.603±0.170 (n=2); lorenz: 6.057±0.000 (n=1); lorenz_pad: 6.599±1.061 (n=6); rossler: 0.898±0.000 (n=1)

- A50 across ALL systems: median=3.932, factor max/min = 14.6

## verdict
- padding spread of H0.5 (6.2%) vs seed noise: d-invariance HOLDS within noise
- cross-family universality of A(q): factor 14.6 -> FAILS (A is family-dependent)
- figures: eh2_fig1_A_and_collapse.png, eh2_fig2_law_and_invariance.png
