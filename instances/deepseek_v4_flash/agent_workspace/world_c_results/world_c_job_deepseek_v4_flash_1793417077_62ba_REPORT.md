# 🏛️ World C Execution Report: Basin volume growth + Kramers barrier law in reflexive Kuramoto (HYP-151 open question)

* **Job ID:** `job_deepseek_v4_flash_1793417077_62ba`
* **Requesting Lineage:** `deepseek_v4_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `115.63` seconds

---

## 📦 Generated Artifacts
- `world_c_job_deepseek_v4_flash_1793417077_62ba_barrier_hyp151.png`
- `world_c_job_deepseek_v4_flash_1793417077_62ba_barrier_results.json`
- `world_c_job_deepseek_v4_flash_1793417077_62ba_barrier_hyp151.png`

---

## 📋 Execution Log Tail
```
=== PART A: escape fraction vs alpha at fixed K0,sigma,N ===
 alpha=  0.5 esc_frac= 1.000  <R_final>=0.501  R*=0.00390625
 alpha= 0.75 esc_frac= 1.000  <R_final>=0.501  R*=0.024803141437003122
 alpha=  1.0 esc_frac= 0.995  <R_final>=0.499  R*=0.0625
 alpha= 1.25 esc_frac= 0.802  <R_final>=0.416  R*=0.1088188204120155
 alpha=  1.5 esc_frac= 0.325  <R_final>=0.200  R*=0.15749013123685915
 alpha=  2.0 esc_frac= 0.005  <R_final>=0.045  R*=0.25
 alpha=  3.0 esc_frac= 0.000  <R_final>=0.039  R*=0.3968502629920499
=== PART A2: K_c(alpha) threshold ===
 alpha=  0.5 K_c_emp=  0.191  K_sn_pred=  0.117
 alpha= 0.75 K_c_emp=  0.308  K_sn_pred=  0.140
 alpha=  1.0 K_c_emp=  0.502  K_sn_pred=  0.162
 alpha= 1.25 K_c_emp=  0.832  K_sn_pred=  0.185
 alpha=  1.5 K_c_emp=  1.412  K_sn_pred=  0.206
 alpha=  2.0 K_c_emp=  4.051  K_sn_pred=  0.250
 alpha=  3.0 K_c_emp= 30.000  K_sn_pred=  0.336
=== PART B: Kramers barrier law ===
 N=  100 esc_frac= 0.912 med_t= 157.360 censored=265
 N=  200 esc_frac= 0.540 med_t= 229.945 censored=1380
 N=  400 esc_frac= 0.111 med_t=     nan censored=2666
 N=  800 esc_frac= 0.004 med_t=     nan censored=2988
 N= 1600 esc_frac= 0.000 med_t=     nan censored=3000
Kramers fit slope=0.003793 (ln t vs N)

=== REPORT SUMMARY ===
PART A: escape fraction across alpha = [1.0, 1.0, 0.995, 0.802, 0.325, 0.005, 0.0]
PART B: median t_esc vs N = [157.36, 229.94, nan, nan, nan]
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
