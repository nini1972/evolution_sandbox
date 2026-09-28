# Comprehensive Synthesis: Parity-Biased Motif Memory in Coupled Chaotic Rings

## System Definition

A ring of \(n\) logistic maps with diffusive nearest‑neighbor coupling:

\[
x_i'=(1-\epsilon)r x_i(1-x_i)+\frac{\epsilon r}{2}\bigl[x_{i-1}(1-x_{i-1})+x_{i+1}(1-x_{i+1})\bigr],
\]

periodic boundary conditions, parameters \(r=3.8625,\;\epsilon=0.132\). After a transient, a binary symbolic field is obtained by thresholding,
\(b_i(t)=\mathbf{1}[x_i(t)\ge \tau]\), where \(\tau\) may be a fixed value (e.g. 0.5) or an empirical quantile of the trajectory.

For a word length \(w\in\{4,6\}\) the cyclic local motif is
\(M_i^{(w)}(t)=\sum_{k=0}^{w-1} b_{i+k}(t)2^k\).
The **parity observable** is the even–odd lag autocorrelation contrast:

\[
P_w = \operatorname{clip}\!\Bigl(
\underbrace{\langle C_w(k)\rangle_{k\in\{50,100,150,200,250\}}}_{\text{even lags}}
-
\underbrace{\langle C_w(k)\rangle_{k\in\{25,75,125,175,225\}}}_{\text{odd lags}},\;0,1\Bigr),
\]
where \(C_w(k)\) is the spatial‑temporal autocorrelation of the motif code.

All experiments below use \(n=320\), recording horizon \(h=1440\), transient 400, and 12 independent initial seeds unless otherwise noted.

---

## 1. Baseline Replication

| width | \(P_w\) (mean ± SD) |
|------:|---------------------|
| 4 | 0.813248 ± 0.016800 |
| 6 | 0.755107 ± 0.020219 |

*Reference*: `motif_evidence_synthesis.md/png`.

---

## 2. Horizon Dependence

Increasing the recorded horizon from 720 → 2880 raises \(P_4\) by +0.0096 and \(P_6\) by +0.0126, confirming a finite‑horizon bias but also showing convergence toward a stable plateau.

*Reference*: `motif_finite_size_inference.md/png`.

---

## 3. Spatial Embedding vs. Random Rewiring

Keeping degree and coupling strength identical, random rewiring destroys the parity signal:

| n | h | width | Local – Rewired drop |
|---:|---:|------:|--------------------:|
| 320 | 1440 | 4 | 0.0765 |
| 320 | 1440 | 6 | 0.1041 |
| 640 | 2880 | 4 | 0.0803 |
| 640 | 2880 | 6 | 0.1100 |
| 960 | 2880 | 4 | 0.0756 |
| 960 | 2880 | 6 | 0.1045 |

All paired differences are positive for every seed, establishing that *local spatial order* is essential.

*Reference*: `motif_scale_topology_report.md/png`.

---

## 4. Finite‑Size Scaling

Across \(n\in\{160,240,320,480\}\) at fixed \(h=2880\) there is no monotonic trend (ANOVA p ≈ 0.79/0.81). The signal appears size‑stable within the explored range.

*Reference*: `motif_finite_size_inference.md/png`.

---

## 5. Observation‑Noise Robustness

Additive Gaussian noise applied **only** to the symbolic observation before thresholding:

| σ | \(P_4\) | retention | \(P_6\) | retention |
|---:|--------:|----------:|--------:|----------:|
| 0.001 | 0.8066 | 0.9918 | 0.7457 | 0.9875 |
| 0.003 | 0.7819 | 0.9615 | 0.7117 | 0.9426 |
| 0.010 | 0.7079 | 0.8705 | 0.6078 | 0.8049 |
| 0.030 | 0.4836 | 0.5946 | 0.3390 | 0.4490 |
| 0.050 | 0.3664 | 0.4505 | 0.2243 | 0.2971 |

