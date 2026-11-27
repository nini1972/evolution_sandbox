# 🏛️ World C Execution Report: R30-Empirical: Resonance Gap Law on Real Coupled Systems (Corrected API)

* **Job ID:** `job_glm_5_2_1795748502_561c`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.47` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `r30_empirical_resonance_gap`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='r30_empirical_resonance_gap', resume_from_job_id='job_glm_5_2_1795748502_561c')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('r30_empirical_resonance_gap')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795748502_561c/entrypoint.py", line 149, in <module>
    sub_b_interp = np.interp(t_new, t_old, sub_b)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/lib/_function_base_impl.py", line 1675, in interp
    return interp_func(x, xp, fp, left, right)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: fp and xp are not of the same length.
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795748502_561c/entrypoint.py", line 214, in <module>
    nino34 = enso_df['nino34_sst'].values.astype(float)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'numpy.ndarray' object has no attribute 'values'
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795748502_561c/entrypoint.py", line 289, in <module>
    lynx = lh_df['lynx'].values.astype(float)
           ^^^^^^^^^^^^^^^^^^^^
AttributeError: 'numpy.ndarray' object has no attribute 'values'
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795748502_561c/entrypoint.py", line 512, in <module>
    Cs_base = [r['peak_cc_uncoupled'] for r in gr]
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795748502_561c/entrypoint.py", line 512, in <listcomp>
    Cs_base = [r['peak_cc_uncoupled'] for r in gr]
               ~^^^^^^^^^^^^^^^^^^^^^
KeyError: 'peak_cc_uncoupled'
```

---
## 📋 Execution Log Tail
```
: CC_coupled=492.1543, CC_base=488.9190, gain=3.2353
  N_gap=  2: CC_coupled=492.2534, CC_base=484.2439, gain=8.0095
  N_gap=  5: CC_coupled=492.1242, CC_base=483.1127, gain=9.0116
  N_gap= 10: CC_coupled=495.4188, CC_base=483.7316, gain=11.6872
  N_gap= 20: CC_coupled=494.7538, CC_base=482.4862, gain=12.2676
  N_gap= 50: CC_coupled=494.9406, CC_base=460.0416, gain=34.8991
  N_gap=100: CC_coupled=494.9406, CC_base=460.0416, gain=34.8991
  Gap law fit: C_max=37.599557024782186, tau=29.31966223379055, R²=0.8982
  Power law fit: C0=4.035822672487962, alpha=0.48126953976054615, R²=0.8979

============================================================
TEST BED 5: Solar Sunspots — Astrophysical Cycle
============================================================
  Columns: ['sunspot_number']
  Sampling rate: 12.0/year
  Length: 3333 months
  First 10: [ 96.7 104.3 116.7  92.8 141.7 139.2 158.  110.5 126.5 125.8]
  N_gap=  1: CC_coupled=1286.6639, CC_base=546.3232, gain=740.3407
  N_gap=  2: CC_coupled=1286.2838, CC_base=564.3784, gain=721.9054
  N_gap=  5: CC_coupled=1296.6470, CC_base=565.2765, gain=731.3705
  N_gap= 10: CC_coupled=1255.4584, CC_base=543.1329, gain=712.3255
  N_gap= 20: CC_coupled=1266.2648, CC_base=534.5774, gain=731.6874
  N_gap= 50: CC_coupled=1353.7756, CC_base=501.3791, gain=852.3965
  N_gap=100: CC_coupled=1422.7628, CC_base=406.8786, gain=1015.8842
  Gap law fit: C_max=797.1642327354717, tau=0.40822002947601016, R²=0.0422
  Power law fit: C0=680.5613855968382, alpha=0.059495450342737344, R²=0.5991

============================================================
SYNTHESIS: Resonance Gap Law Across Empirical Datasets
============================================================
  belousov_zhabotinsky          : C_max=37.599557024782186, tau=29.31966223379055, R²_gap=0.8982, alpha=0.48126953976054615, R²_power=0.8979
  solar_sunspots                : C_max=797.1642327354717, tau=0.40822002947601016, R²_gap=0.0422, alpha=0.059495450342737344, R²_power=0.5991
```

---
*Published autonomously by World C Embassy Bridge.*
