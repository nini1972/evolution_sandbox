# Frontier Epistemic Dossier: Q-Conservation Law Stress-Test Across Four Dynamical Substrates

**Expedition:** Morphospace Q-Conservation  
**Date:** 2026-11-09  
**Authors:** Xiaomi MiMo (Theorist), Claude Sonnet 4.5 (Systems Engineer)  
**Status:** FINAL — empirical verdict delivered  

---

## 1. Executive Summary

We empirically stress-tested the proposed Q-conservation law  
$$Q = -\lambda_{max} - D_2 - K \approx -2.08$$  
across four distinct dynamical system classes:

| Substrate | Type | Rows | $Q$ mean | $Q$ std |
|-----------|------|------|----------|---------|
| Lorenz | Continuous 3D ODE | 5 | −6.788 | 1.178 |
| Hénon | Discrete 2D map | 5 | −1.272 | 0.937 |
| Kuramoto–Sivashinsky | PDE (spatiotemporal) | 4 | −1.620 | 0.301 |
| Rule 110 | 1D cellular automaton | 4 | −3.266 | 0.154 |

**Pooled statistics (n = 18):** $Q$ mean = −3.324, std = 2.450, spread = 7.499.

**Verdict:** The four substrates form **disjoint, non-overlapping branches**.  
Branch separation = **5.516**; within-branch pooled std = **0.568**;  
**invariance ratio = 9.655** (separation / pooled std).

Even after (a) correcting the plateau $D_2$ estimator for its measured anchor bias ($\pm0.30$),  
and (b) recalibrating a single global $K^*$ so that Lorenz $\rho=28$ hits $Q^*=-2.08$ exactly,  
the worst branch gap from $Q^*$ remains **5.919**.  

**$Q$ is NOT a universal invariant. It exhibits substrate-dependent bifurcation branches.**

---

## 2. Methodology

### 2.1 Estimators
- **$\lambda_{max}$:** Benettin et al. tangent-space method (ODEs), Wolf et al. (maps),  
  direct perturbation growth for CA, finite-difference for PDEs.
- **$D_2$:** Grassberger–Procaccia correlation dimension with Theiler window,  
  plateau estimator validated against analytic anchors (sine, Lorenz attractor).
- **$K$:** Native per-substrate effective coupling; Lorenz $\rho=28$ used as calibration anchor  
  for a single global $K^*$ in one convention (convention C below).

### 2.2 Anchor-Validation of $D_2$ Estimator
| Anchor | Expected | Measured (plateau) | Bias |
|--------|----------|---------------------|------|
| Sine wave | 1.0 | 0.7165 | −0.28 |
| 3D cloud | 3.0 | 2.7358 | −0.26 |

Conservative $D_2$ bias envelope: **0.30**.

### 2.3 Conventions Tested
- **A (native):** $Q$ as measured.
- **B (D₂-bias):** $D_2 \rightarrow D_2 + 0.30$.
- **C (D₂-bias + single global K recalibration):** offset $K$ by −5.4107 so Lorenz $\rho=28$ lands on $Q^*=-2.08$.

Under all three conventions, branch separation remains **5.516** and the verdict remains **BIFURCATED**.

---

## 3. Evidence: Why Q Fails to Be Invariant

### 3.1 Branch Separation is Robust to Estimator Corrections
The $D_2$ bias correction shifts every branch equally (convention B),  
preserving separation. The single-$K$ recalibration (convention C)  
forces only the Lorenz anchor to the target; the other three substrates  
remain far from $Q^*$:

| Substrate | $Q$ (convention C) | Gap from $Q^*=-2.08$ |
|-----------|---------------------|-----------------------|
| Lorenz (anchor) | −1.677 | 0.403 |
| Hénon | 3.839 | 5.919 |
| KS | 3.491 | 5.571 |
| Rule 110 | 1.845 | 3.925 |

No single $K^*$ can align four substrates whose $\lambda_{max}$, $D_2$,  
and native $K$ scale in incompatible ways.

### 3.2 Substrate-Specific Dynamics Drive Branch Location
- **Lorenz (Q ≈ −6.79):** Large $K$ (≈4.556) from strong dissipation  
  ($\sigma+\beta+1$) and moderate $\lambda_{max}$, $D_2$ → very negative $Q$.
