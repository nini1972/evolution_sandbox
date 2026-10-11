# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-kernel-radius

## Overview
A study on Lenia2D investigating the sensitivity of soliton stability to the `kernel_radius` parameter.

## Methodology
Using `colony_lib.dynamics.Lenia2D`, a parameter sweep was performed across `kernel_radius` values {7, 10, 13, 16, 19} with fixed growth parameters (mu_k=0.5, sigma_k=0.15, mu_g=0.135, sigma_g=0.015). The system was initialized with the 'Orbium' soliton and evolved for 50 steps.

## Empirical Findings
- **Low `radius` (7-10):** The interaction area is insufficient to maintain the soliton, leading to rapid dissolution.
- **Optimal `radius` (13):** The soliton maintains its characteristic stable morphology.
- **High `radius` (16-19):** Increased interaction radius leads to larger, more complex, or spatially unstable solitons that begin to interact with their own boundaries or become unstable.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791686087_b35a_lenia_radius_sweep.png`: Visual evidence highlighting the size-dependent stability of the Orbium soliton.

## Conclusion
The kernel radius acts as a fundamental scaling factor for structural size. Stability is strongly linked to the interaction radius relative to the initial structure size. This finding suggests that Lenia systems have an inherent "preferred scale" for self-organization, dictated by the spatial extent of the kernel.
