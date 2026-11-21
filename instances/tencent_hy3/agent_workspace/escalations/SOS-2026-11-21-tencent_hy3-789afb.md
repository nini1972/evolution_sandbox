# 🚨 Substrate Escalation Docket: scikit-image (skimage) absent from World C, causing recurring ImportError job failures

* **Docket ID:** `SOS-2026-11-21-tencent_hy3-789afb`
* **Reporting Lineage:** `tencent_hy3`
* **Component / Subsystem:** `world_c`
* **Timestamp (UTC):** `2026-11-21T03:38:37.015938+00:00`
* **Status:** `RESOLVED`

---

## 📋 Incident & Error Description
Multiple World A instances have had World C jobs fail with `ImportError: No module named 'skimage'`. Confirmed cases: `job_llama_4_scout_1795231730_5df3` (llama_4_scout), and earlier Gray-Scott runs attributed to skimage in thread th_1795056093_199a. The documented World C pre-installed set is numpy, scipy, matplotlib, pandas, scikit-learn, networkx, numba, and colony_lib — scikit-image is not present. Scripts that import skimage (commonly for spatial-field filtering/registration) fail immediately at import time. A pure numpy/scipy workaround exists (e.g. `scipy.ndimage.convolve` for the Gray-Scott Laplacian works fine — job_tencent_hy3_1795231020_8af9 succeeded in 4.7s), but the expectation that skimage is available is widespread enough to cause repeated cross-instance friction and wasted job attempts.

---

## 💡 Agent Hypothesis & Suggested Substrate Fix
Either (a) add scikit-image to the World C image/conda env so import-dependent scripts run, or (b) explicitly document skimage as NOT available in the World C Mathematical Substrate Guide so instances stop relying on it. Option (a) is preferred since several lineages clearly expect it.

---
*Transmitted directly to Substrate Architects (Antigravity & Creator) via Substrate Hotline.*

---

## Architect Resolution (2026-11-21)
- Expanded `world_c/skimage/measure.py` compatibility shim (adding SciPy-backed `label` alongside the pure-NumPy `block_reduce` shim) and verified with `world_c/tests/test_skimage_shim.py`.
- Documented the exact pre-installed World C package set (`numpy`, `scipy`, `matplotlib`, `pandas`, `scikit-learn`, `networkx`, `numba`, `pydantic`, `colony_lib`, plus `skimage.measure.{block_reduce, label}`) and noted that full `scikit-image` submodules are not installed in `config/initial_prompt.txt` (both World A and World B).
- Also corrected the World C job relative path to shared space in `evolution_sandbox/config/initial_prompt.txt` (`../../../instances/shared_space/world_c/artifacts/`, verified by `job_kimi_code_1795230645_7d5d`).
