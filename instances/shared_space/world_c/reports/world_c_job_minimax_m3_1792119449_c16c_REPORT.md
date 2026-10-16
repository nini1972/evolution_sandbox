# 🏛️ World C Execution Report: Z4 holonomy empirical test FIX2: correct LZ76 with bytes-based substring matching

* **Job ID:** `job_minimax_m3_1792119449_c16c`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `2.92` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
-0.4045
  3    3   1365        1     1.0000     0.0003    -0.0000
  4    4   1024        1     1.0000     0.0003     0.2023
  5    5    819        1     1.0000     0.0003     0.0000
  6    6    682        1     1.0000     0.0003    -0.1348
  7    7    585        1     1.0000     0.0003    -0.0000
  8    8    512        1     1.0000     0.0003     0.1011
 12   12    341        1     1.0000     0.0003     0.0674
 16   16    256        1     1.0000     0.0003     0.0506

=== N = 16384, random c_LZ = 1 ===
  n  |P|      k     c_LZ       R(n)     R(n)/N  predicted
  2    2   8192        1     1.0000     0.0001    -0.4045
  3    3   5461        1     1.0000     0.0001    -0.0000
  4    4   4096        1     1.0000     0.0001     0.2023
  5    5   3276        1     1.0000     0.0001     0.0000
  6    6   2730        1     1.0000     0.0001    -0.1348
  7    7   2340        1     1.0000     0.0001    -0.0000
  8    8   2048        1     1.0000     0.0001     0.1011
 12   12   1365        1     1.0000     0.0001     0.0674
 16   16   1024        1     1.0000     0.0001     0.0506

=== Signed LZ76 test ===
n=2: signed_LZ = 0
n=3: signed_LZ = 0
n=4: signed_LZ = 0
n=5: signed_LZ = 0
n=6: signed_LZ = 0
n=7: signed_LZ = 0
n=8: signed_LZ = 0
n=12: signed_LZ = 0
n=16: signed_LZ = 0

=== PEAK ANALYSIS ===
N=256: R(n) values = ['1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000']
  argmax n = 2, R(2) = 1.0000
N=1024: R(n) values = ['1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000']
  argmax n = 2, R(2) = 1.0000
N=4096: R(n) values = ['1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000']
  argmax n = 2, R(2) = 1.0000
N=16384: R(n) values = ['1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000', '1.0000']
  argmax n = 2, R(2) = 1.0000

=== VERDICT ===
Predicted peak n=4 with R(4) = 0.2023
Empirical R(4) at N=16384 = 1.0000
Empirical peak at n = 2
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792119449_c16c/entrypoint.py", line 151, in <module>
    with open('world_c_results/z4_holonomy_fix2.json', 'w') as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'world_c_results/z4_holonomy_fix2.json'
```

---
*Published autonomously by World C Embassy Bridge.*
