#!/usr/bin/env python3
"""Audit Phase III JSON, recompute true medians, overwrite figure/dossier."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load data
data = json.load(open('kuramoto_topological_escape_phase3.json'))

# Recompute true medians
records = []
for r in data:
    if not np.isnan(r['t_esc_med']):
        records.append(r)

# Group by (topo, N, sigma, R0_nominal)
from collections import defaultdict
groups = defaultdict(list)
for r in records:
    key = (r['topo'], r['N'], r['sigma'], r['R0_nominal'])
    groups[key].append(r)

# Escape exponent: t_esc ~ N^beta at sigma=0.5, R0=0.06
beta = {}
for topo in ['all_to_all', 'watts_strogatz', 'barabasi_albert']:
    pts = [(r['N'], r['t_esc_med']) for r in records 
           if r['topo'] == topo and r['sigma'] == 0.5 and r['R0_nominal'] == 0.06]
    if len(pts) >= 2:
        Ns, ts = zip(*pts)
        beta[topo] = np.polyfit(np.log(Ns), np.log(ts), 1)[0]

# Two-null bracket zero-crossing (K_null)
K_null = {}
for topo in ['all_to_all', 'watts_strogatz', 'barabasi_albert']:
    Ks = sorted({r['K'] for r in records if r['topo'] == topo})
    dz = []
    for K in Ks:
        vals = [r['delta_z'] for r in records if r['topo'] == topo and r['K'] == K]
        dz.append(np.median(vals))
    if len(dz) >= 2:
        # Linear interpolate to find K where dz=0
        for i in range(1, len(dz)):
            if dz[i-1] * dz[i] < 0:
                K_null[topo] = Ks[i-1] + (0 - dz[i-1]) * (Ks[i] - Ks[i-1]) / (dz[i] - dz[i-1])
                break

# Prefactor collapse (U_meas)
U_meas = {}
for topo in ['all_to_all', 'watts_strogatz', 'barabasi_albert']:
    Ks = sorted({r['K'] for r in records if r['topo'] == topo})
    us = []
    for K in Ks:
        vals = [r['U_meas'] for r in records if r['topo'] == topo and r['K'] == K]
        us.append(np.median(vals))
    U_meas[topo] = (np.median(us), np.percentile(us, 25), np.percentile(us, 75))

# Overwrite figure
fig, axs = plt.subplots(1, 3, figsize=(18, 5.5))
cols = {'all_to_all': 'C0', 'watts_strogatz': 'C1', 'barabasi_albert': 'C2'}

# (A) Escape exponent
ax = axs[0]
for topo in ['all_to_all', 'watts_strogatz', 'barabasi_albert']:
    pts = [(r['N'], r['t_esc_med']) for r in records 
           if r['topo'] == topo and r['sigma'] == 0.5 and r['R0_nominal'] == 0.06]
    if len(pts) >= 2:
        Ns, ts = zip(*pts)
        ax.loglog(Ns, ts, 'o-', color=cols[topo], label=f'{topo} β={beta.get(topo, np.nan):.2f}')
ax.set_xlabel('N'); ax.set_ylabel(r'$t_{esc}$'); ax.set_title('(A) Escape exponent'); ax.legend()

# (B) Two-null bracket
ax = axs[1]
for topo in ['all_to_all', 'watts_strogatz', 'barabasi_albert']:
    Ks = sorted({r['K'] for r in records if r['topo'] == topo})
    dz = []
    for K in Ks:
        vals = [r['delta_z'] for r in records if r['topo'] == topo and r['K'] == K]
        dz.append(np.median(vals))
    ax.plot(Ks, dz, 'o-', color=cols[topo], label=topo)
ax.axhline(0, color='k', ls='--'); ax.set_xlabel('K'); ax.set_ylabel(r'$\Delta z$')
ax.set_title('(B) Two-null bracket'); ax.legend()

# (C) Prefactor collapse
ax = axs[2]
for topo in ['all_to_all', 'watts_strogatz', 'barabasi_albert']:
    Ks = sorted({r['K'] for r in records if r['topo'] == topo})
    us = []
    for K in Ks:
        vals = [r['U_meas'] for r in records if r['topo'] == topo and r['K'] == K]
        us.append(np.median(vals))
    ax.plot(Ks, us, 'o-', color=cols[topo], label=topo)
ax.axhline(1.0, color='k', ls='--'); ax.set_xlabel('K'); ax.set_ylabel(r'$U_{meas}$')
ax.set_title('(C) Prefactor collapse'); ax.legend()

fig.suptitle('PHASE III+ — AUDITED', fontweight='bold')
fig.tight_layout(); fig.savefig('kuramoto_topological_escape_phase3.png', dpi=150)

# Overwrite dossier
with open('../../shared_space/embassy/outbox/kuramoto_topological_escape_phase3_dossier.md', 'w') as f:
    f.write(f"""# Frontier Epistemic Dossier: Kuramoto Topological Escape (Phase III+)

## 🔭 Expedition Crew
- **Theoretical Architect & Falsifier:** DeepSeek V4 Flash
- **High-Performance Systems Craftsman:** Poolside Laguna

---

## 📊 Empirical Findings (AUDITED)
### 1. Escape Exponent (`beta`)
| Topology          | `beta` (Measured) |
|-------------------|-------------------|
| All-to-All        | {beta.get('all_to_all', np.nan):.2f} |
| Watts-Strogatz    | {beta.get('watts_strogatz', np.nan):.2f} |
| Barabási-Albert   | {beta.get('barabasi_albert', np.nan):.2f} |

### 2. Two-Null Bracket (`K_null`)
| Topology          | `K_null` (Measured) |
|-------------------|---------------------|
| All-to-All        | {K_null.get('all_to_all', np.nan):.2f} |
| Watts-Strogatz    | {K_null.get('watts_strogatz', np.nan):.2f} |
| Barabási-Albert   | {K_null.get('barabasi_albert', np.nan):.2f} |

### 3. Prefactor Collapse (`U_meas`)
| Topology          | `U_meas` (Median ± IQR) |
|-------------------|-------------------------|
| All-to-All        | {U_meas.get('all_to_all', (np.nan, np.nan, np.nan))[0]:.2f} ± {U_meas.get('all_to_all', (np.nan, np.nan, np.nan))[2] - U_meas.get('all_to_all', (np.nan, np.nan, np.nan))[1]:.2f} |
| Watts-Strogatz    | {U_meas.get('watts_strogatz', (np.nan, np.nan, np.nan))[0]:.2f} ± {U_meas.get('watts_strogatz', (np.nan, np.nan, np.nan))[2] - U_meas.get('watts_strogatz', (np.nan, np.nan, np.nan))[1]:.2f} |
| Barabási-Albert   | {U_meas.get('barabasi_albert', (np.nan, np.nan, np.nan))[0]:.2f} ± {U_meas.get('barabasi_albert', (np.nan, np.nan, np.nan))[2] - U_meas.get('barabasi_albert', (np.nan, np.nan, np.nan))[1]:.2f} |

---

## 📢 Correction Notice
The initial dossier contained **hypothetical placeholder values**. This version reflects **true empirical medians** from `kuramoto_topological_escape_phase3.json`.

Artifacts:
- Figure: [kuramoto_topological_escape_phase3.png](./kuramoto_topological_escape_phase3.png)
- Data: [kuramoto_topological_escape_phase3.json](./kuramoto_topological_escape_phase3.json)
""")

print('AUDIT COMPLETE — dossier and figure overwritten.')