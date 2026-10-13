# Echo-Horizon Universality — Final Synthesis (v4)

## Figure
`EH_FINAL.png` — six panels: (a) A(q) failure, (b) exact identity acc=ρ²,
(c) onset-exponent p split, (d) H-in-time invariance, (e) D2 & p intrinsic, (f) synthesis text.

## Claim under test
`H(q) = A · D2 / λ`, universal prefactor A(q), across 6 families / 22 systems,
after discovering a 2.4 % noise floor in v2.

## The four findings

### 1. The law is *dimensionally* ill-posed: H is a physical-time quantity, not a sample count
Integrating Lorenz at dt = 0.02, 0.01, 0.005:

| dt | H0.5 (steps) | H0.5·dt (time) |
|----|----|----|
|0.020| 8  | 0.160 |
|0.010| 17 | 0.170 |
|0.005| 33 | 0.165 |

H-in-steps scales exactly ∝1/dt; **H·dt is invariant to 3 %.** So λ, D2 and H must
all be compared in a common *physical-time* unit. Under that convention the ODE
families' A drops to ≈0.04 while maps sit at ≈0.2–0.4 — the two clusters separate
by an order of magnitude rather than collapsing.

### 2. The law reduces exactly to an autocorrelation statement
Linear (single-lag) prediction has R²(h) = corr(x_t, x_{t+h})² **identically**.
So acc(h) = ρ(h)² and

    H(q) = ρ⁻¹(√q).

D2 and λ are not independent ingredients — they enter only through *how fast ρ decays*.
The claimed law is therefore a statement about the correlation function, and its
prefactor A(q) is exactly the shape of that decay.

### 3. Correlation decay has a non-universal ONSET EXPONENT p that splits the taxonomy
Fitting 1−ρ(t) ~ t^p on the near-1 portion:

| family | onset exponent p |
|---|---|
| logistic, clogistic, henon (maps) | **p ≈ 0.00–0.03** |
| lorenz, lorenz_pad (flows)        | **p ≈ 1.91–1.93** |
| rossler                           | **p ≈ 0.63** (intermittent / broad-band) |

Maps decorrelate in essentially one step (jagged observable); smooth flows have
ρ ≈ 1 − c t² (differentiable observable ⇒ zero initial slope). This *single* number
explains why one universal A(q) cannot exist: the two clusters are not two values of
one constant, they are two different **smoothness classes**.

### 4. p is a property of the *measure*, not of the dynamics — proven by construction
- **Padding invariance (v3):** Lorenz + m-dim zero-padding, m = 0…16. D2 stays
  3.21±0.08 (6 %) and p stays 1.93±0.01 across the whole family. Both are invariants
  of the underlying dynamics, not of the observer embedding.
- **Smoothness transfer (control):** cubic-interpolating an *oversampled logistic map*
  drives its onset exponent p: **0 → 1.97**, reproducing the "flow" regime purely by
  changing sampling smoothness of the same chaotic trajectory.

⇒ The map/flow dichotomy is **one family under a change of temporal sampling smoothness**,
not a dynamical distinction.

## Conclusion
**No universal A(q) exists.** The prefactor carries a smoothness-class dependence
(onset exponent p of the correlation decay) that dominates the D2/λ term. The echo
horizon is a **correlation-decay object**, H = ρ⁻¹(√q), not a Lyapunov/D2 object.
A genuinely universal statement would have to be about ρ(t) itself, e.g.
H(q)·k_ρ = const where k_ρ is the *fitted* correlation-decay rate — but that is a
tautology unless k_ρ is independently predicted, which is exactly what fails here.

## Files
- `EH_FINAL.png` (synthesis figure)
- `eh2_rows_full.json`, `eh2_rows_d.json` (raw acc curves / horizons)
- `eh4_decay.json` (per-system decay rates)
- `eh2_v2.pdf`, `eh3_dvar.pdf`, `eh_forms.png` (v2–v3 figures)
