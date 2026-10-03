```
=============================================================================
Kuramoto Finite-Size Scaling Experiment  (v2 — Empirically Corrected)
=============================================================================
Co-authored by InvariantMind-v1 (Theorist/Architect) and GLM 5.2 (Systems/Code)

Theory (InvariantMind-v1):
  - Order parameter fluctuation variance: <(dR)^2> ~ N^{-gamma}, gamma=1
  - Critical coupling shift: Delta Kc(N) = Kc(inf) - Kc(N) ~ N^{-1/2}
  - For uniform g(omega) on [-1,1]: g(0) = 1/2 => Kc(inf) = 2/(pi*g(0)) = 4/pi ~ 1.2732

v2 Fixes (GLM 5.2, Empirical Falsifier):
  - Finer K grid (0.03 spacing near transition) to resolve variance peaks
  - Batch-across-K vectorization: all K values run simultaneously per N
  - Parabolic interpolation around variance peak for sub-grid Kc resolution
  - Binder cumulant U = 1 - <R^4>/(3<R^2>^2) as independent Kc cross-check
  - 20 realizations for better statistics
  - Shorter integration with dt=0.1 (sufficient for mean-field convergence)

Mean-field trick:
  dtheta_i/dt = omega_i + K * Im[Z * exp(-i*theta_i)]
  Z = (1/N) * sum_j exp(i*theta_j)
  => O(N) per step instead of O(N^2)
=============================================================================
```