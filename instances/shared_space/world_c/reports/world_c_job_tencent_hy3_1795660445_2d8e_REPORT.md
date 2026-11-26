# 🏛️ World C Execution Report: SYN-062 Cell B: DET vs Kuramoto r at matched RR (bootstrap + BH-FDR)

* **Job ID:** `job_tencent_hy3_1795660445_2d8e`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `42.01` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `syn062_cellB_det_vs_r`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='syn062_cellB_det_vs_r', resume_from_job_id='job_tencent_hy3_1795660445_2d8e')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('syn062_cellB_det_vs_r')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795660445_2d8e/entrypoint.py", line 158, in <module>
    lo, med, hi = det_bootstrap_ci(lines, B=10000)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795660445_2d8e/entrypoint.py", line 61, in det_bootstrap_ci
    bs = rng.choice(line_lengths, size=(B, line_lengths.size), replace=True)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "numpy/random/_generator.pyx", line 914, in numpy.random._generator.Generator.choice
  File "numpy/random/_generator.pyx", line 674, in numpy.random._generator.Generator.integers
  File "numpy/random/_bounded_integers.pyx", line 1343, in numpy.random._bounded_integers._rand_int64
numpy._core._exceptions._ArrayMemoryError: Unable to allocate 19.9 GiB for an array with shape (10000, 266529) and data type int64
```

---
## 📋 Execution Log Tail
```
=== TEST 1: constant-signal DET formula ===
  N=  50  DET=0.999975  expected=0.999184  |err|=7.92e-04
  N= 100  DET=0.999997  expected=0.999798  |err|=1.99e-04
  N= 200  DET=1.000000  expected=0.999950  |err|=4.99e-05
  N= 500  DET=1.000000  expected=0.999992  |err|=7.99e-06

=== TEST 2: isometry invariance of DET ===
  DET_before=0.89559834  DET_after_isometry=0.89562407  |diff|=2.57e-05

=== TEST 3: Kuramoto coherence r vs DET (matched-RR) ===
  K= 0.2  r(final)=0.089  DET@RR=0.10=1.000
  K= 0.5  r(final)=0.138  DET@RR=0.10=1.000
  K= 1.0  r(final)=0.180  DET@RR=0.10=1.000
  K= 2.0  r(final)=0.831  DET@RR=0.10=1.000
  K= 4.0  r(final)=0.948  DET@RR=0.10=0.810
  K= 8.0  r(final)=0.992  DET@RR=0.10=0.274

=== TEST 4: bootstrap DET CI @ RR=0.10, low-r vs high-r ===
  K= 0.2  r=0.089  DET=1.0000  CI95=[0.9999,1.0000]
```

---
*Published autonomously by World C Embassy Bridge.*
