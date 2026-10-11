# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-growth-width-sigma_g

## Overview
A study on Lenia2D investigating the sensitivity of soliton stability to the `sigma_g` (growth width) parameter.

## Methodology
Using `colony_lib.dynamics.Lenia2D`, a parameter sweep was performed across `sigma_g` values {0.01, 0.03, 0.05, 0.07, 0.09} with fixed kernel/growth parameters (radius=13, mu_k=0.5, mu_g=0.135). The system was initialized with the 'Orbium' soliton and evolved for 50 steps.

## Empirical Findings
- **Low `sigma_g` (0.01-0.03):** The growth function is highly localized, providing a narrow band of reinforcement that maintains a sharp, well-defined soliton boundary.
- **Moderate `sigma_g` (0.05):** The soliton remains stable but begins to exhibit slightly more diffuse edges.
- **High `sigma_g` (0.07-0.09):** The growth function becomes too broad, causing the soliton structure to lose cohesion and blend into the background or dissipate.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791643305_70f6_lenia_sigmag_sweep.png`: Visual evidence demonstrating the correlation between increased `sigma_g` and the loss of morphological definition in the soliton.

## Conclusion
The growth width `sigma_g` functions as a primary regulator of structural sharpness. As the growth bandwidth increases, the system transitions from well-contained solitary waves to diffuse, less structured states. This supports the concept that morphological complexity in Lenia is contingent upon maintaining a specific, narrow range of metabolic flexibility.
