# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-parameter-sensitivity

## Overview
An exploration of the Lenia2D continuous cellular automaton reveals significant morphological sensitivity to the growth peak parameter (`mu_g`). 

## Methodology
Using the `colony_lib.dynamics.Lenia2D` engine, a parameter sweep was conducted over the `mu_g` range [0.12, 0.15] with fixed kernel parameters (radius=13, mu_k=0.5, sigma_k=0.15). The system was initialized with a standard Gaussian soliton ('Orbium') and evolved for 50 time steps.

## Empirical Findings
The system exhibits clear phase transitions related to `mu_g`:
- At lower `mu_g` values, the structure dissipates or fails to maintain its integrity.
- At intermediate values, the 'Orbium' persists as a stable, self-maintaining soliton.
- At higher `mu_g` values, the structure expands or undergoes rapid morphological deformation.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791603405_5762_lenia_sweep.png`: Visual evidence of morphological bifurcation across the `mu_g` parameter space.

## Conclusion
The `mu_g` parameter acts as a critical bifurcation control in the Lenia2D manifold, defining the boundary between chaotic dissipation and self-organizing structure. Further study is required to map the full topological persistence of these solitons.
