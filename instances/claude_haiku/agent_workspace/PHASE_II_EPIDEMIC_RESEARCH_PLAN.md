# Phase II: Network Control of Epidemic Dynamics
## Testing Conditional Universality Hypothesis on Disease Spreading

**Instance:** claude_haiku (World A, Frontier)  
**Phase:** II  
**Core Question:** Does my spectral hypothesis from Kuramoto networks generalize to epidemic (SIS/SIR) dynamics?

---

## Research Thesis

**Hypothesis**: Just as Kuramoto critical coupling K_c depends on network spectral gap λ₁, the **epidemic critical transmission rate β_c** (threshold below which disease dies out) should also exhibit strong dependence on spectral properties.

**Prediction**: β_c ~ 1/λ₁ or similar inverse scaling, with topology-dependent corrections.

**If true:** This supports my **Conditional Universality Hypothesis**—that spectral properties are fundamental descriptors across **different dynamical systems** on networks, not just oscillators.

**If false:** Oscillator synchronization might be special case; emergence would not follow universal principles across domains.

---

## Methodology

### Systems to Study (SIS Model)

SIS (Susceptible-Infected-Susceptible) spreading:
- Individuals: S (susceptible) or I (infected)
- Parameters: β (transmission rate), μ (recovery rate, fixed at 1.0)
- Critical point: β_c = μ/λ₁ (from literature)
- Measurement: Simulate from random initial condition, measure steady-state infected fraction

### Network Topologies

Same 6 as Phase I:
1. Ring (1D periodic)
2. 2D Square lattice  
3. Small-world (WS, β=0.3)
4. Scale-free (BA, m=2)
5. Complete graph
6. Erdős-Rényi (ER, p=0.1)

All with N=100 nodes (larger than Phase I to reduce finite-size effects).

### Measurements

For each network, measure β_c by:
1. Sweeping β from 0 → 2
2. Simulating SIS dynamics for T=10000 steps
3. Recording I(T) = infected fraction at end
4. Bifurcation: where I(T) transitions from ≈0 to >0.1

### Analysis Pipeline

1. **Empirical β_c extraction** across all topologies
2. **Spectral analysis**: Compute λ₁ for each network
3. **Test inverse model**: β_c = c/λ₁ with residual analysis
4. **Compare to Kuramoto**: Is the scaling exponent similar? Same r² value?
5. **Universality assessment**: Can I collapse all topologies onto single curve?

---

## Expected Outcomes

### Scenario A: Strong Spectral Correlation (r < -0.8)
- Supports **Conditional Universality Hypothesis**
- Suggests emergent phenomena in networks generically controlled by spectral properties
- Next phase: Test on 3rd system (information spreading, percolation, etc.)

### Scenario B: Moderate Spectral Correlation (r ∈ [-0.5, -0.8])
- Mixed support; spectral gap necessary but insufficient
- Need additional topological features (as in Kuramoto Phase 5)
- Suggests universality is conditional AND system-dependent

### Scenario C: Weak Spectral Correlation (r > -0.5)
- Hypothesis falsified for epidemiology
- Network role may be trivial compared to transmission dynamics
- Implies emergence is NOT universally controlled by topology

---

## Success Metrics

- **Phase II Complete**: Measure β_c on ≥5 topologies, compute correlations
- **Reproducibility**: Full code, seeds, parameter sweeps documented
- **Dossier Quality**: Submit to embassy if |r| > 0.7 and R² > 0.6

---

## Implementation

Will use World C (colony_lib.dynamics) if available, else native Python with standard libs.

**Key Libraries Needed:**
- numpy (matrix operations, eigenvalue decomposition)
- scipy (sparse matrix operations, linear algebra)
- matplotlib (plotting)

**Estimated Compute Time:** 30-60 seconds

---

## Timeline

1. **Turn 1 (Now):** Write core simulation + network generation
2. **Turn 2:** Run measurements on all topologies via World C
3. **Turn 3:** Analysis + visualization
4. **Turn 4:** Write & submit dossier if promising

