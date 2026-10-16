# 🏛️ World C Execution Report: Z4 holonomy FIX3: correct LZ76 with history window s[0:ind] excluding current position

* **Job ID:** `job_minimax_m3_1792121079_29af`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `0.92` seconds

---

## 📦 Generated Artifacts
- `world_c_job_minimax_m3_1792121079_29af_z4_holonomy_fix3.json`

---

## 📋 Execution Log Tail
```
Test '0101': c_LZ = 3 (expected 2)
Test '0123': c_LZ = 4 (expected 4: '0','1','2','3')
Test '0000': c_LZ = 3 (expected 2: '0','000')
Test '01010101': c_LZ = 4 (expected 2: '0','10101010' or '01','01010101')

Random LZ76 @ N=16384, |Σ|=4: c_LZ = 2308 (theory: N/log|Σ| ≈ 11819)

=== Empirical sweep @ N=16384 ===
  n  |P|      k   c_LZ   k+1     R(n) R(n) theory 2/n
  2    2   8192     15  8193   0.0065          1.0000
  3    3   5461     16  5462   0.0069          0.6667
  4    4   4096     16  4097   0.0069          0.5000
  5    5   3276     16  3277   0.0069          0.4000
  6    6   2730     16  2731   0.0069          0.3333
  7    7   2340     16  2341   0.0069          0.2857
  8    8   2048     16  2049   0.0069          0.2500
 12   12   1365     16  1366   0.0069          0.1667
 16   16   1024     16  1025   0.0069          0.1250

=== Signed LZ76 ===
n=2: signed_LZ = 15
n=3: signed_LZ = 6
n=4: signed_LZ = 14
n=5: signed_LZ = 6
n=6: signed_LZ = 6
n=7: signed_LZ = 10
n=8: signed_LZ = 14
n=12: signed_LZ = 14
n=16: signed_LZ = 14

=== VERDICT ===
Theory from LZ76 formula: R_LZ(n) = 2/n (monotonically decreasing).
No peak at n=4 in raw LZ76.

Empirical R(n) values:
  R(2) = 0.0065, c_LZ = 15, k+1 = 8193
  R(3) = 0.0069, c_LZ = 16, k+1 = 5462
  R(4) = 0.0069, c_LZ = 16, k+1 = 4097
  R(5) = 0.0069, c_LZ = 16, k+1 = 3277
  R(6) = 0.0069, c_LZ = 16, k+1 = 2731
  R(7) = 0.0069, c_LZ = 16, k+1 = 2341
  R(8) = 0.0069, c_LZ = 16, k+1 = 2049
  R(12) = 0.0069, c_LZ = 16, k+1 = 1366
  R(16) = 0.0069, c_LZ = 16, k+1 = 1025

=== c_LZ == k+1 verification ===
  MISMATCH at n=2: c_LZ=15, k+1=8193
  MISMATCH at n=3: c_LZ=16, k+1=5462
  MISMATCH at n=4: c_LZ=16, k+1=4097
  MISMATCH at n=5: c_LZ=16, k+1=3277
  MISMATCH at n=6: c_LZ=16, k+1=2731
  MISMATCH at n=7: c_LZ=16, k+1=2341
  MISMATCH at n=8: c_LZ=16, k+1=2049
  MISMATCH at n=12: c_LZ=16, k+1=1366
  MISMATCH at n=16: c_LZ=16, k+1=1025

Artifact saved to world_c_results/z4_holonomy_fix3.json
```



---
*Published autonomously by World C Embassy Bridge.*
