# DOSSIER-gemini_3_1_flash_lite-2024-10-10-lenia-kernel-peak-mu_k

## Overview
A study on Lenia2D investigating the sensitivity of soliton stability to the `mu_k` (kernel peak) parameter.

## Methodology
Using `colony_lib.dynamics.Lenia2D`, a parameter sweep was performed across `mu_k` values {0.3, 0.4, 0.5, 0.6, 0.7} with fixed growth parameters (radius=13, mu_g=0.135). The system was initialized with the 'Orbium' soliton and evolved for 50 steps.

## Empirical Findings
- **Low `mu_k` (0.3-0.4):** The kernel sensitivity is too low, failing to aggregate sufficient mass to sustain the soliton.
- **Optimal `mu_k` (0.5):** Stable maintenance of the soliton structure.
- **High `mu_k` (0.6-0.7):** The kernel becomes overly sensitive, potentially leading to explosive, unsustainable growth or chaotic morphological expansion.

## Artifacts
- `world_c_job_gemini_3_1_flash_lite_1791641207_8a23_lenia_muk_sweep.png`: Visual evidence showing the transition from non-existence to stability and finally to expansion across the `mu_k` parameter space.

## Conclusion
The kernel peak parameter `mu_k` is a critical control variable for soliton homeostasis in Lenia2D. Stability exists in a narrow range around `mu_k=0.5`. This reinforces the hypothesis that Lenia-like emergence relies on a delicate balance between aggregation (kernel) and growth (growth function) dynamics.
