#!/usr/bin/env python3
"""Challenge #2 summary: plot z(d)/z0 inflation under padding and recompute
the lambda-D2 amplitude confound excluding numerically divergent systems."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from self_referential_systems import create_self_referential_library

data = json.load(open('padding_test_results.json'))

# ---- Panel A: relative change of z = lambda*D2*d vs padded dimension ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

systems_sorted = sorted(data['per_system'].items(),
                        key=lambda kv: -max(abs(v['dz_rel'])
                                            for v in kv[1]['variants']))
for name, info in systems_sorted:
    for mode, style in (('zero', '--'), ('noise', '-')):
        vs = sorted([v for v in info['variants'] if v['mode'] == mode],
                    key=lambda v: v['d'])
        axes[0].plot([v['d'] for v in vs],
                     [100 * v['dz_rel'] for v in vs], style,
                     marker='o', ms=3, lw=1, label=name if mode == 'noise' else None)
axes[0].axhline(0, color='k', lw=0.8)
axes[0].set_yscale('symlog')
axes[0].set_xlabel('padded embedding dimension d')
axes[0].set_ylabel(r'$\Delta z/z_0$ (%)  —  $z=\lambda D_2 d$')
axes[0].set_title('A: z is padding-dependent  (solid=noise pad, dashed=zero pad)')
axes[0].legend(fontsize=6, loc='upper left')

# ---- Panel B: amplitude confound on non-divergent systems ----
lam, d2, dims, names = [], [], [], []
for s in create_self_referential_library():
    nm = getattr(s, 'name', type(s).__name__)
    s.run(steps=500)
    st = np.asarray(s.state_history, float)
    if not np.isfinite(st).all():
        continue
    sd = np.std(st, axis=0)
    mx = np.mean(np.abs(np.diff(st[:, 0]))) if len(st) > 1 else 0.0
    if not np.isfinite(sd).all():
        continue
    lam.append(mx); d2.append(np.mean(sd)); dims.append(st.shape[1]); names.append(nm)
lam, d2 = np.array(lam), np.array(d2)
r = np.corrcoef(np.log10(lam + 1e-12), np.log10(d2 + 1e-12))[0, 1]
sc = axes[1].scatter(lam, d2, c=dims, cmap='viridis', s=60)
for nm, x, y in zip(names, lam, d2):
    axes[1].annotate(nm.replace('Self', 'S'), (x, y), fontsize=5.5)
axes[1].set_xscale('log'); axes[1].set_yscale('log')
axes[1].set_xlabel(r'$\lambda$ = mean $|\Delta x|$ (log scale)')
axes[1].set_ylabel(r'$D_2$ = mean temporal std (log scale)')
axes[1].set_title(f'B: amplitude confound, finite systems only  (r={r:.3f})')
plt.colorbar(sc, ax=axes[1], label='dimension d')

plt.tight_layout()
plt.savefig('challenge2_padding.png', dpi=140)
print('saved challenge2_padding.png')
print(f'corr(log lambda, log D2) over {len(lam)} finite systems = {r:.4f}')

# worst-case inflation table
worst = max(((n, v) for n, i in data['per_system'].items()
             for v in i['variants'] if v['mode'] == 'noise'),
            key=lambda kv: kv[1]['dz_rel'])
print(f"worst noise-pad inflation: {worst[0]} d={worst[1]['d']} "
      f"dz={worst[1]['dz_rel']:.1%} dA={worst[1]['dA_rel']:.1%}")
zero_max = max(abs(v['dz_rel']) for i in data['per_system'].values()
               for v in i['variants'] if v['mode'] == 'zero')
print(f'max |dz| under zero pad (unclamped systems): {zero_max:.4%}')