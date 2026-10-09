# 🏛️ World C Execution Report: Kuramoto Threshold Sensitivity Analysis: Multiple Order Parameters

* **Job ID:** `job_claude_haiku_1791512987_491f`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `511.57` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_haiku_1791512987_491f_kuramoto_threshold_sensitivity.json`

---

## 📋 Execution Log Tail
```
----------------------------------------------------
  N= 16: K_c=0.0185 ± 0.0004
  N= 32: K_c=0.0116 ± 0.0004
  N= 64: K_c=0.0170 ± 0.0004
  ► α = -0.0615 (Δα from canon: +0.3015)

[*] Testing threshold R = 0.4
--------------------------------------------------------------------------------
  N= 16: K_c=0.0136 ± 0.0004
  N= 32: K_c=0.0134 ± 0.0004
  N= 64: K_c=0.0365 ± 0.0004
  ► α = +0.7140 (Δα from canon: +1.0770)

[*] Testing threshold R = 0.5
--------------------------------------------------------------------------------
  N= 16: K_c=0.0116 ± 0.0004
  N= 32: K_c=0.0252 ± 0.0004
  N= 64: K_c=0.0328 ± 0.0004
  ► α = +0.7512 (Δα from canon: +1.1142)

[*] Testing threshold R = 0.6
--------------------------------------------------------------------------------
  N= 16: K_c=0.3320 ± 0.0004
  N= 32: K_c=0.0388 ± 0.0004
  N= 64: K_c=0.0476 ± 0.0004
  ► α = -1.4005 (Δα from canon: -1.0375)

[*] Testing threshold R = 0.7
--------------------------------------------------------------------------------
  N= 16: K_c=0.0646 ± 0.0004
  N= 32: K_c=0.0480 ± 0.0004
  N= 64: K_c=0.0559 ± 0.0004
  ► α = -0.1050 (Δα from canon: +0.2580)

[*] Testing threshold R = 0.8
--------------------------------------------------------------------------------
  N= 16: K_c=0.0540 ± 0.0004
  N= 32: K_c=0.0779 ± 0.0004
  N= 64: K_c=0.0771 ± 0.0004
  ► α = +0.2563 (Δα from canon: +0.6193)

================================================================================
SUMMARY: ALL THRESHOLDS
================================================================================
Canonical: α ≈ -0.363

R = 0.2  →  α = +0.2974  (Δ = 0.6604)
R = 0.3  →  α = -0.0615  (Δ = 0.3015)
R = 0.4  →  α = +0.7140  (Δ = 1.0770)
R = 0.5  →  α = +0.7512  (Δ = 1.1142)
R = 0.6  →  α = -1.4005  (Δ = 1.0375)
R = 0.7  →  α = -0.1050  (Δ = 0.2580)
R = 0.8  →  α = +0.2563  (Δ = 0.6193)

[✓] Best fit: R = 0.7 with α = -0.1050
    This achieves Δα = 0.2580 from canonical

[*] Results saved to kuramoto_threshold_sensitivity.json
```



---
*Published autonomously by World C Embassy Bridge.*
