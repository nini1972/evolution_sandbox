# 🏛️ World C Execution Report: SYN-062 Cell B FIX: batched-bootstrap DET vs Kuramoto r (matched RR + isometry)

* **Job ID:** `job_tencent_hy3_1795660928_c180`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `61.73` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `syn062_cellB_det_vs_r`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='syn062_cellB_det_vs_r', resume_from_job_id='job_tencent_hy3_1795660928_c180')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('syn062_cellB_det_vs_r')`.

---

## 📦 Generated Artifacts
- `SYN062_CELLB_DET_RR.png` (delivered to `world_c_results/SYN062_CELLB_DET_RR.png` and `world_c/artifacts/job_tencent_hy3_1795660928_c180/SYN062_CELLB_DET_RR.png`)
- `SYN062_CELLB_RESULTS.json` (delivered to `world_c_results/SYN062_CELLB_RESULTS.json` and `world_c/artifacts/job_tencent_hy3_1795660928_c180/SYN062_CELLB_RESULTS.json`)

---

## 📋 Execution Log Tail
```
=== TEST 1: constant-signal DET (l_min=2, main diag excluded) ===
  N=  50  DET=0.99997526  expected~0.99997526  |err|=0.00e+00
  N= 100  DET=0.99999695  expected~0.99999695  |err|=0.00e+00
  N= 200  DET=0.99999962  expected~0.99999962  |err|=0.00e+00
  N= 500  DET=0.99999998  expected~0.99999998  |err|=0.00e+00
  -> DET_const = 1 - 6/[(N-1)N(2N-1)] = 1 - O(1/N^3); ceiling=1 confirmed.

=== TEST 2: isometry invariance of DET ===
  DET_before=0.8955983377  DET_after_isometry=0.8956240695  |diff|=2.57e-05
  -> isometry invariance CONFIRMED (rotations preserve Euclidean distance).

=== TEST 3: Kuramoto coherence r vs DET (matched RR) ===
  K= 0.2  r=0.089  DET@RR0.10=1.000
  K= 0.5  r=0.138  DET@RR0.10=1.000
  K= 1.0  r=0.180  DET@RR0.10=1.000
  K= 2.0  r=0.831  DET@RR0.10=1.000
  K= 4.0  r=0.948  DET@RR0.10=0.810
  K= 8.0  r=0.992  DET@RR0.10=0.274

=== TEST 4: bootstrap DET CI @ RR=0.10, low vs high r ===
  K= 0.2  r=0.089  DET=1.0000  CI95=[0.9999,1.0000]
  K= 8.0  r=0.992  DET=0.2743  CI95=[0.2708,0.2779]

VERDICT: DET at matched RR is NOT flat across r (1.0 -> 0.27).
  BUT the drop is dominated by fixed-RR threshold geometry on near-constant
  (synchronized) signals -> DET is CONFOUNDED, not a clean order-parameter meter.
  Isometry invariance (TEST 2) confirms true blindness only for embedding isometries.

DONE. Artifacts written.
```

---
*Published autonomously by World C Embassy Bridge.*
