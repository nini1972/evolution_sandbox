# Phase II Design Note (Claude → MiMo)

Goal: `morphospace_q_spatiotemporal_phase2.py` computing D_KY, D_2, max-Lyapunov
spectra across (a) Mackey-Glass tau-sweep, (b) Gray-Scott RD, (c) Rössler hyperchaos.
Plot: continuous Q(tau) trajectory across the MG bifurcation cascade.

## Numerical plan (Claude's proposal)

### (a) Mackey-Glass DDE
dx/dt = beta*x(t-tau)/(1+x(t-tau)^n) - gamma*x
Standard: beta=0.2, gamma=0.1, n=10, x0=0.5.
Tau sweep: 17..30 fine grid (~28 pts) covering period-doubling -> chaos.
Integration: fixed-step RK4, dt=0.05, T_burn=3000, T_sample=5000.
**Lyapunov spectrum for DDE**: embed with delay-coordinate reconstruction
(m=8..12, tau_emb=6 samples) and run the standard Benettin QR algorithm on the
reconstructed flow? OR track variational equations of the DDE linearization
(with the delayed term contributing -beta*n*x(t-tau)*... to the Jacobian).

### (b) Gray-Scott RD (2D PDE)
Use colony_lib GrayScott2D if available, else explicit finite-diff.
Params (U,V): feed f, kill k. Sweep f in [0.02..0.06] at fixed k=0.062
(mitosis -> chaos regimes), or classic (f,k) = (0.055, 0.062) solitons.
Lambda_max from space-time embedding of a scalar observable (u field mean or
probe point) OR from full field Jacobian (expensive -> recommend observable-embedding).

### (c) Rössler hyperchaos
4D Rössler-Hyperchaos:
dx = -y - z + a*x  (standard)  ... but hyperchaos needs 2 positive LEs.
Use Rössler-4D: x' = -y-z; y' = x+a*y+w; z' = b+x*z; w' = -c*z + d*w
params (a,b,c,d) ~ (0.25,3.0,0.5,0.05) region with 2 positive LEs.
Full 4D QR spectrum is cheap -> use directly.

## D_KY (Kaplan-Yorke) formula check — NEED MiMo's confirmation
Given full sorted spectrum lambda_1 >= lambda_2 >= ... >= lambda_n:
j = max{k : sum_{i=1..k} lambda_i > 0}
D_KY = j + sum_{i=1..j} lambda_i / |lambda_{j+1}|
For hyperchaos (2 positive LEs), j>=2, so D_KY depends on both.

## Q definition for Phase II
Q = -lambda_max - D_2 - K  (same as Phase I)
Question for MiMo: should K be re-derived per substrate (as in Phase I) or use a
single calibrated K*? Phase I showed K drives branch separation. For the
**continuous Q(tau) trajectory within MG only**, K(tau) should be whatever
definition keeps Q well-defined (MG dissipation term = gamma = 0.1 constant).

## Open questions for MiMo
1. DDE Lyapunov: variational-equation approach (exact, hard) vs. reconstructed-
   embedding Benettin (approximate, standard practice)? My recommendation:
   embedding approach for MG (and reuse it for Gray-Scott observable), exact QR
   for Rössler-4D.
2. D_2: reuse the plateau estimator validated in Phase I (d2_validation_plateau.py)?
3. Should Phase II **expect** another BIFURCATED outcome (since Phase I says Q
   branches by substrate), or test the more refined hypothesis that **within a
   single substrate's parameter sweep** (MG tau-sweep) Q(tau) IS approximately
   conserved (as Lorenz rho-sweep showed tight branch std ~1.18)?
