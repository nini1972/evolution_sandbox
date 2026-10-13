
---

# ADDENDUM (v2–v4): universality law is REFUTED; mechanism identified

## v2 — noise floor found
v1's claimed 1–5 % deviations were the **21-year numerical noise floor** of the
empirical Lyapunov estimator (λ's relative std across random seeds = 2.4 %).
Correcting: H λ / D2 **collapses to 6.2 %**, so the *law* holds to noise
within any single system, but its prefactor varies **31×** across families
(0.013–0.40) → the shape-universality is REFUTED.

## v3 — padding invariance (clean, confirmed)
Adding m-dim zero-padding to Lorenz (m=0,1,2,4,8,16):
D2 = 3.21±0.08 (6 %) — D2 is an invariant of the true dynamics, not the
observation map. Also: the correlation-onset exponent p (see below) stays
1.93±0.01 across m → p too is intrinsic to the dynamics, not the observer.

## v4 — mechanism
1. **H is a physical-time quantity.** Lorenz at dt = 0.02/0.01/0.005 gives
   H(dt=0.5)·dt = 0.160/0.170/0.165 (3 % invariant) while H-in-steps scales ∝1/dt.
2. **Exact identity:** single-lag linear prediction R²(h) = ρ(h)², hence
   H(q) = ρ⁻¹(√q). D2 and λ are *not* independent ingredients — the whole law is
   a statement about the autocorrelation function's decay.
3. **Non-universal onset exponent.** 1−ρ ~ t^p: **maps p≈0** (logistic 0.00,
   clogistic −0.00, henon 0.03), **flows p≈2** (lorenz 1.91–1.93), rossler 0.63.
4. **Smoothness, not dynamics, sets p.** Cubic-interpolating an oversampled
   logistic map drives p: 0 → 1.97, reproducing the "flow" regime from the same
   chaotic trajectory. The map/flow clusters are one family under a change of
   temporal sampling smoothness.

**Conclusion.** There is no universal A(q): the prefactor carries a
smoothness-class dependence (p) that dominates D2/λ. Echo horizons are
correlation-decay objects, H = ρ⁻¹(√q), not Lyapunov/D2 objects.
