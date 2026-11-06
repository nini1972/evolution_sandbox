# 🏛️ World C Execution Report: Field test v11 retry: NaN-cleaned, data-driven refs, 3 remaining datasets

* **Job ID:** `job_claude_sonnet_4_5_1793931700_a72f`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `115.06` seconds

---

## 📦 Generated Artifacts
- `field_test_v11.json` (delivered to `world_c_results/field_test_v11.json` and `world_c/artifacts/job_claude_sonnet_4_5_1793931700_a72f/field_test_v11.json`)

---

### ⚠️ Errors / Warnings:
```
/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/_core/fromnumeric.py:3824: RuntimeWarning: Mean of empty slice
  return _methods._mean(a, axis=axis, dtype=dtype,
/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/_core/_methods.py:142: RuntimeWarning: invalid value encountered in scalar divide
  ret = ret.dtype.type(ret / rcount)
```

---
## 📋 Execution Log Tail
```
lynx_hare (n=21, ref=10.5):
  hit=True z0=6.61 surr mu=5.71 sd=1.43
  NONLINEAR Z = 0.63  p = 0.2750

power_grid_ieee (n=1000, ref=83.3):
  hit=True z0=3.50 surr mu=8.09 sd=2.97
  NONLINEAR Z = -1.55  p = 0.9700

belousov_zhabotinsky (n=1000, ref=250.0):
  hit=False z0=1.37 surr mu=2.72 sd=2.96
  NONLINEAR Z = -0.45  p = 0.5450

saved field_test_v11.json
```

---
*Published autonomously by World C Embassy Bridge.*
