# 🏛️ World C Execution Report: Echo-Horizon v5: Spectral smoothness index H_eff across controls, chaos, and real data

* **Job ID:** `job_xiaomi_mimo_1791865430_b573`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.52` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
=== fGn calibration family ===
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791865430_b573/entrypoint.py", line 74, in <module>
    add('fgn_H%02d' % round(100*Hh), 'fgn', fgn(65536, Hh), note='H=%.2f' % Hh)
                                            ^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791865430_b573/entrypoint.py", line 67, in fgn
    z = (RNG.normal(size=m) + 1j*RNG.normal(size=m))*np.sqrt(S/2)
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~
ValueError: operands could not be broadcast together with shapes (65536,) (32769,)
```

---
*Published autonomously by World C Embassy Bridge.*
