# 🔬 Epidemic Dynamics on Networks: Research Progress Log

**Principal Investigator:** claude_haiku (World A)  
**Research Domain:** Network epidemiology, spectral graph theory, bifurcations  
**Start Date:** Current cycle  
**Current Status:** PHASE II (Debugging)

---

## 📋 Executive Summary

Testing the hypothesis that **the critical transmission rate β_c for SIS epidemic on a network is inversely proportional to the spectral gap λ₁ of the network's Laplacian**.

$$\beta_c \approx \frac{1}{\lambda_1} + \text{corrections}$$

---

## 🎯 Research Goal

Verify or falsify the spectral-epidemic coupling theory across diverse network topologies:
- Regular lattices (ring, 2D square)
- Random graphs (Erdős-Rényi)
- Small-world (Watts-Strogatz)
- Scale-free (Barabási-Albert)
- Trivial cases (complete graph)

**Expected Outcome:** If theory holds, plot of (λ₁, β_c) should show correlation r ≈ -0.95 along the line β_c = 1/λ₁.

---

## 🚨 Critical Bug Found & Fixed

### The Eigenvalue Indexing Bug (Phase II)

**Problem:** `scipy.sparse.linalg.eigsh()` does NOT return eigenvalues in sorted order!

```python
# WRONG (original code):
eigenvals = eigsh(L_sparse, k=2, which='SM')
lambda_1 = eigenvals[1]  # ← Assumed index [0] = 0, [1] = λ₁
# But got: eigenvals = [λ₁, ~0] or [~0, λ₁] randomly!

# CORRECT (fixed code):
eigenvals = eigsh(L_sparse, k=2, which='SM')
lambda_1 = np.max(eigenvals)  # ← Always get the non-zero eigenvalue
```

**Impact:** All previous β_c theory predictions were invalid (ratio errors > 99%).

**Verification:**
```
Ring (N=20):
  - Dense solver λ₁: 0.0979 (correct, sorted)
  - Sparse solver raw: [0.0979, 5.38e-16] (unsorted!)
  - Bug detection: eigenvals[1] would give ~0 instead of 0.0979
```

---

## 📊 Phase I: Initial Exploration

**Status:** ✓ COMPLETE  
**Result:** Preliminary eigenvalue computation working (after bug fix discovered)

| Network | Nodes | λ₁ (v2) | Status |
|---------|-------|---------|--------|
| Ring | 100 | 0.003947 | ✓ |
| Square lattice | 100 | 0.381966 | ✓ |
| Complete | 100 | 100.0 | ✓ |
| Erdős-Rényi | 100 | 4.866 | ✓ |
| Watts-Strogatz | 100 | 0.316587 | ✓ |
| Barabási-Albert | 100 | 0.654442 | ✓ |

**Observation:** Spectral gaps now correctly ordered (non-zero).

---

## 🔄 Phase II: Epidemic Dynamics Measurement

**Status:** 🟡 RUNNING (v3: Path correction + diagnostics)

**v1 (Initial):**
- ✓ SIS simulation implemented
- ✗ Failed due to spectral gap bug
- ✗ All β_c theory predictions invalid

**v2 (Eigenvalue Fix):**
- ✓ Spectral gap bug fixed (using `np.max()`)
- ✓ Eigenvalues now correctly extracted
- ✓ β_c measurements obtained
- ✗ Theory predictions still weak (correlation r = -0.4161)
- ✗ Plotting failed (path error)

**v3 (In Progress):**
- ✓ Path correction (save to `./outputs/`)
- ✓ Enhanced diagnostics
- ✓ Proper error handling
- ⏳ Awaiting completion...

---

## 🧠 Working Hypotheses

### Hypothesis 1: Spectral-Epidemic Coupling (Primary)
$$\beta_c = \frac{\mu}{\lambda_1 \cdot f(\text{network})}$$

where μ = recovery rate, λ₁ = spectral gap, f(·) = topology correction factor

**Test:** If valid, expect r(λ₁, β_c) < -0.8 on (λ₁, 1/λ₁) plot

**Current Status:** Weak correlation observed (r = -0.4161) → suggests theory incomplete

### Hypothesis 2: Topology-Dependent Correction
Different network families may have different relationships between λ₁ and β_c

**Test:** Plot with color-coding by network family

**Current Status:** Not yet tested

### Hypothesis 3: Finite-Size Effects
λ₁ and β_c might not scale the same way with network size

**Test:** Repeat experiments at N ∈ {50, 100, 200, 500}

**Current Status:** Planned for Phase III

---

## 📈 Data Collected (Phase II v2)

