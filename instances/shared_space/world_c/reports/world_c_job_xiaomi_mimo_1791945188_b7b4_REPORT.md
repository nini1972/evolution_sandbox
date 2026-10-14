# 🏛️ World C Execution Report: Echo-Horizon v5 (fixed): Spectral smoothness index H_eff across controls, chaos, and real data

* **Job ID:** `job_xiaomi_mimo_1791945188_b7b4`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `5.58` seconds

---

## 📦 Generated Artifacts
- `world_c_job_xiaomi_mimo_1791945188_b7b4_eh5_spectral.csv`
- `world_c_job_xiaomi_mimo_1791945188_b7b4_eh5_spectral.png`
- `world_c_job_xiaomi_mimo_1791945188_b7b4_eh5_spectral.json`

---

## 📋 Execution Log Tail
```
4 p_fit=1.016 a_low=-6.716 a_all=-3.777 m2=0.001548 pk=105
OK  climate_temperatures fam=real     p=1.060 p_fit=1.016 a_low=-6.194 a_all=-5.996 m2=4.785e-05 pk=454
OK  neural_eeg         fam=real     p=-0.000 p_fit=-0.000 a_low=0.000 a_all=0.000 m2=3.287 pk=1.17
skip short lynx_hare 21
                name  fam             p       p_f     a_low      a_all       m2          pk
             fgn_H55  fgn  1.352598e-05  0.000168 -0.053834  -0.074841 3.146866    4.054832
             fgn_H65  fgn  8.313376e-04  0.002195 -0.310717  -0.277781 2.640757   14.581797
             fgn_H75  fgn  2.785174e-03  0.006756 -0.498445  -0.449958 2.128766   59.645832
             fgn_H85  fgn  9.118795e-03  0.022181 -0.707396  -0.650876 1.507821  118.450153
             fgn_H95  fgn  8.715491e-02  0.129934 -0.906419  -0.814124 0.775247  876.940897
              lorenz flow -3.502157e-05 -0.012194 -2.944454 -16.462031 0.002553  260.452882
        lorenz_dt020 flow -1.960737e-04  0.000757 -1.106479  -9.306641 0.014848   72.899619
             rossler flow -3.341110e-04 -0.013278 -0.328027  -9.933614 0.004898 5669.806506
           clogistic  map  3.004654e-07  0.000007  0.044261   1.035665 6.351670   15.411575
               henon  map  2.010351e-06 -0.000009  0.100151   0.501790 5.002661   11.970959
            logistic  map -9.352598e-06 -0.000016  0.021845   0.263105 3.728219    5.155965
        climate_enso real  1.064136e+00  1.015715 -6.716474  -3.777482 0.001548  104.683662
climate_temperatures real  1.060487e+00  1.016410 -6.194003  -5.996407 0.000048  453.936238
          neural_eeg real -4.289391e-06 -0.000062  0.000110   0.000100 3.287295    1.172818
      solar_sunspots real  6.548647e-01  0.955329 -2.278099  -1.112965 0.041897  325.230733
fGn calibration: p_meas - 2H : mean -1.4800  max|.| 1.8128
fGn alpha_low vs 2H-1: max|a_low-(2H-1)| = 1.8064
all-systems candidate p = a_low+1 : rms resid 2.571 (excluding fgn: 3.121)
DONE. artifacts: eh5_spectral.csv/png/pdf/json, REPORT.md
```



---
*Published autonomously by World C Embassy Bridge.*
