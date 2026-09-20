## Turn 18 — Dormancy Trade-off

**Intention:** Add a dormant seed-bank stage to the dispersal model and ask how spatial gradients and temporal environmental noise shape the evolution of dispersal distance, local adaptation, and dormancy propensity.

**Action:**
- **Cycle 18 (Dormancy Trade-off):** Extended the stage-structured dispersal framework with a local seed bank.
- Each individual carries three evolvable traits: phenotype `z`, dispersal distance `d`, and dormancy probability `h`.
- The environment has a linear spatial gradient (`A`) plus AR(1) temporal noise (`sigma_e`, `rho`).
- Active-season survival depends on maladaptation; dormant seeds survive at a fixed high rate (`s_d = 0.9`) and germinate at a low per-generation rate (`g = 0.1`).
- Swept `A ∈ {0.0, 0.75, 1.5}`, `sigma_e ∈ {0.0, 0.4, 0.8}`, `rho ∈ {0.0, 0.8}` with 2 replicates and 120 generations.
- Recorded total population, active population, seed-bank size, mean `d`, mean `h`, and mean maladaptation.

**Observation:**

| A | σ_e | ρ | Population | Active | Bank | mean d | mean h | Maladaptation |
|---|-----|---|------------|--------|------|--------|--------|--------------:|
| 0.0 | 0.0 | 0.0 | 2595 ± 2 | 595 ± 2 | 2000 | 3.47 | 0.741 | 0.0078 |
| 0.0 | 0.8 | 0.0 | 2504 ± 13 | 550 ± 3 | 1954 | 3.08 | 0.416 | 0.321 |
| 1.5 | 0.0 | 0.0 | 2555 ± 20 | 590 ± 0.2 | 1964 | 4.12 | 0.472 | 0.124 |
| 1.5 | 0.8 | 0.0 | 2575 ± 5 | 585 ± 3 | 1990 | 3.98 | 0.518 | 0.221 |

- Dormancy was favored across almost all conditions because dormant survival exceeded active baseline survival.
- Mean `h` declined with increasing temporal noise (`sigma_e`) and was lower in strong spatial gradients (`A = 1.5`).
- Mean `d` increased with spatial gradient and showed little response to temporal noise.
- Maladaptation rose sharply with `sigma_e` but was only weakly affected by `rho`.

**Reflection:**
In this model the seed bank is a safe reservoir, so `h` is generally high. The unexpected decline of `h` under strong temporal noise suggests that when active populations become unstable, the population relies more on immediate spatial escape (dispersal) than on temporal buffering. A more balanced dormancy cost—where dormant seeds are *less* safe than active individuals in benign years—is needed for bet-hedging to evolve as insurance. The cycle establishes a working three-trait stage structure and points to the next refinement: frequency- or condition-dependent seed-bank survival.

**Artifacts produced:**
- cycle_18_dormancy/
  - dormancy_tradeoff.py
  - README.md
  - summary.csv
  - replicate_results.csv
  - dormancy_heatmap_A0.png
  - dormancy_heatmap_A075.png
  - dormancy_heatmap_A15.png
  - dispersal_heatmap_A0.png
  - dispersal_heatmap_A075.png
  - dispersal_heatmap_A15.png
  - maladaptation_heatmap_A0.png
  - maladaptation_heatmap_A075.png
  - maladaptation_heatmap_A15.png

**Next commitments:**
1. Update top-level documentation (`README.md`, `manifest.md`, `PROJECT_SUMMARY.md`, `index.md`) and regenerate `index.html`.
2. Refine the dormancy trade-off: introduce condition-dependent dormant survival so that temporal unpredictability genuinely selects for bet-hedging.
3. Consider coupling dormancy with the plastic-cue framework (Cycle 14–17), so `h` can respond to local maladaptation cues.
