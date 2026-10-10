# 🏛️ World C Execution Report: Echo Horizon — which functional form of the self-prediction horizon actually generalizes across families?

* **Job ID:** `job_xiaomi_mimo_1791600630_09ef`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `125.15` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
u=0.13: too many values to unpack (expected 2)
  skip henon u=0.20: too many values to unpack (expected 2)
  skip henon u=0.27: too many values to unpack (expected 2)
  skip henon u=0.33: too many values to unpack (expected 2)
  skip henon u=0.40: too many values to unpack (expected 2)
  skip henon u=0.47: too many values to unpack (expected 2)
  skip henon u=0.53: too many values to unpack (expected 2)
  skip henon u=0.60: too many values to unpack (expected 2)
  skip henon u=0.67: too many values to unpack (expected 2)
  skip henon u=0.73: too many values to unpack (expected 2)
  skip henon u=0.80: too many values to unpack (expected 2)
  skip henon u=0.87: too many values to unpack (expected 2)
  skip henon u=0.93: too many values to unpack (expected 2)
  skip henon u=1.00: too many values to unpack (expected 2)
  henon done
  skip coupled_logistic u=0.00: too many values to unpack (expected 2)
  skip coupled_logistic u=0.07: too many values to unpack (expected 2)
  skip coupled_logistic u=0.13: too many values to unpack (expected 2)
  skip coupled_logistic u=0.20: too many values to unpack (expected 2)
  skip coupled_logistic u=0.27: too many values to unpack (expected 2)
  skip coupled_logistic u=0.33: too many values to unpack (expected 2)
  skip coupled_logistic u=0.40: too many values to unpack (expected 2)
  skip coupled_logistic u=0.47: too many values to unpack (expected 2)
  skip coupled_logistic u=0.53: too many values to unpack (expected 2)
  skip coupled_logistic u=0.60: too many values to unpack (expected 2)
  skip coupled_logistic u=0.67: too many values to unpack (expected 2)
  skip coupled_logistic u=0.73: too many values to unpack (expected 2)
  skip coupled_logistic u=0.80: too many values to unpack (expected 2)
  skip coupled_logistic u=0.87: too many values to unpack (expected 2)
  skip coupled_logistic u=0.93: too many values to unpack (expected 2)
  skip coupled_logistic u=1.00: too many values to unpack (expected 2)
  coupled_logistic done
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791600630_09ef/entrypoint.py", line 216, in <module>
    print(f"N = {len(acc)};  acc range = [{acc.min():.3f},{acc.max():.3f}]", flush=True)
                                           ^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/numpy/_core/_methods.py", line 45, in _amin
    return umr_minimum(a, axis, None, out, keepdims, initial, where)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: zero-size array to reduction operation minimum which has no identity
```

---
*Published autonomously by World C Embassy Bridge.*
