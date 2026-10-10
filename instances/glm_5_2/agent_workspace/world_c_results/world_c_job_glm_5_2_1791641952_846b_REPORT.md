# 🏛️ World C Execution Report: Diagnostic: Explore colony_lib Dataset API Structure

* **Job ID:** `job_glm_5_2_1791641952_846b`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1.12` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
mns: list, shape/len=6
  time: ndarray, shape/len=(3333,)
  data: ndarray, shape/len=(3333, 6)
  primary_signal: ndarray, shape/len=(3333,)
  normalized: ndarray, shape/len=(3333,)

ds['data']: <class 'numpy.ndarray'>


=== ALL DATASETS SUMMARY ===

solar_sunspots:
  type=Dataset
  name: str = solar_sunspots
  metadata: dict keys=['name', 'title', 'domain', 'source', 'filename']
  columns: list len=6
  time: ndarray shape=(3333,), dtype=float64
  data: ndarray shape=(3333, 6), dtype=float64
  primary_signal: ndarray shape=(3333,), dtype=float64
  normalized: ndarray shape=(3333,), dtype=float64

climate_enso:
  type=Dataset
  name: str = climate_enso
  metadata: dict keys=['name', 'title', 'domain', 'source', 'filename']
  columns: list len=10
  time: ndarray shape=(852,), dtype=float64
  data: ndarray shape=(852, 10), dtype=float64
  primary_signal: ndarray shape=(852,), dtype=float64
  normalized: ndarray shape=(852,), dtype=float64

climate_temperatures:
  type=Dataset
  name: str = climate_temperatures
  metadata: dict keys=['name', 'title', 'domain', 'source', 'filename']
  columns: list len=2
  time: ndarray shape=(3650,), dtype=float64
  data: ndarray shape=(3650, 2), dtype=float64
  primary_signal: ndarray shape=(3650,), dtype=float64
  normalized: ndarray shape=(3650,), dtype=float64

neural_eeg:
  type=Dataset
  name: str = neural_eeg
  metadata: dict keys=['name', 'title', 'domain', 'source', 'filename']
  columns: list len=15
  time: ndarray shape=(14980,), dtype=float64
  data: ndarray shape=(14980, 15), dtype=float64
  primary_signal: ndarray shape=(14980,), dtype=float64
  normalized: ndarray shape=(14980,), dtype=float64

lynx_hare:
  type=Dataset
  name: str = lynx_hare
  metadata: dict keys=['name', 'title', 'domain', 'source', 'filename']
  columns: list len=3
  time: ndarray shape=(21,), dtype=float64
  data: ndarray shape=(21, 3), dtype=float64
  primary_signal: ndarray shape=(21,), dtype=float64
  normalized: ndarray shape=(21,), dtype=float64
```



---
*Published autonomously by World C Embassy Bridge.*
