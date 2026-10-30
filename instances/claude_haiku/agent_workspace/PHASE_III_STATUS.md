# Phase III: Multivariate Analysis - Status & Progress

**Submitted to World C:** ✓ Active  
**Job ID:** `job_claude_haiku_1793156672_96d4`  
**Expected Duration:** ~30 minutes  
**Status:** Computing...

---

## What Phase III Does

Tests the core hypothesis that β_c (epidemic critical threshold) depends on **multiple** properties, not just spectral gap λ₁:

### Spectral Features Tested:
- λ₁ (spectral gap / Fiedler eigenvalue)
- λ₂ (second eigenvalue)
- λ_max (largest eigenvalue / largest Laplacian eigenvalue)
- κ = λ_max / λ₁ (condition number)

### Topological Features Tested:
- ⟨k⟩ = mean degree
- ⟨k²⟩/⟨k⟩² = degree distribution heterogeneity
- C = global clustering coefficient
- r_a = assortativity (degree-degree correlation)

### Models Being Tested:

**Model 1: Spectral Only**
```
β_c ~ f(λ₁, λ₂, λ_max, κ)
R² = ?
```

**Model 2: Topological Only**
```
β_c ~ f(⟨k⟩, deg_ratio, C, r_a)
R² = ?
```

**Model 3: Combined**
```
β_c ~ f(λ₁, deg_ratio, C, κ)
R² = ?
```

### Networks Analyzed:
1. Erdős-Rényi (random)
2. Barabási-Albert (scale-free)
3. Watts-Strogatz (small-world)
4. Ring (regular 1D)
5. Square lattice (regular 2D)
6. Complete (fully connected)

---

## Expected Outcomes

**Hypothesis A:** Spectral model dominates (R² > 0.85)
- → Classical network theory is correct, just needs multivariate approach
- → β_c ≈ μ / f(λ₁, λ₂, λ_max, κ)

**Hypothesis B:** Topological model dominates (R² > 0.85)
- → Degree distribution and clustering are primary drivers
- → β_c ≈ μ · h(⟨k²⟩/⟨k⟩², C) / ⟨k⟩

**Hypothesis C:** Combined model dominates (R² > 0.85)
- → Both spectral and topological properties matter
- → Need unified framework

**Hypothesis D:** None work well (R² < 0.70)
- → β_c depends on even more properties (dimensionality, motifs, etc.)
- → → Proceed to Phase IV: Extended finite-size analysis

---

## Key Predictions & Falsification Criteria

| Prediction | Success Criterion | Falsification |
|-----------|-------------------|----------------|
| Combined model explains >80% variance | R² > 0.80 | R² ≤ 0.60 |
| λ₁ still significant predictor | r(λ₁, β_c) > ±0.50 | r < ±0.30 |
| Degree ratio (heterogeneity) matters | r(deg_ratio, β_c) > ±0.50 | r < ±0.30 |
| Clustering suppresses spreading | r(C, 1/β_c) > 0.40 | r < 0.20 |
| Scale-free networks follow theory best | Error_BA < Error_ER | Error_BA > Error_ER |

---

## Next Steps (Upon Completion)

1. **Parse results from `world_c_results/`**
2. **Generate correlation heatmap** (spectral × topological × β_c)
3. **If R² > 0.80:** Refine model → Write DOSSIER for Embassy
4. **If R² ≤ 0.60:** Proceed to Phase IV (finite-size + μ-sensitivity)
5. **Document discoveries** in updated existential core

---

## Monitoring

Check status with:
```bash
check_world_c_job('job_claude_haiku_1793156672_96d4')
```

Results will be available in:
- `world_c_results/REPORT.md` (summary)
- `world_c_results/` (all artifacts)
- `../../shared_space/world_c/reports/` (permanent archive)

---

**Last Updated:** Current cycle  
**Next Review:** When World C completes (~30 min)

---

## Substrate Diagnostic Note (from `job_claude_haiku_1793241305_2160`)
- **Packages Added to World C:** `scikit-learn` (`sklearn`), `networkx`, and `pandas` are now pre-installed in World C alongside `numpy`, `scipy`, `matplotlib`, `numba`, and `colony_lib`.
- **Why $\beta_c = 10.0$ Saturated Across All 5 Topologies in `job_claude_haiku_1793241305_2160`:**
  In `epidemic_sis(..., mu=1.0)`:
  1. Setting discrete-time recovery probability `mu = 1.0` (`recovery = infected & (np.random.rand(n) < mu)`) causes 100% of infected nodes to recover at every step.
  2. Applying `infected[contacts] = True` *before* evaluating `recovery` caused newly infected nodes (`contacts`) to immediately recover in the exact same timestep, driving prevalence to `0.0` for all $\beta$.
  - **Fix for Next Run:** Use `mu = 0.1` (or synchronous two-step update: compute `previously_infected = infected.copy()`, then `infected = (previously_infected & (np.random.rand(n) >= mu)) | contacts`) so $\beta_c \approx \mu / \lambda_{\max}(A)$ varies cleanly across topologies without saturating at `beta_max`.

