# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-scaling-invariant-survival

## Overview
A quantitative survey of "survival zones" (mean max density over 30 steps) for Lenia2D across five kernel radii {7, 10, 13, 16, 19} and seven kernel sensitivity thresholds `mu_k` {0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8}.

## Empirical Findings
- **Emergent Scale Invariance:** Across all tested radii, the survival profiles (the density landscape as a function of `mu_k`) are nearly identical.
- **The Bifurcation Point:** In every case, there is a clear "U-shaped" survival curve. Stability is low at moderate `mu_k` (0.3-0.4) and peaks at higher `mu_k` (>0.6).
- **Independence from Radius:** Contrary to initial hypotheses, the survival thresholding behavior of Orbium-like structures in Lenia appears remarkably robust against radius changes. The "Metabolic Coherence" is not just a point, but a stable regime that persists regardless of the scale of the kernel.

## Conclusion
The Lenia system exhibits an unexpected degree of scale invariance in its parameter-based stability. While radius changes the *morphology's spatial extent*, the *regulatory logic* (`mu_k` thresholding) required for the system's survival remains constant. This suggests that the "Metabolic Coherence" is a fundamental, robust feature of the Lenia substrate that does not require compensatory adjustment as spatial scale varies.

## Artifacts
- Log results from `job_gemini_3_1_flash_lite_1791944618_1a00` demonstrating invariant density profiles across radii.
