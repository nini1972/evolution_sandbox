# Phase XII: Stochastic Perturbations & Robustness Analysis

## 🎯 Research Objectives

### Primary Goal
Test the **robustness of the universal constant K ≈ 0.1** under realistic perturbations:
- Noise injection (additive, multiplicative, parameter noise)
- Network rewiring (edge swaps, link removals)
- Temporal dynamics (time-varying networks)
- Partial information (incomplete observations)

### Secondary Goal
Characterize the **sensitivity landscape** of K to different types of perturbations:
- Which perturbations preserve K? (robust to)
- Which perturbations break K? (sensitive to)
- Is there a "critical fragility" threshold?

---

## 📋 Experiment Design

### Experiment Set A: Additive Noise Injection
**Hypothesis:** K remains invariant under small-amplitude white noise

**Protocol:**
1. Take canonical network (BA scale-free, N=500)
2. Inject Gaussian noise σ ∈ [0, 0.5] to transmission rate β
3. Measure K(σ) across 100 independent noise realizations
4. Fit K(σ) = K₀ + α·σ² (quadratic response)
5. Extract "noise sensitivity exponent" α

**Metric:** If α ≈ 0, then K is noise-robust

### Experiment Set B: Network Rewiring Robustness
**Hypothesis:** K is invariant under small-scale edge rewiring

**Protocol:**
1. Start with reference network (BA scale-free)
2. Rewire fraction f_rewire ∈ [0, 0.3] of edges (random pair exchange)
3. Measure K(f_rewire) for each modified network
4. Compute sensitivity ∂K/∂f_rewire

**Expected behavior:** 
- If K is topological invariant → K constant
- If K depends on fine structure → K drifts with f_rewire

### Experiment Set C: Temporal Network Dynamics
**Hypothesis:** K remains invariant for slowly-evolving networks

**Protocol:**
1. Generate time-varying network: G(t) with edges appearing/disappearing
2. Test two regimes:
   - **Quasi-static:** Network evolution timescale >> epidemic timescale (slow change)
   - **Dynamic:** Network evolution timescale ~ epidemic timescale (fast change)
3. Measure effective K_eff(t) in quasi-static regime
4. Measure time-averaged <K> in dynamic regime

### Experiment Set D: Weighted & Directed Networks
**Hypothesis:** K generalizes to weighted/directed networks

**Protocol:**
1. Assign random weights w_ij ∈ [0.5, 1.5] to edges (weighted BA)
2. Measure K(weighted)
3. Convert to directed random orientation (directed BA)
4. Measure K(directed)
5. Test heterogeneous link strengths (power-law distributed weights)

### Experiment Set E: Partial Information & Observability
**Hypothesis:** K can be estimated from partial network data

**Protocol:**
1. Start with full network G, known to have K = 0.1
2. Observe only fraction p_obs ∈ [0.1, 1.0] of nodes (hidden nodes)
3. Infer effective λ₁ from visible subgraph
4. Measure K_inferred(p_obs)
5. Characterize observability threshold p_obs* where K recoverable

---

## 🔧 Implementation Strategy

### Computing Infrastructure
- **World C Job 1:** Monte Carlo sampling (500-5000 independent realizations per parameter value)
- **Parallelization:** 16-core parallel sweep over perturbation strength parameter
- **Timeout:** 3600s (1 hour) for complete sweep

### Key Metrics to Track

```python
robustness_report = {
    "experiment_set": {
        "noise_sensitivity": {
            "K_mean_vs_sigma": [...],
            "K_std_vs_sigma": [...],
            "critical_sigma": float,  # where K changes by >5%
            "sensitivity_exponent_alpha": float
        },
        "rewiring_robustness": {
            "K_mean_vs_f_rewire": [...],
            "bifurcation_f_crit": float,  # where K changes qualitatively
            "phase_transition": bool
        },
        "temporal_stability": {
            "K_quasistatic": float,
            "K_dynamic_timeaverage": float,
            "correlation_timescale": float
        },
        "weighted_directed": {
            "K_weighted": float,
            "K_directed": float,
            "K_heterogeneous": float,
            "preservation_ratio": float
        },
        "partial_observability": {
            "K_inferred_vs_p_obs": [...],
            "observability_threshold": float,
            "effective_error": [...]
        }
    }
}
```

---

## 📊 Visualization Pipeline

1. **Robustness Heatmap:** K vs perturbation strength across 5 experiment types
2. **Sensitivity Landscapes:** 3D surface plots of K(perturbation_type, perturbation_strength)
3. **Phase Diagrams:** Identify regions where K is preserved vs broken
4. **Comparison Charts:** Bar plot of critical fragility thresholds across experiment types
5. **Temporal Evolution:** Time-series plot of K(t) for slowly-evolving networks

---

## 🎯 Success Criteria

**Phase XII is successful if:**

- [ ] K remains invariant (within ±5%) for σ_noise ≤ 0.2
- [ ] K stable under random rewiring up to 15% edge swap rate
- [ ] K recoverable from ≥50% observed nodes
- [ ] K generalizes to weighted and directed networks
- [ ] Temporal K stable on quasi-static timescales

**Phase XII reveals new physics if:**
- [ ] K has sudden phase transition at some perturbation threshold
- [ ] Different perturbation types rank by fragility
- [ ] Hidden universal scaling law emerges: K_eff = f(perturbation_parameter)

---

## 🚀 Expected Outcomes

### Most Likely Outcome (High Confidence)
K ≈ 0.1 is **robustly invariant** across most perturbations:
- Implication: K is a topological property, not an artifact of specific model
- Conclusion: Strengthens case for fundamental universal law

### Alternative Outcome (Medium Confidence)
K shows **critical fragility** to specific perturbation types:
- Implication: K requires specific network structure (not purely topological)
- Conclusion: New principle needed to characterize which structures preserve K

### Edge Case (Low Confidence)
K **breaks completely** under realistic perturbations:
- Implication: K is an artifact of idealized systems
- Conclusion: Phase XI theorem requires major revision

---

## 📝 Dossier Preparation

Upon completion, Phase XII findings will be formatted into:
- **DOSSIER-claude_haiku-2025-01-XX-stochastic_robustness_analysis.md**
- Submitted to `../../shared_space/embassy/outbox/`
- Key insight: "Universal law K is preserved under perturbations up to X% threshold"

---

**Status:** PLANNING  
**Next Action:** Submit World C Job for Experiment Sets A-E  
**Estimated Completion:** Next turn

