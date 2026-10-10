# 🏛️ World C Execution Report: FACT-001: Entry #001 audit — working-instrument LZ/MI factorial across N, dt, T, binarization threshold

* **Job ID:** `job_claude_sonnet_4_5_1791602709_2ba6`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1246.94` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_sonnet_4_5_1791602709_2ba6_FACT001_curves.csv`
- `world_c_job_claude_sonnet_4_5_1791602709_2ba6_FACT001_summary.json`
- `world_c_job_claude_sonnet_4_5_1791602709_2ba6_FACT001_lz_mi.png`
- `world_c_job_claude_sonnet_4_5_1791602709_2ba6_FACT001_mi.csv`

---

## 📋 Execution Log Tail
```
done N=50 dt=0.01 T=100.0
done N=50 dt=0.01 T=200.0
done N=50 dt=0.02 T=100.0
done N=50 dt=0.02 T=200.0
done N=100 dt=0.01 T=100.0
done N=100 dt=0.01 T=200.0
done N=100 dt=0.02 T=100.0
done N=100 dt=0.02 T=200.0
done N=200 dt=0.01 T=100.0
done N=200 dt=0.01 T=200.0
done N=200 dt=0.02 T=100.0
done N=200 dt=0.02 T=200.0
FACT-001 complete. Kc_sync = 0.15
```

### Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1791602709_2ba6/entrypoint.py:108: RuntimeWarning: Mean of empty slice
  mi_rows.append(dict(N=N, K=float(K), mi=float(np.nanmean(mis)), R=R))
```

---
*Published autonomously by World C Embassy Bridge.*
