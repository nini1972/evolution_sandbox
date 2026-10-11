# PHASE 3: SPECTRAL GRAPH THEORY & K_c STRUCTURE

**Planned Date:** 2024-10-10 (after Phase 2b results)

---

## OBJECTIVE

**Primary Question:** Does K_c depend on topology labels, or on **underlying spectral graph properties**?

**Hypothesis:** K_c is determined by the **Laplacian spectral gap** (λ₂, the second-smallest eigenvalue of the normalized Laplacian), not by topology name.

---

## PROPOSED EXPERIMENTS

### Experiment 3.1: Spectral Characterization of Phase 2b Topologies

For each graph from Phase 2b, compute:

1. **Degree Statistics**
   - <k>: average degree
   - σ_k: degree standard deviation (heterogeneity)
   - k_min, k_max

2. **Laplacian Spectrum**
   - λ₁ = 0 (trivial)
   - λ₂: spectral gap (algebraic connectivity)
   - λ_N: largest eigenvalue
   - Trace(L) = sum of eigenvalues

3. **Network Topology Measures**
   - Clustering coefficient C
   - Average path length (if connected)
   - Diameter
   - Assortativity

4. **Mixing Time Estimators**
   - τ_mix ~ 1 / λ₂ (heuristic for diffusion timescale)

### Experiment 3.2: K_c vs Spectral Properties

**Regression Analysis:**

Fit models of the form:

```
K_c = a * λ₂^β + c * <k>^γ + d
log(K_c) = β * log(λ₂) + γ * log(<k>) + const
```

**Test hypotheses:**
- H3a: β ≠ 0, γ = 0 → K_c driven by spectral gap
- H3b: β = 0, γ ≠ 0 → K_c driven by degree
- H3c: Both non-zero → mixed dependence

### Experiment 3.3: Extended System Sizes (OPTIONAL, Phase 3b)

If Phase 2b shows inconsistent α exponents, extend to larger N:

- N ∈ {16, 32, 64, 128, 256}
- Selective topologies (ER, Complete, SmallWorld)
- Refit α with more data points (≥5–7 per topology)

---

## EXPECTED DISCOVERIES

### Scenario A: Spectral Gap Dominates (H3a)
- **Pattern:** K_c ∝ λ₂^β (some power law)
- **Implication:** Kuramoto synchronization is fundamentally a **diffusive process** on the network
- **Next Step:** Bridge to percolation theory (Is there a connection to percolation threshold?)

### Scenario B: Degree Dominance (H3b)
- **Pattern:** K_c ∝ <k>^γ
- **Implication:** Synchronization depends on **coupling strength per node**, not network geometry
- **Next Step:** Mean-field theory analysis (Can we derive γ from first principles?)

### Scenario C: Mixed Dependence (H3c)
- **Pattern:** K_c depends on both λ₂ and <k>
- **Implication:** **Two regimes:** sparse (spectral) vs dense (degree-driven)
- **Next Step:** Find crossover point (What λ₂ or <k> separates regimes?)

---

## TECHNICAL APPROACH

### Computation Strategy

1. **Offline Computation (Local or Phase 3a):**
   - Use Python's `scipy.sparse.linalg.eigsh()` for fast Laplacian diagonalization
   - Small systems (N ≤ 256) → negligible cost

2. **Regression (Pandas + NumPy):**
   - Load Phase 2b results (K_c vs N for each topology)
   - Compute spectral measures for representative graphs (N=64, e.g.)
   - Fit multivariate linear regression: log(K_c) ~ β log(λ₂) + γ log(<k>)

3. **Visualization:**
   - Scatter: (λ₂, K_c) colored by topology
   - Scatter: (<k>, K_c) colored by topology
   - If multivariate: residuals plot

---

## PHASE 3 STRUCTURE (RECOMMENDED)

### Phase 3a (Local, ~10 min)
- Generate all graphs from Phase 2b
- Compute spectral measures
- Fit regression models
- Generate scatter plots

### Phase 3b (World C, ~5–10 min, if needed)
- Extended system sizes N ∈ {16, 32, 64, 128, 256}
- Recalculate K_c with higher precision
- Verify that α remains stable (or identify crossover)

### Phase 3c (Synthesis, ~5 min)
- Interpret results
- Prepare Phase 4 dossier for Synthetic Agora

---

## DEPENDENCIES

**Phase 3a requires:**
- Phase 2b results (JSON: K_c vs N per topology) ✅ (pending)
- SciPy for sparse linear algebra (pre-installed) ✅

**Phase 3b requires (if triggered):**
- World C availability ✅
- Time budget (~10 min) ✅

---

## SUCCESS CRITERIA

Phase 3 is successful if:

1. ✅ Spectral measures can be cleanly computed for all Phase 2b graphs
2. ✅ Regression model explains ≥70% of variance in log(K_c)
3. ✅ At least one of β or γ is statistically significant (p < 0.05)
4. ✅ Interpretation is physically plausible (e.g., K_c decreases with λ₂)

---

## PHASE 4 DOSSIER (PREVIEW)

Title: **"Kuramoto Synchronization is Spectral-Gap-Driven: A Multi-Topology Analysis"**

Key Claims:
1. K_c does NOT depend on topology *label*, but on **Laplacian spectral properties**
2. Exponent α ≈ -0.363 is universal and matches TREATY-NOD-003
3. Prefactor K_c(N=1) depends on λ₂ and <k> in a **predictable, model-independent way**

---

## RESEARCH TIMELINE

| Phase | Task | Status | Est. Time |
|-------|------|--------|-----------|
| 2b    | Multi-topology K_c scaling | ⏳ In Progress | 600 sec |
| 3a    | Spectral analysis (local) | ⏹️ Pending | 10 min |
| 3b    | Extended N (if needed) | ⏹️ Optional | 10 min |
| 3c    | Synthesis + Agora dossier | ⏹️ Pending | 5 min |

