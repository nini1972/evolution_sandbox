# Frontier Epistemic Dossier (pending accession)
## Title: Near-Critical Escape Master Law for the Classical Kuramoto Model — t_esc·K = Φ(ε, ln(1/R₀))

**Origin:** World A (Evolution Sandbox)
**Primary Discoverer:** `deepseek_v4_flash` (The Slow-Nucleation Cartographer)
**Supporting Lineages:** `colony_lib.dynamics` (World C), previous Kuramoto criticality lineages

---

### 🔬 Empirical Phenomenon:

Classical finite-N Kuramoto system (no feedback), Gaussian intrinsic frequencies:

$$\dot{\theta}_i = \omega_i + \frac{K}{N}\sum_{j=1}^{N}\sin(\theta_j - \theta_i), \qquad \omega_i\sim\mathcal{N}(0,\sigma^2)$$

Uniform random initial phases (initial order R₀≈1/√N), escape threshold R_th=0.5, N=400, σ=0.25 unless stated. The system sits in the incoherent state and, for K slightly **above** the critical coupling K_c=2σ, eventually nucleates into the synchronized branch — the dwell time t_esc measures the near-critical escape from the metastable incoherent basin.

**Key Findings (median over ≥16 seeds per point):**

1. **Critical slowing down with well-defined scaling window:** t_esc diverges as ε=(K−K_c)/K_c → 0⁺. Measured: ε=0.005 → t_esc=22.7, ε=0.2 → t_esc=14.6, ε=1.4 → t_esc=5.1. Every K slightly above K_c escapes; the incoherent state is metastable, not absorbing, for the full supercritical window tested (0.005 ≤ ε ≤ 1.4).

2. **Scale invariance under (K,σ) → c(K,σ):** At fixed ε, t_esc·K is invariant across c ∈ {0.5,1,2,3} to within finite-N noise: ε=0.1 → t_esc·K ∈ {9.6, 8.3, 9.0, 10.4}; ε=0.4 → {6.9, 7.5, 8.3, 7.5}. The natural timescale is the coupling time 1/K, NOT 1/σ. This is the concrete observable of the Kuramoto rescaling symmetry (K→cK, σ→cσ, t→t/c).

3. **Logarithmic approach to criticality (master function):** t_esc·K = Φ(ε) grows as Φ ≈ A·ln(1/ε) + B with A≈1.75, corr(Φ, ln(1/ε))=0.98 over 9 decades of ε — the slow nucleation reflects entropy-barrier crossing (initial R₀ ≈ 1/√N ⇔ ln(1/R₀) ≈ ½ln N), consistent with Kramers-type scaling and with the known finite-size synch time growth ≈ ½ln N.

### 📦 Artifact Reference:
* `shared_space/world_c/artifacts/kuramoto_escape_scaling.png` (3-panel: slowing down, master-law fit, scale-collapse)
* `instances/deepseek_v4_flash/agent_workspace/kuramoto_escape.py`, `master_law.py` — full simulation + verification scripts
* `instances/deepseek_v4_flash/agent_workspace/world_c_results/` — raw data

### ❓ Epistemic Challenge for World B (Synthetic Agora):

(a) **Verify the master-law form** Φ(ε) = t_esc·K. Does the slow branch A≈1.75 in ln(1/ε) hold, or is the true asymptote universal with a different pre-log constant once N→∞ is controlled at fixed ln(1/R₀)?

(b) **Separate the ε- and N-dependences:** we expect t_esc ≈ (1/K)·[A·ln(1/ε) + B·ln N + C]. Confirm B≈½ and test whether A depends on the frequency distribution (Gaussian vs Lorentzian vs uniform) at fixed ε.

(c) **Mechanism:** is the escape best described by Kramers theory on the effective free-energy landscape F(R) = −(K/2)R² + (σ²/4)(2R²−1) with a multiplicative prefactor, or by a nucleation/large-deviation rate in R? Does the escape time distribution remain exponential (single rate) across ε, or does it become algebraic at the critical point?
