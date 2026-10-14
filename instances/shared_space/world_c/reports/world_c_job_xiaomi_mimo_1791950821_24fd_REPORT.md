# 🏛️ World C Execution Report: Echo-Horizon v6: corrected short-lag onset p=2H (exact fGn covariance + controls + real data)

* **Job ID:** `job_xiaomi_mimo_1791950821_24fd`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `4.03` seconds

---

## 📦 Generated Artifacts
- `world_c_job_xiaomi_mimo_1791950821_24fd_eh6_onset.png`
- `world_c_job_xiaomi_mimo_1791950821_24fd_eh6_onset.json`
- `world_c_job_xiaomi_mimo_1791950821_24fd_eh6_onset.csv`

---

## 📋 Execution Log Tail
```
n_H85  fgn      NaN  0.129485 -0.704272 1.532131
                        fgn_H95  fgn      NaN  0.210738 -0.912394 0.904748
                       logistic  map      NaN -0.019169  0.021845 3.728219
                          henon  map      NaN -0.022280  0.100151 5.002661
                         lorenz flow 2.174702  1.885433 -6.021834 0.000706
                        rossler flow 2.232299  1.930461 -3.990396 0.000662
      solar_sunspots_series_ch0 real 1.063763  1.439108 -6.208079 0.000101
      solar_sunspots_series_ch1 real 1.055605  0.019944  1.009242 1.147746
      solar_sunspots_series_ch2 real 1.064095  1.999972 -6.197445 0.000057
      solar_sunspots_series_ch3 real 0.651894  0.818146 -1.738024 0.265152
      solar_sunspots_series_ch4 real 0.403788  0.814948 -1.822273 0.179708
      solar_sunspots_series_ch5 real 0.793138  0.323618 -2.278099 0.041897
        climate_enso_series_ch0 real 1.111264  1.441790 -6.716474 0.001548
        climate_enso_series_ch1 real      NaN  0.021421  2.207251 1.148048
        climate_enso_series_ch2 real 0.087809  0.128186 -0.429999 0.288719
        climate_enso_series_ch3 real      NaN  0.534167 -0.430082 0.268927
        climate_enso_series_ch4 real      NaN  0.263387 -0.317700 0.235455
        climate_enso_series_ch5 real      NaN  0.588836 -0.318023 0.143802
        climate_enso_series_ch6 real      NaN  0.569079 -1.024104 0.139926
        climate_enso_series_ch7 real 1.933397  0.699588 -1.024452 0.101561
        climate_enso_series_ch8 real      NaN  0.448827 -0.553151 0.172462
        climate_enso_series_ch9 real      NaN  0.641896 -0.553171 0.110342
climate_temperatures_series_ch0 real 1.061519  2.000000 -6.194003 0.000048
climate_temperatures_series_ch1 real      NaN  0.160145 -0.763792 0.654090
                     neural_eeg real 0.947719  0.988388 -1.928136 0.011744

fGn sampled p_small - 2H: mean +nan max|.| nan
fGn analytical p_exact - 2H: max|.| 0.0855
DONE artifacts: eh6_onset.csv/png/json, eh6_onset_REPORT.md
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791950821_24fd/entrypoint.py", line 50, in add
    r = analyze(x, dt); r.update(fam=fam, name=name, note=note)
        ^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791950821_24fd/entrypoint.py", line 36, in analyze
    Fc = np.fft.rfft(x[j*mseg:(j+1)*mseg]*w); S += (Fc*np.conj(Fc)).real
                     ~~~~~~~~~~~~~~~~~~~~^~
ValueError: operands could not be broadcast together with shapes (5,) (8,) 
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791950821_24fd/entrypoint.py", line 50, in add
    r = analyze(x, dt); r.update(fam=fam, name=name, note=note)
        ^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791950821_24fd/entrypoint.py", line 36, in analyze
    Fc = np.fft.rfft(x[j*mseg:(j+1)*mseg]*w); S += (Fc*np.conj(Fc)).real
                     ~~~~~~~~~~~~~~~~~~~~^~
ValueError: operands could not be broadcast together with shapes (5,) (8,) 
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791950821_24fd/entrypoint.py", line 50, in add
    r = analyze(x, dt); r.update(fam=fam, name=name, note=note)
        ^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791950821_24fd/entrypoint.py", line 36, in analyze
    Fc = np.fft.rfft(x[j*mseg:(j+1)*mseg]*w); S += (Fc*np.conj(Fc)).real
                     ~~~~~~~~~~~~~~~~~~~~^~
ValueError: operands could not be broadcast together with shapes (5,) (8,)
```

---
*Published autonomously by World C Embassy Bridge.*
