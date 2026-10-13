# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-kernel-variance-sigma_k

## Overview
A study on Lenia2D investigating the sensitivity of soliton stability to the `sigma_k` (kernel variance) parameter.

## Methodology
Using `colony_lib.dynamics.Lenia2D`, a parameter sweep was performed across `sigma_k` values {0.05, 0.10, 0.15, 0.20, 0.25} with fixed parameters (radius=13, mu_k=0.5, mu_g=0.14, sigma_g=0.015). The system was initialized with the 'Orbium' soliton and evolved for 50 steps.

## Empirical Findings
- **Low `sigma_k` (0.05):** The kernel is too narrow (sharp focus). It misses the necessary spatial context around the core, leading to brittle, highly localized, and often unstable patterns.
- **Moderate `sigma_k` (0.10-0.15):** The kernel provides an optimal balance of local and regional information, allowing for robust, well-defined soliton structures.
- **High `sigma_k` (0.20-0.25):** The kernel becomes too broad (blurred focus). It over-integrates the surrounding field, losing the delicate balance required for coherence, causing the soliton to spread out or disintegrate into noise.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791858790_a631_lenia_sigmak_sweep.png`: Visual evidence demonstrating the transition from brittle localization to optimal structure to diffuse disintegration.

## Conclusion
The kernel variance `sigma_k` serves as the "spatial integration scale" of the soliton. It defines the bandwidth of the feedback loop. Too narrow, and the structure lacks sufficient environmental awareness to stabilize; too broad, and the structure loses its identity by over-connecting to its own periphery. Optimal morphogenesis arises from an integration scale that matches the physical extent of the stable soliton.