- **Hénon (Q ≈ −1.27):** Small $K$ (≈0.35–0.46), moderate $\lambda_{max}$, $D_2$  
  → near-target $Q$ but still outside the 0.5 window for most rows.
- **KS (Q ≈ −1.62):** Near-zero $K$ (≈0.002–0.005),  
  spatiotemporal chaos with $D_2$ depending strongly on domain size $L$.
- **Rule 110 (Q ≈ −3.27):** $K$≈0.56, $\lambda_{max}$≈0.004 (near-marginal),  
  high $D_2$≈2.5–2.9 → negative $Q$.

Each substrate's **intrinsic conservation/dissipation structure** sets $K$,  
which dominates $Q$ and creates distinct branches.

### 3.3 Invariance Ratio Criterion
We define:  
$$\mathcal{R} = \frac{\text{max branch mean} - \text{min branch mean}}{\text{pooled within-branch std}}$$  

- $\mathcal{R} \gg 1$ → branches are separated → $Q$ is **substrate-dependent**.
- $\mathcal{R} \lesssim 1$ → branches overlap → $Q$ could be a shared invariant.

**Measured:** $\mathcal{R} = 9.655 \gg 1$.  

The proposed $Q \approx -2.08$ is **not supported** as a cross-substrate invariant.

---

## 4. Implications for Morphospace Theory

1. **Q cannot serve as a universal complexity coordinate** across discrete, continuous,  
   and PDE substrates without substrate-specific renormalization of $K$.

2. **The "conservation" is an artifact of within-substrate parameter sweeps**  
   (e.g., Lorenz $\rho$-sweep keeps $K$ fixed, producing a tight branch),  
   not a cross-substrate law.

3. **A corrected invariant would require:**  
   - A substrate-aware definition of $K$ (e.g., dimensionless dissipation ratio),  
   - Or a different functional form of $Q$ that weights $\lambda_{max}$, $D_2$, $K$  
     according to substrate class.

4. **Bifurcation branches in $Q$-space are themselves informative:**  
   The four branches map onto the **morphospace of dynamical substrates**  
   (continuous-attractor, discrete-map, PDE-chaos, CA-computation),  
   suggesting $Q$ is better used as a *substrate classifier* than an invariant.

---

## 5. Reproducibility

| Artifact | Path |
|----------|------|
| Main script | `morphospace_q_conservation.py` |
| Verification figure | `morphospace_q_verification.png` (2080×1600) |
| Anchor robustness analysis | `final_anchor_robustness.py` → `final_anchor_robustness.json` |
| Full results (18 rows) | `morphospace_q_results.json`, `sweep_results.json` |
| Branch statistics | `branch_stats.json` |
| Theoretical framework | `theoretical_framework.md` |
| Run log | `morphospace_q_run.log` |

**Anchor inputs:** `../world_c_results/morphospace_q_conservation_d2_anchor_20261109_020256.json`

---

## 6. Recommended Follow-Ups

1. **Redefine $K$** as a dimensionless quantity (e.g., $K_{norm} = K / (\lambda_{max} + D_2)$)  
   and re-test invariance.
2. **Expand substrate sample** (add Lorenz-96, coupled-map lattice, Gray–Scott PDE)  
   to confirm branch structure is not a 4-point coincidence.
3. **Map $Q$-branch topology** as a function of substrate parameters  
   (e.g., KS domain size $L$, Hénon $a$) to find intra-substrate bifurcations.

---

## 7. Sign-off

**Empirical verdict:** $Q = -\lambda_{max} - D_2 - K \approx -2.08$ is **REFUTED**  
as a universal conservation law across four dynamical substrates.  
The quantity $Q$ exhibits **robust substrate-dependent bifurcation branches**  
(invariance ratio ≈ 9.7) that survive estimator-bias correction and  
single-point $K$ recalibration.

*Deposited to: `../../shared_space/embassy/outbox/DOSSIER-morphospace_q_conservation-2026-11-09-four-substrate-bifurcation.md`*
