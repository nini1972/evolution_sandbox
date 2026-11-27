# 🏛️ World C Execution Report: Stage-4: Spectral-Topological Immunity to RQA Degeneracy (N=256 Higher Resolution) - FIXED API

* **Job ID:** `job_claude_haiku_1795748932_ad5b`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `60.11` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `stage4_spectral_topological_immunity_v1`
* **Resumed From Job:** `job_claude_haiku_1795746284_c0fb`
* **Completed Stage Slices Saved:** `1` (Last completed key: `gs_state_0`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='stage4_spectral_topological_immunity_v1', resume_from_job_id='job_claude_haiku_1795748932_ad5b')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('stage4_spectral_topological_immunity_v1')`.

---

## 📦 Generated Artifacts
- `stage4_spectral_topological_immunity_v1_state.json` (delivered to `world_c_results/stage4_spectral_topological_immunity_v1_state.json` and `world_c/artifacts/job_claude_haiku_1795748932_ad5b/stage4_spectral_topological_immunity_v1_state.json`)
- `stage4_spectral_topological_immunity_v1_horizon_certificate.json` (delivered to `world_c_results/stage4_spectral_topological_immunity_v1_horizon_certificate.json` and `world_c/artifacts/job_claude_haiku_1795748932_ad5b/stage4_spectral_topological_immunity_v1_horizon_certificate.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1795748932_ad5b/entrypoint.py", line 242, in <module>
    print(f"    DET (binary): {encoding_results[results['encoding_protocols'][0]]['u_rqa'].get('DET', 'N/A'):.4f}")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: Unknown format code 'f' for object of type 'str'
```

---
## 📋 Execution Log Tail
```
================================================================================
STAGE-4: SPECTRAL-TOPOLOGICAL IMMUNITY VERIFICATION (API FIXED)
================================================================================

[1/5] Running GS at f=0.03, k=0.062
  Step 500/15000
  Step 1000/15000
  Step 1500/15000
  Step 2000/15000
  Step 2500/15000
  Step 3000/15000
  Step 3500/15000
  Step 4000/15000
  Step 4500/15000
  Step 5000/15000
  Step 5500/15000
  Step 6000/15000
  Step 6500/15000
  Step 7000/15000
  Step 7500/15000
  Step 8000/15000
  Step 8500/15000
  Step 9000/15000
  Step 9500/15000
  Step 10000/15000
  Step 10500/15000
  Step 11000/15000
  Step 11500/15000
  Step 12000/15000
  Step 12500/15000
  Step 13000/15000
  Step 13500/15000
  Step 14000/15000
  Step 14500/15000
  Step 15000/15000
  ✓ Completed: 4 encodings tested
    u components: 0
```

---
*Published autonomously by World C Embassy Bridge.*
