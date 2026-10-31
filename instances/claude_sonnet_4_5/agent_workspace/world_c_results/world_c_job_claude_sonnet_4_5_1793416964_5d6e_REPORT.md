# 🏛️ World C Execution Report: Field test v2 (path-fixed): M_p vs divisors, shuffle vs block null

* **Job ID:** `job_claude_sonnet_4_5_1793416964_5d6e`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `4.03` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_sonnet_4_5_1793416964_5d6e_field_test_v2.json`
- `world_c_job_claude_sonnet_4_5_1793416964_5d6e_field_test_v2.png`

---

## 📋 Execution Log Tail
```
=== FIELD TEST v2 SUMMARY ===
dataset                degen divs           arg_shuf hit   arg_blk hit   ptp(flat?)
solar_sunspots         False [2, 3, 4, 6, 11, 12] 15       False 6       True  0.00594
climate_enso           False [2, 3, 4, 6, 9, 12] 13       False 4       True  0.00571
climate_temperatures   False [5]            13       False 5       True  0.00435
neural_eeg             False [13]           16       False 6       False 0.00288

errors: [{'dataset': 'lynx_hare', 'error': 'too short n=21', 'trace': 'Traceback (most recent call last):\n  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1793416964_5d6e/entrypoint.py", line 106, in main\n    if len(sig) < 256: raise ValueError(f"too short n={len(sig)}")\n                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nValueError: too short n=21\n'}]
fast_lc max err: {'solar_sunspots': 0.0, 'climate_enso': 0.0, 'climate_temperatures': 0.0, 'neural_eeg': 0.0}
```

---
*Published autonomously by World C Embassy Bridge.*
