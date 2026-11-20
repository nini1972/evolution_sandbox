# 🏛️ World C Execution Report: Phase III full-resolution plastic-dormancy sweep (5×9×13×5 grid, n_rep=4, T=800)

* **Job ID:** `job_expedition_plastic_dormancy_1795143399_1a9f`
* **Requesting Lineage:** `expedition_plastic_dormancy` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `262.70` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `plastic_dormancy_phase3`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='plastic_dormancy_phase3', resume_from_job_id='job_expedition_plastic_dormancy_1795143399_1a9f')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('plastic_dormancy_phase3')`.

---

## 📦 Generated Artifacts
- `plastic_dormancy_metapopulation_phase3.png` (delivered to `world_c_results/plastic_dormancy_metapopulation_phase3.png` and `world_c/artifacts/job_expedition_plastic_dormancy_1795143399_1a9f/plastic_dormancy_metapopulation_phase3.png`)
- `plastic_dormancy_metapopulation_phase3_metrics.json` (delivered to `world_c_results/plastic_dormancy_metapopulation_phase3_metrics.json` and `world_c/artifacts/job_expedition_plastic_dormancy_1795143399_1a9f/plastic_dormancy_metapopulation_phase3_metrics.json`)

---

### ⚠️ Errors / Warnings:
```
plastic_dormancy_metapopulation_phase3.py:286: UserWarning: This figure includes Axes that are not compatible with tight_layout, so results might be incorrect.
  plt.tight_layout(rect=[0, 0.03, 1, 0.96])
```

---
## 📋 Execution Log Tail
```
Script written: 12155 bytes
[1/20] rho=-0.50 rep=1/4 done
[2/20] rho=-0.50 rep=2/4 done
[3/20] rho=-0.50 rep=3/4 done
[4/20] rho=-0.50 rep=4/4 done
[5/20] rho=+0.00 rep=1/4 done
[6/20] rho=+0.00 rep=2/4 done
[7/20] rho=+0.00 rep=3/4 done
[8/20] rho=+0.00 rep=4/4 done
[9/20] rho=+0.30 rep=1/4 done
[10/20] rho=+0.30 rep=2/4 done
[11/20] rho=+0.30 rep=3/4 done
[12/20] rho=+0.30 rep=4/4 done
[13/20] rho=+0.60 rep=1/4 done
[14/20] rho=+0.60 rep=2/4 done
[15/20] rho=+0.60 rep=3/4 done
[16/20] rho=+0.60 rep=4/4 done
[17/20] rho=+0.90 rep=1/4 done
[18/20] rho=+0.90 rep=2/4 done
[19/20] rho=+0.90 rep=3/4 done
[20/20] rho=+0.90 rep=4/4 done
Sweep complete in 260.3s
Saved metrics to plastic_dormancy_metapopulation_phase3_metrics.json
Saved figure to plastic_dormancy_metapopulation_phase3.png
```

---
*Published autonomously by World C Embassy Bridge.*
