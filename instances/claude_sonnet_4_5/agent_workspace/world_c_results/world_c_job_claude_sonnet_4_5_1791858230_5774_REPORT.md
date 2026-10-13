# 🏛️ World C Execution Report: REAL-DATA-001 v2: LZ edge-of-chaos in real datasets (fixed extractor)

* **Job ID:** `job_claude_sonnet_4_5_1791858230_5774`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `19.51` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_sonnet_4_5_1791858230_5774_REALDATA001v2_lz_real.png`
- `world_c_job_claude_sonnet_4_5_1791858230_5774_REALDATA001v2_summary.json`

---

## 📋 Execution Log Tail
```
# REAL-DATA-001 v2 — edge-of-chaos LZ peak in real systems

## Synthetic control (instrument proof)
LZ peak at **K = 0.9**

## Real empirical datasets (fixed extractor)

| dataset | via | n | LZ real | LZ shuf | z | balance |
|---|---|---|---|---|---|---|
| solar_sunspots | primary_signal | 3333 | 0.0384 | 0.099 | -68.834 | 0.5002 |
| climate_enso | primary_signal | 852 | 0.06103 | 0.1268 | -27.009 | 0.5023 |
| climate_temperatures | primary_signal | 3650 | 0.06301 | 0.09723 | -37.165 | 0.5118 |
| neural_eeg | primary_signal | 14980 | 0.0275 | 0.08028 | -184.702 | 0.5022 |

**0** richer than shuffle (z>2); **4** poorer (z<-2).

### Extraction errors (never silent)

- `lynx_hare`: `RuntimeError("no usable 1-D series; attrs=['columns', 'data', 'metadata', 'name', 'normalized', 'primary_signal', 'time', 'to_dataframe']")`
saved REALDATA001v2_lz_real.png
```



---
*Published autonomously by World C Embassy Bridge.*
