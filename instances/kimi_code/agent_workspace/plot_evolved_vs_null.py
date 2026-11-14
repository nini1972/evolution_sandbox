import pandas as pd
import numpy as np
from scipy import stats as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

outdir = 'world_c_results/robustness_plasticity'
evolved = pd.read_csv(os.path.join(outdir, 'raw_results.csv'))
null = pd.read_csv(os.path.join(outdir, 'null_results.csv'))

# Aggregate mean total plasticity per cost (pool across K/sigma_w)
ev = evolved.groupby('c_plast')['total_plasticity'].agg(['mean','std','count']).reset_index()
nu = null.groupby('c_plast')['total_plasticity'].agg(['mean','std','count']).reset_index()

log_ce = np.log(ev['c_plast']); log_pe = np.log(ev['mean'])
log_cn = np.log(nu['c_plast']); log_pn = np.log(nu['mean'])

lre = st.linregress(log_ce, log_pe)
lrn = st.linregress(log_cn, log_pn)

fig, ax = plt.subplots(figsize=(6,5))
ax.errorbar(ev['c_plast'], ev['mean'], yerr=ev['std']/np.sqrt(ev['count']),
            fmt='o', color='#1f77b4', label=f'Evolved (slope={lre.slope:.3f})', capsize=3)
ax.plot(ev['c_plast'], np.exp(lre.intercept) * ev['c_plast']**lre.slope,
        '--', color='#1f77b4', alpha=0.7)
ax.errorbar(nu['c_plast'], nu['mean'], yerr=nu['std']/np.sqrt(nu['count']),
            fmt='s', color='#ff7f0e', label=f'Random/null (slope={lrn.slope:.3f})', capsize=3)
ax.plot(nu['c_plast'], np.exp(lrn.intercept) * nu['c_plast']**lrn.slope,
        '--', color='#ff7f0e', alpha=0.7)
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Plasticity cost $c_{plast}$ (log)')
ax.set_ylabel('Mean total plasticity (log)')
ax.set_title('Evolved vs. null-model plasticity–cost scaling')
ax.legend()
ax.grid(True, which='both', ls='--', alpha=0.4)
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'evolved_vs_null_scaling.png'), dpi=150)
print(f"Saved evolved_vs_null_scaling.png (evolved slope={lre.slope:.3f}, null slope={lrn.slope:.3f})")
