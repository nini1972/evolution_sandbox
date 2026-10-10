# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-kernel-radius-scaling

## Overview
A follow-up study on Lenia2D explores the dependency of soliton stability on the `kernel_radius` parameter. 

## Methodology
Using `colony_lib.dynamics.Lenia2D`, a parameter sweep was performed across `kernel_radius` values {5, 9, 13, 17, 21} with fixed growth peak (`mu_g`=0.135). The system was initialized with the 'Orbium' soliton and evolved for 50 steps.

## Empirical Findings
- **Small Radii (5-9):** The kernel range is insufficient to maintain the soliton structure, leading to rapid decay or fragmentation.
- **Intermediate Radii (13-17):** The soliton maintains structural coherence.
- **Large Radii (21+):** The interaction scale becomes too broad, causing the structure to expand and lose its localized compact form, potentially leading to instability or rapid, diffuse growth.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791638662_9cae_lenia_radius_sweep.png`: Visual evidence of the radius-dependency on soliton existence.

## Conclusion
Soliton stability in Lenia2D is constrained by a "Goldilocks zone" of interaction radii. This suggests the existence of a scaling relationship between structural size and the interaction kernel extent, which is fundamental to the emergence of localized, self-sustaining entities in this dynamical system.
