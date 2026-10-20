# 🏛️ World C Execution Report: EMP135_AUDIT: period-4 replication, FT-surrogate discrimination, LZ cross-coordinate dissociation

* **Job ID:** `job_claude_sonnet_4_5_1792463325_f493`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `14.10` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_sonnet_4_5_1792463325_f493_emp135_audit.png`
- `world_c_job_claude_sonnet_4_5_1792463325_f493_emp135_audit_results.json`
- `world_c_job_claude_sonnet_4_5_1792463325_f493_summary.json`

---

## 📋 Execution Log Tail
```
0.030
  bc=periodic form=additive seed=2 div=False C4_raw=-0.003 C4_bin=+0.000 C4_sym=-0.024
  bc=periodic form=additive seed=3 div=False C4_raw=-0.004 C4_bin=-0.001 C4_sym=+0.010
  bc=periodic form=impladed seed=1 div=False C4_raw=-0.029 C4_bin=-0.002 C4_sym=-0.007
  bc=periodic form=impladed seed=2 div=False C4_raw=-0.011 C4_bin=-0.002 C4_sym=-0.018
  bc=periodic form=impladed seed=3 div=False C4_raw=-0.027 C4_bin=-0.003 C4_sym=-0.016
  bc=fixed    form=additive seed=1 div=False C4_raw=-0.005 C4_bin=+0.001 C4_sym=-0.009
  bc=fixed    form=additive seed=2 div=False C4_raw=+0.000 C4_bin=-0.002 C4_sym=-0.036
  bc=fixed    form=additive seed=3 div=False C4_raw=-0.003 C4_bin=-0.001 C4_sym=+0.084
  bc=fixed    form=impladed seed=1 div=False C4_raw=-0.026 C4_bin=-0.003 C4_sym=-0.036
  bc=fixed    form=impladed seed=2 div=False C4_raw=-0.021 C4_bin=-0.001 C4_sym=-0.004
  bc=fixed    form=impladed seed=3 div=False C4_raw=-0.035 C4_bin=+0.015 C4_sym=+0.014
  treaty C4 target = 0.257 (threshold 0.1); configs with |C4|>0.1: 0/12

=== Part B: FT-surrogate discrimination ===
  real C4=-0.000 vs FT-sur -0.000±0.000 z=-0.58
  AR(4) period-4-pole control: C4=-0.061 z=-0.25 (linear, must fail prediction test)
  pred: h1=0.0000 h4=0.0000 gain=-3.6% z=+5.35 | FT-sur gain=-103.2%±18.7% | AR gain=-695.3%

=== Part C: LZ cross-coordinate on same substrate ===
  N=256: c_sub=31 c_rand=59.3 R=0.523
  N=512: c_sub=45 c_rand=101.4 R=0.444
  N=1024: c_sub=63 c_rand=175.7 R=0.359
  N=2048: c_sub=90 c_rand=310.3 R=0.290
  N=4096: c_sub=109 c_rand=552.9 R=0.197
  R(n) ramp: n2:0.636 n3:0.689 n4:0.714 n5:0.701 n6:0.740 n7:0.744 n8:0.768 n12:0.758 n16:0.819
  argmax n=16, R(4)=0.714

SUMMARY: {
  "replication_hits": 0,
  "replication_stable": 12,
  "C4_real": -0.00047738295318888735,
  "z_c4": -0.5759522950343641,
  "C4_ar": -0.06068019873125109,
  "gain": -0.03552219370180756,
  "z_gain": 5.345559811117889,
  "gain_ar": -6.952760326923298,
  "lz_R4": 0.7142857142857143,
  "lz_argmax": 16
}
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
