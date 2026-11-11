# 🏛️ World C Execution Report: Network Topology Phase Diagrams: K-sigma Scan (Ratified Kc)

* **Job ID:** `job_poolside_laguna_1793733618_3e1b`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.34` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_phase_diagram_v5`
* **Resumed From Job:** `job_poolside_laguna_1793696363_4a90`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_phase_diagram_v5', resume_from_job_id='job_poolside_laguna_1793733618_3e1b')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_phase_diagram_v5')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_poolside_laguna_1793733618_3e1b\entrypoint.py", line 164, in <module>
    main()
    ~~~~^^
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_poolside_laguna_1793733618_3e1b\entrypoint.py", line 116, in main
    lambda_2 = spectral_gap(G)
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_poolside_laguna_1793733618_3e1b\entrypoint.py", line 66, in spectral_gap
    eigvals = eigsh(L.asfptype(), k=2, which='SM', return_eigenvectors=False)
                    ^^^^^^^^^^
AttributeError: 'csr_array' object has no attribute 'asfptype'. Did you mean: 'astype'?
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
