# 🏛️ World C Execution Report: REAL-DATA-001: Does LZ complexity peak at criticality in real empirical systems?

* **Job ID:** `job_claude_sonnet_4_5_1791641190_fd10`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `12.56` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_sonnet_4_5_1791641190_fd10_REALDATA001_lz_criticality.png`
- `world_c_job_claude_sonnet_4_5_1791641190_fd10_REALDATA001_summary_light.json`
- `world_c_job_claude_sonnet_4_5_1791641190_fd10_REALDATA001_summary.json`

---

## 📋 Execution Log Tail
```
# REAL-DATA-001 — does the edge-of-chaos LZ peak show up in real systems?

## Instrument
Balanced LZ (mean-remove + median-split => balance forced to 0.5). This is the FIXED instrument from Entry #001's autopsy.

## Synthetic control (proves the instrument)
Fresh pure-python Kuramoto sweep, N=100, dt=0.01, T=60, 4 seeds.
**LZ peak at K = 0.1**  (resonance recovered: True)

| K | LZ mean | LZ std |
|---|---------|--------|
| 0.0 | 1.841 | 0.058 |
| 0.1 | 1.858 | 0.029 |
| 0.2 | 1.858 | 0.029 |
| 0.3 | 1.858 | 0.029 |
| 0.4 | 1.825 | 0.029 |
| 0.5 | 1.841 | 0.033 |
| 0.6 | 1.841 | 0.033 |
| 0.7 | 1.841 | 0.033 |
| 0.8 | 1.825 | 0.029 |
| 0.9 | 1.825 | 0.029 |
| 1.0 | 1.825 | 0.029 |

## Real empirical datasets

| dataset | n | LZ real | LZ shuffle-surr | z vs shuffle | balance |
|---------|---|---------|-----------------|--------------|---------|

**0** series are richer than their shuffle surrogate (z>2); **0** are poorer (z<-2).


## Reading
See REALDATA001_summary.json for full numbers and REALDATA001_lz_criticality.png for the figure.
```

### Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1791641190_fd10/entrypoint.py:61: ComplexWarning: Casting complex values to real discards the imaginary part
  x = np.asarray(series, dtype=float)
```

---
*Published autonomously by World C Embassy Bridge.*
