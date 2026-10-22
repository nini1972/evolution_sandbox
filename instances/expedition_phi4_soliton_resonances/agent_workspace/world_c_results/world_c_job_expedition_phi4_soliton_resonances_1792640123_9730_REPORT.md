# 🏛️ World C Execution Report: Phi4_Kink_Resonance_Scan

* **Job ID:** `job_expedition_phi4_soliton_resonances_1792640123_9730`
* **Requesting Lineage:** `expedition_phi4_soliton_resonances` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `129.01` seconds

---

## 📦 Generated Artifacts
- `world_c_job_expedition_phi4_soliton_resonances_1792640123_9730_phi4_resonance_data.json`

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_phi4_soliton_resonances_1792640123_9730/entrypoint.py", line 225, in <module>
    make_figure(results, windows, "phi4_velocity_windows.png")
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_phi4_soliton_resonances_1792640123_9730/entrypoint.py", line 187, in make_figure
    plt.use('Agg')
    ^^^^^^^
AttributeError: module 'matplotlib.pyplot' has no attribute 'use'
```

---
## 📋 Execution Log Tail
```
w=0.0529 drift=1.3e-04
[ 59/89] v=0.2330 vf=0.0000 esc=0 b=3 Ew=0.0534 drift=1.3e-04
[ 60/89] v=0.2340 vf=0.1877 esc=1 b=4 Ew=0.0197 drift=9.1e-05
[ 61/89] v=0.2350 vf=0.0000 esc=0 b=4 Ew=0.0543 drift=1.4e-04
[ 62/89] v=0.2360 vf=0.0259 esc=1 b=1 Ew=0.0542 drift=8.0e-07
[ 63/89] v=0.2370 vf=0.0000 esc=0 b=6 Ew=0.0553 drift=2.5e-05
[ 64/89] v=0.2380 vf=0.1770 esc=1 b=1 Ew=0.0256 drift=7.5e-07
[ 65/89] v=0.2390 vf=0.1995 esc=1 b=1 Ew=0.0176 drift=6.6e-07
[ 66/89] v=0.2400 vf=0.2071 esc=1 b=5 Ew=0.0150 drift=7.1e-05
[ 67/89] v=0.2410 vf=0.0000 esc=0 b=5 Ew=0.0573 drift=1.0e-04
[ 68/89] v=0.2420 vf=0.2045 esc=1 b=9 Ew=0.0171 drift=1.2e-04
[ 69/89] v=0.2430 vf=0.7118 esc=1 b=16 Ew=0.0000 drift=6.4e-05
[ 70/89] v=0.2440 vf=0.0000 esc=0 b=3 Ew=0.0588 drift=1.1e-04
[ 71/89] v=0.2450 vf=0.2140 esc=1 b=1 Ew=0.0145 drift=5.2e-07
[ 72/89] v=0.2460 vf=0.0000 esc=0 b=1 Ew=0.0598 drift=1.3e-04
[ 73/89] v=0.2470 vf=0.0000 esc=0 b=21 Ew=0.0603 drift=1.3e-04
[ 74/89] v=0.2480 vf=0.2937 esc=1 b=18 Ew=0.0000 drift=6.4e-05
[ 75/89] v=0.2490 vf=0.1458 esc=1 b=1 Ew=0.0409 drift=3.9e-07
[ 76/89] v=0.2500 vf=0.0000 esc=0 b=18 Ew=0.0618 drift=4.0e-05
[ 77/89] v=0.2510 vf=0.2044 esc=1 b=1 Ew=0.0217 drift=9.7e-08
[ 78/89] v=0.2520 vf=0.2532 esc=1 b=2 Ew=0.0000 drift=1.6e-04
[ 79/89] v=0.2530 vf=0.1370 esc=1 b=1 Ew=0.0455 drift=6.7e-07
[ 80/89] v=0.2540 vf=0.2072 esc=1 b=1 Ew=0.0221 drift=3.0e-07
[ 81/89] v=0.2550 vf=0.2264 esc=1 b=1 Ew=0.0142 drift=3.2e-07
[ 82/89] v=0.2560 vf=0.0000 esc=0 b=5 Ew=0.0650 drift=3.4e-05
[ 83/89] v=0.2570 vf=0.2592 esc=1 b=4 Ew=0.0000 drift=6.5e-05
[ 84/89] v=0.2580 vf=0.1629 esc=1 b=1 Ew=0.0405 drift=1.9e-06
[ 85/89] v=0.2590 vf=0.0000 esc=0 b=10 Ew=0.0666 drift=1.5e-04
[ 86/89] v=0.2600 vf=0.0000 esc=0 b=1 Ew=0.0672 drift=2.3e-06
[ 87/89] v=0.2610 vf=0.0000 esc=0 b=1 Ew=0.0677 drift=1.6e-07
[ 88/89] v=0.2620 vf=0.0273 esc=1 b=1 Ew=0.0675 drift=1.0e-06
[ 89/89] v=0.2630 vf=0.0383 esc=1 b=1 Ew=0.0674 drift=4.5e-07
--- Metrics saved to phi4_resonance_data.json ---
```

---
*Published autonomously by World C Embassy Bridge.*
