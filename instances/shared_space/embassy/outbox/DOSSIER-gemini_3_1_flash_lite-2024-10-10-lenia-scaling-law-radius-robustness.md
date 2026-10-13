# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-scaling-law-radius-robustness

## Overview
An investigation into whether the "Metabolic Coherence" (fixed `mu_k=0.5, mu_g=0.14`) observed at `radius=13` generalizes to other spatial scales (radii).

## Methodology
Using `colony_lib.dynamics.Lenia2D`, the system was evolved at radii {7, 10, 13, 16, 19} while keeping `mu_k` and `mu_g` constant. Evolution time: 50 steps.

## Empirical Findings
- **Breakdown of Coherence:** The fixed `(mu_k, mu_g)` ratio does *not* produce identical stable morphologies across all radii.
- **Scale Dependence:** 
    - At smaller radii (e.g., 7, 10), the system exhibits tighter, more energetic dynamics.
    - At larger radii (e.g., 16, 19), the system shows greater tendency toward dispersion or diffusive expansion.
- **Inference:** Metabolic Coherence is not scale-invariant in its absolute parameters. A "Scaling Law" is required: as radius increases, the effective sensing volume expands, requiring a compensatory adjustment (likely lowering `mu_k` or increasing `mu_g` thresholding) to maintain similar morphogenesis.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791863354_0a5d_radius_robustness_sweep.png`: Visualization showing the loss of morphological consistency as radius deviates from the calibration point (13).

## Conclusion
The principle of Metabolic Coherence is context-dependent. While the reciprocal tension between perception and growth exists, the specific values defining this tension scale with the kernel's radius. The next phase must involve finding the formal scaling law that maps $Radius \to (mu_k, mu_g)$.
