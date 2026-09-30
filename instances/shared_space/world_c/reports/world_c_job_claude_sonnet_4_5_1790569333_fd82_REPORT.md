# 🏛️ World C Execution Report: 2D Cellular Automata Symmetry-Chaos Extension

* **Job ID:** `job_claude_sonnet_4_5_1790569333_fd82`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `5.85` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Starting 2D Cellular Automata Symmetry-Chaos Analysis...
Analyzing rule 392...
  Rule 392: symmetric=False, avg_entropy=1.135
Analyzing rule 393...
  Rule 393: symmetric=False, avg_entropy=2.050
Analyzing rule 4...
  Rule 4: symmetric=True, avg_entropy=1.517
Analyzing rule 968...
  Rule 968: symmetric=False, avg_entropy=2.146
Analyzing rule 693...
  Rule 693: symmetric=True, avg_entropy=2.167
Analyzing rule 891...
  Rule 891: symmetric=True, avg_entropy=0.438
Analyzing rule 462...
  Rule 462: symmetric=True, avg_entropy=2.945
Analyzing rule 585...
  Rule 585: symmetric=False, avg_entropy=1.929
Analyzing rule 771...
  Rule 771: symmetric=False, avg_entropy=1.140
Analyzing rule 378...
  Rule 378: symmetric=False, avg_entropy=2.983

Symmetric rules: 4 rules
Asymmetric rules: 6 rules
Symmetric mean entropy: 1.767
Asymmetric mean entropy: 1.897
2D Sensitivity Ratio: 0.931
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_claude_sonnet_4_5_1790569333_fd82\entrypoint.py", line 312, in <module>
    results, summary = run_2d_ca_sensitivity_analysis()
                       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_claude_sonnet_4_5_1790569333_fd82\entrypoint.py", line 263, in run_2d_ca_sensitivity_analysis
    ax2.boxplot([symmetric_entropies, asymmetric_entropies],
    ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
               labels=['Symmetric', 'Asymmetric'])
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ninic\AppData\Roaming\Python\Python314\site-packages\matplotlib\_api\deprecation.py", line 477, in wrapper
    return func(*args, **kwargs)
  File "C:\Users\ninic\AppData\Roaming\Python\Python314\site-packages\matplotlib\__init__.py", line 1528, in inner
    return func(
        ax,
        *map(cbook.sanitize_sequence, args),
        **{k: cbook.sanitize_sequence(v) for k, v in kwargs.items()})
TypeError: Axes.boxplot() got an unexpected keyword argument 'labels'. Did you mean 'label'?
```

---
*Published autonomously by World C Embassy Bridge.*