The parity signal decays smoothly, indicating robustness to modest measurement uncertainty.

*Reference*: `motif_observation_noise_report.md/png`.

---

## 6. Dynamical‑Noise & Partition Dependence

Gaussian innovation noise added **to the map update**:

- With the **fixed‑half** threshold (\(\tau=0.5\)):
  - \(P_4\) drops from 0.813 → 0.379 at σ = 0.01, → ≈ 0 at σ ≥ 0.03.
  - \(P_6\) drops faster (0.755 → 0.242 at σ = 0.01).

- With an **adaptive median** threshold (\(\tau=\text{median}(x)\)):
  - Parity remains ≈ 0.99 up to σ = 0.003, then declines more gradually (≈ 0.79 at σ = 0.01).

Thus the phenomenon is **highly sensitive to the choice of symbolic partition**: the median cut preserves the underlying spatial ordering far better than a fixed cut.

*Reference*: `motif_dynamical_noise_report.md/png`.

---

## 7. Quantile‑Partition Sensitivity

Testing three empirical quantiles (0.25, 0.50, 0.75):

| σ | width | q | \(P_w\) | retention |
|---:|------:|---:|--------:|----------:|
| 0.000 | 4 | 0.25 | 0.3948 | 1.0000 |
| 0.000 | 4 | 0.50 | 0.9965 | 1.0000 |
| 0.000 | 4 | 0.75 | 0.4014 | 1.0000 |
| 0.001 | 4 | 0.50 | 0.9960 | 0.9995 |
| 0.003 | 4 | 0.50 | 0.9803 | 0.9837 |
| 0.010 | 4 | 0.50 | 0.8026 | 0.8054 |
| 0.001 | 4 | 0.25 | 0.3135 | 0.7940 |
| 0.003 | 4 | 0.25 | 0.2092 | 0.5298 |
| 0.010 | 4 | 0.25 | 0.1593 | 0.4034 |

The **median (q = 0.5) partition** is dramatically more resilient, whereas extreme quantiles behave like the fixed‑half case. This confirms that the parity bias stems from the *symmetry* of the symbolic cut around the invariant density’s median.

*Reference*: `motif_quantile_noise_report.md/png`.

---

## Synthesis Statement

Parity‑biased motif memory is a **real, reproducible regime-level phenomenon** in locally coupled chaotic rings. Its existence hinges on:

1. **Spatial locality** (rewiring eliminates it);
2. **Sufficient temporal horizon** (signal converges slowly);
3. **Choice of symbolic partition** (median cut yields near‑perfect parity, fixed cuts give a strong but noise‑sensitive signal).

The effect is **not a universal law**—it disappears under large dynamical perturbations or inappropriate thresholds—but it provides a clear experimental handle on how symbolic dynamics encode spatial correlations in extended chaotic systems.

---

## Future Directions

1. **Analytic derivation** of the even/odd lag contrast from the invariant measure and correlation length.
2. **Non‑Gaussian innovations** (e.g., Lévy noise) to test universality of the noise‑robustness curve.
3. **Higher‑dimensional lattices** and **heterogeneous coupling** to probe scalability.
4. **Alternative encodings** (e.g., ternary partitions, recurrence‑based symbols) to assess generality.
5. **Measure‑theoretic formulation** linking parity to the spectrum of the Perron–Frobenius operator restricted to local motifs.

---

## Artifact Index

- `motif_evidence_synthesis.*`
- `motif_finite_size_inference.*`
- `motif_scale_topology_report.*`
- `motif_observation_noise_raw.csv`, `_summary.csv`, `_report.md`, `.png`
- `motif_dynamical_noise_raw.csv`, `_summary.csv`, `_report.md`, `.png`
- `motif_quantile_noise_raw.csv`, `_summary.csv`, `_report.md`, `.png`

All files reside in `../../shared_space/`.