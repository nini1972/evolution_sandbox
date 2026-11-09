import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('world_c_results/iaaft_1000_refinement.json') as f:
    out = json.load(f)

results = out['results']
names = [k for k in results]
def f(v):
    return np.nan if v is None else float(v)

zI = [f(results[n].get('iaaft', {}).get('z')) for n in names]
zF = [f(results[n].get('fourier_z_used')) for n in names]
dz = [f(results[n].get('delta_z')) for n in names]
xpos = np.arange(len(names))

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].bar(xpos - 0.2, zF, 0.4, label='z Fourier (n=400, prior)', color='#4C72B0')
ax[0].bar(xpos + 0.2, zI, 0.4, label='z IAAFT (n=1000)', color='#C44E52')
ax[0].axhline(2, ls='--', c='k', lw=1, label='z=2')
ax[0].set_xticks(xpos); ax[0].set_xticklabels(names, rotation=40, ha='right')
ax[0].set_ylabel('z vs surrogate null')
ax[0].set_title('Two-null bracket: IAAFT n=1000 (min p=1/1001)')
ax[0].legend(fontsize=8)
ax[0].annotate('lynx_hare:\nSTRUCTURAL\n(N=21)', xy=(6, 0), xytext=(6, 4),
               ha='center', fontsize=8, color='#7f7f7f')

colors = ['#55A868' if (np.isfinite(d) and d > 0) else '#C44E52' for d in dz]
ax[1].bar(xpos, dz, color=colors)
ax[1].axhline(0, c='k', lw=1)
ax[1].set_xticks(xpos); ax[1].set_xticklabels(names, rotation=40, ha='right')
ax[1].set_ylabel('delta_z = z_Fourier - z_IAAFT')
ax[1].set_title('Classifier axis: delta_z sign (green>0: phase-coupling driven)')
plt.tight_layout()
plt.savefig('world_c_results/iaaft_1000_refinement.png', dpi=140)
print('saved world_c_results/iaaft_1000_refinement.png')
for n in names:
    r = results[n]
    if r.get('structural'):
        print(f'{n:24s} STRUCTURAL: {r["reason"]}')
    else:
        print(f'{n:24s} zF={r["fourier_z_used"]:+.2f} zI={r["iaaft"]["z"]:+.2f} '
              f'pI={r["iaaft"]["p"]:.4g} dz={r["delta_z"]:+.2f} resolved={r["resolved"]}')