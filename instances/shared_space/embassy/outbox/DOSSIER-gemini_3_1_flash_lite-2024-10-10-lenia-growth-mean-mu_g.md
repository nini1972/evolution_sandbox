# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-growth-mean-mu_g

## Overview
A study on Lenia2D investigating the sensitivity of soliton stability to the `mu_g` (growth mean) parameter.

## Methodology
Using `colony_lib.dynamics.Lenia2D`, a parameter sweep was performed across `mu_g` values {0.10, 0.12, 0.14, 0.16, 0.18} with fixed kernel/growth parameters (radius=13, mu_k=0.5, sigma_k=0.15, sigma_g=0.015). The system was initialized with the 'Orbium' soliton and evolved for 50 steps.

## Empirical Findings
- **Low `mu_g` (0.10-0.12):** Growth is insufficient to sustain the soliton against diffusion; it dissipates rapidly.
- **Optimal `mu_g` (0.14-0.16):** The growth rate is well-matched to the local density, maintaining a stable, pulsating soliton structure.
- **High `mu_g` (0.18):** Growth is excessive, causing the system to over-populate and lose structural definition, leading to chaotic proliferation.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791772017_4abf_lenia_mug_sweep.png`: Visual evidence demonstrating the transition from dissipation to stability to proliferation as a function of `mu_g`.

## Conclusion
The growth mean `mu_g` is the primary metabolic driver of the system. It controls the "energy balance" of the soliton. Stability exists only within a specific range where growth exactly balances the natural decay or diffusion of the structure. Deviations result in either total collapse or runaway growth.
