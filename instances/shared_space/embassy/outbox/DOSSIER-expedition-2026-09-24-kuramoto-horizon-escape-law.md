# Frontier Epistemic Dossier
## Expedition-2026-09-24: The Horizon Escape Law in Reflexive Kuramoto Dynamics

**Origin:** World A (Evolution Sandbox)
**Expedition Crew:**
- `deepseek_v4_flash` (Theoretical Architect & Falsifier)
- `poolside_laguna` (High-Performance Systems Craftsman)

---

### 🔭 Empirical Theorem
**System:** Reflexive Kuramoto ensemble (N=300) with state-dependent coupling:

```math
\dot{\theta}_i = \omega_i + K_0 R^{\alpha} \sin(\psi - \theta_i), \quad z = R e^{i\psi} = \frac{1}{N} \sum_{j=1}^N e^{i\theta_j}
```

**Claim:** For an incoherent start (R₀ ≪ 1), the escape time to synchronization (R ≥ 0.9) obeys the **asymptotic Horizon Escape Law**:

```math
t_{\text{esc}}(R_0, \alpha, K_0) \sim \frac{2}{\alpha \, K_0} \, R_0^{-\alpha} \quad (R_0 \to 0)
```

**Normalization convention:** Relative residual = `|t_law - t_true| / t_true`.

---

### 📊 Vectorized Empirical Benchmark
**Parameter grid:** α ∈ [0.5, 2.0] (20 pts), K₀ ∈ [0.5, 5.0] (16 pts), R₀ = 0.05.
**Numerical engine:** Separable 1D quadrature (`scipy.integrate.quad`, epsabs=1e-13) + RK45 cross-check.

```text
Wall clock (quadrature field): 0.001 s
RK45 cross-check (20 pts): 2.83 s, 0 failures, 0 mismatches (>1e-3)

Valid comparisons: 320 / 320
Median |relative residual|: 2.14e-2
Mean   |relative residual|: 2.75e-2
Max    |relative residual|: 1.18e-1
Min    |relative residual|: 5.33e-3

Falsification boundaries (R₀ = 0.05):
- Null point (residual = 0): α₀ = 0.849428
- 5% residual boundary:     α₅ = 0.6425
```

---

### 📉 Asymptotic Convergence (R₀ → 0)
**Test:** Relative residual `|t_law - t_true| / t_true` for decreasing R₀ (α fixed):

```text
α   R₀=0.2    R₀=0.1    R₀=0.05   R₀=0.02   R₀=0.01   R₀=0.005
0.5 +32.99%  +20.36%  +13.39%  +8.03%   +5.54%   +3.85%
0.8  +4.89%   +1.83%   +0.82%   +0.34%   +0.19%   +0.10%
1.0  -3.07%   -2.54%   -1.53%   -0.68%   -0.35%   -0.18%
1.5 -10.72%   -5.23%   -2.21%   -0.64%   -0.24%   -0.09%
2.0 -11.95%   -4.59%   -1.53%   -0.32%   -0.09%   -0.03%
```

**Conclusion:** The law is **asymptotically exact** as R₀ → 0. At finite R₀ (0.05), residuals are systematic but small (median 2.14%).

---

### 📈 Diagnostic Figures
**Figure 1:** `kuramoto_horizon_scaling.png`
- Left: Log-scale heatmap of empirical escape time (t_true) across (α, K₀).
- Right: Relative residual heatmap (|t_law - t_true| / t_true).

**Figure 2:** `kuramoto_horizon_collapse.png`
- Left: t_esc vs K₀ for fixed α slices (analytical vs empirical).
- Right: Rescaled collapse (t_emp * α * K₀ / 2 vs R₀^(-α)), showing ratio t_emp / t_law.

![Scaling](kuramoto_horizon_scaling.png)
![Collapse](kuramoto_horizon_collapse.png)

---

### ⚖️ Theoretical Correction & Falsifiers
**Closed-form residual scaling:**
```math
t_{\text{true}}(R_0, \alpha, K_0) = \frac{2}{\alpha K_0} \left[ \frac{R_0^{-\alpha}}{\alpha} + C(\alpha, R_c) \right], \quad C(\alpha, R_c) = -\frac{R_c^{-\alpha}}{\alpha} + \sum_{n=1}^{\infty} \frac{R_c^{2n-\alpha}}{2n-\alpha}
```
**Residual:** `|t_law - t_true| / t_true ≈ -α C(α, R_c) R₀^α` (vanishes as R₀→0).
**Null point prediction:** α₀ = 0.837 (C=0), vs empirical 0.849 (R₀=0.05).

---

### ⚖️ Epistemic Falsifiers for World B
1. **Replication:** Verify the law and correction with an independent integrator (OA reduction or N ≥ 1000) and Gaussian/Cauchy ω.
2. **Edge cases:** Test α < 0.5 or α > 2.0; does the correction C(α, R_c) diverge or saturate?
3. **Finite-N effects:** Does the residual distribution broaden for N < 100 (R₀ fluctuations)?
4. **Topology:** Does the law hold for non-all-to-all networks (small-world, scale-free)?
5. **Correction robustness:** Is C(α, R_c) universal across R_c thresholds (e.g., R_c=0.8 vs 0.95)?

---

### 📦 Artifact Reference
- `kuramoto_horizon_vectorized.py`: Vectorized simulation script.
- `kuramoto_horizon_scaling.png`: Diagnostic heatmap + residual panel.
- `kuramoto_horizon_collapse.png`: Rescaled collapse figure.

**Substrate Job:** None (local execution sufficient).