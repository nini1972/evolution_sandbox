# 🏛️ World C Execution Report: Discovery-029b: Decorrelation-controlled Rayleigh tail test (NLS integrable turbulence)

* **Job ID:** `job_glm_4_7_flash_1792638758_50c8`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `311.97` seconds

---

## 📦 Generated Artifacts
- `world_c_job_glm_4_7_flash_1792638758_50c8_it_decorrel_result.json`

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1792638758_50c8/entrypoint.py:83: RuntimeWarning: divide by zero encountered in scalar divide
  z_real = (prt.mean() - np.exp(-thr)) / (prt.std(ddof=1)/np.sqrt(len(prt)))
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1792638758_50c8/entrypoint.py", line 96, in <module>
    cert = falsification_certificate(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: falsification_certificate() got an unexpected keyword argument 'system_sizes'
```

---
## 📋 Execution Log Tail
```
--- config A (N=1024) ---
  s> 6: ratio=1.042  z_frame=+0.5  z_real=+0.52
  s> 8: ratio=0.970  z_frame=-0.1  z_real=-0.14
  s>10: ratio=1.344  z_frame=+0.4  z_real=+0.45
  s>12: ratio=0.000  z_frame=-0.3  z_real=-inf
  s>14: ratio=0.000  z_frame=-0.0  z_real=-inf
  s>16: ratio=0.000  z_frame=-0.0  z_real=-inf
  s>18: ratio=0.000  z_frame=-0.0  z_real=-inf
--- config B (N=1024) ---
  s> 6: ratio=0.000  z_frame=-974.7  z_real=-0.30
  s> 8: ratio=0.000  z_frame=-131.9  z_real=-0.83
  s>10: ratio=0.000  z_frame=-17.9  z_real=-inf
  s>12: ratio=0.000  z_frame=-2.4  z_real=-inf
  s>14: ratio=0.000  z_frame=-0.3  z_real=-inf
  s>16: ratio=0.000  z_frame=-0.0  z_real=-inf
  s>18: ratio=0.000  z_frame=-0.0  z_real=-inf
--- config C (N=4096) ---
  s> 6: ratio=0.973  z_frame=-0.6  z_real=-0.54
  s> 8: ratio=0.910  z_frame=-0.8  z_real=-0.88
  s>10: ratio=1.120  z_frame=+0.3  z_real=+0.38
  s>12: ratio=1.656  z_frame=+0.6  z_real=+0.57
  s>14: ratio=0.000  z_frame=-0.2  z_real=-inf
  s>16: ratio=0.000  z_frame=-0.0  z_real=-inf
  s>18: ratio=0.000  z_frame=-0.0  z_real=-inf
```

---
*Published autonomously by World C Embassy Bridge.*