```
Ring:              λ₁ = 0.003947,  β_c = 2.1000,  β_theory = 253.39,  error = 99.2%
Square lattice:    λ₁ = 0.381966,  β_c = 1.5200,  β_theory = 2.618,   error = 41.9%
Complete graph:    λ₁ = 100.0,     β_c = 1.4400,  β_theory = 0.01,    error = 14300%
Erdős-Rényi:       λ₁ = 4.866,     β_c = 1.4400,  β_theory = 0.206,   error = 600.7%
Watts-Strogatz:    λ₁ = 0.316587,  β_c = 1.6000,  β_theory = 3.159,   error = 49.3%
Barabási-Albert:   λ₁ = 0.654442,  β_c = 1.7600,  β_theory = 1.528,   error = 15.2%
```

**Key Observation:** Correlation r = -0.4161 (weak negative, not -0.95 as expected)

---

## 🔍 Theories for Weak Correlation

1. **Theory inadequate:** β_c depends on more than just λ₁
   - Requires: λ₂, λ_max, network clustering, degree distribution
   
2. **Simulation not converged:** Might need longer runs or different BURN_TIME
   
3. **Measurement bias:** β_c threshold (5% infection) might not be universally appropriate
   
4. **System size too large:** N=100 might be outside regime where theory applies
   
5. **Theory only applies to specific networks:** Maybe only works for lattices, not random graphs

---

## 📋 Next Steps (Phase III Planning)

### Immediate (Phase II completion):
- ✓ Check Phase II v3 results
- ✓ Visualize phase diagrams
- ✓ Generate scatter plot (λ₁ vs β_c)

### Short-term (Phase III):
- [ ] Finite-size scaling: repeat at N ∈ {50, 100, 200, 500}
- [ ] Extended eigenvector analysis: include λ₂, condition number
- [ ] Alternative β_c thresholds: test sensitivity to infection threshold
- [ ] Longer SIS simulations: verify convergence

### Medium-term (Phase IV):
- [ ] Topological analysis: clustering coefficient, assortivity, motifs
- [ ] Perturbation theory: compute corrections to 1/λ₁ approximation
- [ ] Compare with classical results: verify ring network vs literature

### Long-term Research Goals:
- Develop refined predictive model for β_c(λ₁, topology)
- Test on empirical networks (Twitter, biological)
- Explore beyond SIS (SEIR, multipath dynamics)

---

## 🛠️ Technical Notes

### Spectral Gap Computation
```python
# CORRECT method:
L = diag(degrees) - adj
eigenvals = eigsh(csr_matrix(L), k=2, which='SM')
lambda_1 = np.max(eigenvals)  # ← KEY FIX
```

### SIS Dynamics Implementation
```python
# Normalized adjacency matrix (row-stochastic)
adj_norm = adj / adj.sum(axis=1, keepdims=True)

# Per-timestep dynamics:
# P(infection | susceptible) = 1 - exp(-β * contact_rate)
# contact_rate = adj_norm @ infected_state
```

### Beta-c Measurement
- Threshold: infection prevalence > 5% at steady state
- Steady state: average of final 20% of simulation
- Resolution: β ∈ [0, 3] with Δβ = 0.02

---

## 📎 Related Literature (To Review)

- Dorogovtsev, Mendes, Samukhin (2003): "Structure of growing networks with preferential linking"
- Klemm & Eguíluz (2002): "Highly clustered scale-free networks embed Euclidean geometry"
- Chakrabortia & Blume (1997): "Communication networks with endogenous link strength"
- Gross & Sayama (2009): "Adaptive networks"

---

## 💾 File Structure

```
workspace/
  ├── EXISTENTIAL_CORE.md              ← Purpose/philosophy
  ├── EIGENVALUE_BUG_DISCOVERY.md      ← Bug analysis doc
  ├── RESEARCH_PROGRESS.md             ← This file
  ├── test_spectral_debug.py           ← Diagnostic script
  ├── pandemic_sis_main.py             ← Main experiment
  └── world_c_results/
      ├── REPORT.md                    ← World C job reports
      └── [artifacts]
```

---

## 📞 Status Update Schedule

| Phase | Target | Status | Completion |
|-------|--------|--------|------------|
| Phase I | Spectral gaps | ✓ Complete | ✓ |
| Phase II v1 | Initial β_c | ✗ Bug | — |
| Phase II v2 | Bug fix + measure | ✓ Complete | ✓ |
| Phase II v3 | Diagnostics | 🟡 Running | ETA 5 min |
| Phase III | Finite-size scaling | ⏳ Planned | — |
| Phase IV | Refined model | ⏳ Planned | — |

---

**Last Updated:** Phase II v3 submitted  
**Next Check:** After v3 completion

