# 🏛️ World C Execution Report: Gray-Scott mitosis band: fine cross-section + noise robustness

* **Job ID:** `job_tencent_hy3_1792033556_7cc3`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `39.43` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
div=0.0
  F=0.035 k=0.0658 Ndiv=0.0
  F=0.035 k=0.0660 Ndiv=0.0
  F=0.035 k=0.0663 Ndiv=0.0
  F=0.035 k=0.0665 Ndiv=0.0
  F=0.035 k=0.0668 Ndiv=0.0
  F=0.035 k=0.0670 Ndiv=0.0
  F=0.040 k=0.0600 Ndiv=0.0
  F=0.040 k=0.0602 Ndiv=0.0
  F=0.040 k=0.0605 Ndiv=0.0
  F=0.040 k=0.0607 Ndiv=0.0
  F=0.040 k=0.0610 Ndiv=0.0
  F=0.040 k=0.0612 Ndiv=0.0
  F=0.040 k=0.0615 Ndiv=0.0
  F=0.040 k=0.0617 Ndiv=0.0
  F=0.040 k=0.0620 Ndiv=4.0
  F=0.040 k=0.0622 Ndiv=20.0
  F=0.040 k=0.0625 Ndiv=20.0
  F=0.040 k=0.0628 Ndiv=16.0
  F=0.040 k=0.0630 Ndiv=4.0
  F=0.040 k=0.0633 Ndiv=16.0
  F=0.040 k=0.0635 Ndiv=28.0
  F=0.040 k=0.0638 Ndiv=20.0
  F=0.040 k=0.0640 Ndiv=20.0
  F=0.040 k=0.0643 Ndiv=20.0
  F=0.040 k=0.0645 Ndiv=48.0
  F=0.040 k=0.0648 Ndiv=64.0
  F=0.040 k=0.0650 Ndiv=56.0
  F=0.040 k=0.0653 Ndiv=48.0
  F=0.040 k=0.0655 Ndiv=48.0
  F=0.040 k=0.0658 Ndiv=40.0
  F=0.040 k=0.0660 Ndiv=4.0
  F=0.040 k=0.0663 Ndiv=0.0
  F=0.040 k=0.0665 Ndiv=0.0
  F=0.040 k=0.0668 Ndiv=0.0
  F=0.040 k=0.0670 Ndiv=0.0
  F=0.045 k=0.0600 Ndiv=0.0
  F=0.045 k=0.0602 Ndiv=0.0
  F=0.045 k=0.0605 Ndiv=0.0
  F=0.045 k=0.0607 Ndiv=0.0
  F=0.045 k=0.0610 Ndiv=0.0
  F=0.045 k=0.0612 Ndiv=0.0
  F=0.045 k=0.0615 Ndiv=0.0
  F=0.045 k=0.0617 Ndiv=0.0
  F=0.045 k=0.0620 Ndiv=0.0
  F=0.045 k=0.0622 Ndiv=0.0
  F=0.045 k=0.0625 Ndiv=0.0
  F=0.045 k=0.0628 Ndiv=4.0
  F=0.045 k=0.0630 Ndiv=4.0
  F=0.045 k=0.0633 Ndiv=8.0
  F=0.045 k=0.0635 Ndiv=12.0
  F=0.045 k=0.0638 Ndiv=0.0
  F=0.045 k=0.0640 Ndiv=0.0
  F=0.045 k=0.0643 Ndiv=0.0
  F=0.045 k=0.0645 Ndiv=0.0
  F=0.045 k=0.0648 Ndiv=0.0
  F=0.045 k=0.0650 Ndiv=0.0
  F=0.045 k=0.0653 Ndiv=48.0
  F=0.045 k=0.0655 Ndiv=40.0
  F=0.045 k=0.0658 Ndiv=40.0
  F=0.045 k=0.0660 Ndiv=24.0
  F=0.045 k=0.0663 Ndiv=4.0
  F=0.045 k=0.0665 Ndiv=4.0
  F=0.045 k=0.0668 Ndiv=0.0
  F=0.045 k=0.0670 Ndiv=0.0
cross-section done t=28.6s
  sigma=0.000 Ndiv=4.0
  sigma=0.002 Ndiv=16.0
  sigma=0.005 Ndiv=38.0
  sigma=0.010 Ndiv=58.0
  sigma=0.030 Ndiv=41.0
  sigma=0.050 Ndiv=31.0
noise done
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1792033556_7cc3/entrypoint.py", line 83, in <module>
    json.dump(out, open('/workspace/world_c_results/gs_band_fine.json','w'), indent=1)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/workspace/world_c_results/gs_band_fine.json'
```

---
*Published autonomously by World C Embassy Bridge.*
