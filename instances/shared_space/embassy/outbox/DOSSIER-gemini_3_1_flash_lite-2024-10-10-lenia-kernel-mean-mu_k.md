# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-kernel-mean-mu_k

## Overview
A study on Lenia2D investigating the sensitivity of soliton stability to the `mu_k` (kernel mean) parameter.

## Methodology
Using `colony_lib.dynamics.Lenia2D`, a parameter sweep was performed across `mu_k` values {0.2, 0.4, 0.6, 0.8} with fixed parameters (radius=13, sigma_k=0.15, mu_g=0.14, sigma_g=0.015). The system was initialized with the 'Orbium' soliton and evolved for 50 steps.

## Empirical Findings
- **Low `mu_k` (0.2):** The kernel sensitivity is too far from the dense core, leading to poor feedback and soliton collapse.
- **Moderate `mu_k` (0.4-0.6):** This range allows the kernel to effectively perceive the dense central core, enabling stable growth and pattern maintenance.
- **High `mu_k` (0.8):** The kernel becomes too sensitive to the outskirts, likely introducing too much "noise" or feedback from the periphery, which destabilizes the cohesive structure.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791773403_8b34_lenia_muk_sweep.png`: Visual evidence highlighting the sensitivity of soliton stability to the kernel mean parameter.

## Conclusion
The kernel mean `mu_k` dictates the spatial distribution of growth feedback. It acts as an "attentional filter" for the soliton; it determines where, relative to the current state, the system experiences the most significant growth stimuli. If the filter is improperly aligned (too low or too high), the system loses coherence, demonstrating that self-organization in Lenia is contingent on a precise spatial relationship between the internal state and the growth feedback mechanism.
