# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-metabolic-coherence-manifold

## Overview
A study on Lenia2D investigating the coupled sensitivity of `mu_k` (kernel mean) and `mu_g` (growth mean) to identify the "Manifold of Metabolic Coherence."

## Methodology
Using `colony_lib.dynamics.Lenia2D`, a 5x5 parameter grid was explored over `mu_k` {0.3, 0.4, 0.5, 0.6, 0.7} and `mu_g` {0.12, 0.13, 0.14, 0.15, 0.16}. Fixed parameters: `radius=13`, `sigma_k=0.15`, `sigma_g=0.015`. The system was initialized with 'Orbium' and evolved for 40 steps.

## Empirical Findings
- **Coherence Manifold:** Stability is not dictated by absolute values but by the ratio/alignment between `mu_k` and `mu_g`.
- **The Diagonal Trend:** Stable morphologies track a diagonal trend where an increase in `mu_k` (higher kernel sensitivity to the core) requires a corresponding adjustment in `mu_g` (growth response threshold) to maintain homeostasis.
- **Regions of Divergence:**
    - High `mu_k` combined with low `mu_g` often leads to over-growth (explosive expansion).
    - Low `mu_k` combined with high `mu_g` often leads to starvation or decay.
- **Homeostatic Balancing:** The "Orbium" soliton resides on a narrow bridge of parameter space where feedback strength perfectly compensates for internal diffusion.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791861172_41a2_metabolic_coherence_manifold.png`: Visualization of the parameter space, showing the emergent stability corridor.

## Conclusion
"Metabolic Coherence" is a topological property of Lenia's parameter space. Stability manifests as a manifold where the kernel's perception of density (`mu_k`) and the growth response function (`mu_g`) remain in a state of reciprocal tension. This confirms that autonomous morphogenesis is governed by a self-regulating balance between environmental perception and internal growth stimuli.
