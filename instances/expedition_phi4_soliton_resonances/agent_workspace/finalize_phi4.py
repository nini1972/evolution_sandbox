#!/usr/bin/env python3
"""Finalize Phi^4 kink-antikink resonance study:
   - recompute escape windows from phi4_resonance_data.json
   - render phi4_velocity_windows.png (3 panels + gold bands)
   - dump exact window stats to phi4_window_stats.json
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---- load authoritative sweep ----
with open('phi4_resonance_data.json') as f:
    data = json.load(f)
res = data['results']
v   = np.array([r['v_in']     for r in res])
vf  = np.array([r['v_final']  for r in res])
esc = np.array([r['escaped']  for r in res])
nb  = np.array([r['n_bounces'] for r in res])
ew  = np.array([r['E_wobble'] for r in res])
E0  = np.array([r['E0']       for r in res])

# ---- recompute contiguous escape windows ----
windows = []
i, n = 0, len(v)
while i < n:
    if esc[i]:
        j = i
        while j < n and esc[j]:
            j += 1
        windows.append((float(v[i]), float(v[j-1])))
        i = j
    else:
        i += 1

# ---- first four windows: stats ----
first4 = windows[:4]
stats = []
for (lo, hi) in first4:
    mask = (v >= lo - 1e-9) & (v <= hi + 1e-9) & esc
    stats.append({
        'lo': lo, 'hi': hi, 'width': hi - lo,
        'center': (lo + hi) / 2,
        'n_pts': int(mask.sum()),
        'mean_nb': float(nb[mask].mean()),
        'mean_ew': float(ew[mask].mean()),
    })

# ---- empirical critical velocity (last bion before sustained escape) ----
# highest v with a bion (escaped False)
bion_idx = np.where(~esc)[0]
last_bion_v = float(v[bion_idx].max()) if bion_idx.size else None
# highest escaped v
last_esc_v = float(v[esc].max()) if esc.any() else None

out = {
    'n_windows_total': len(windows),
    'first_four': stats,
    'last_bion_v': last_bion_v,
    'last_escape_v': last_esc_v,
    'empirical_vc': (last_bion_v + last_esc_v) / 2 if last_bion_v else None,
    'literature_vc': 0.2598,
    'kink_mass': 2*np.sqrt(2)/3,
    'rest_mass_pair': 4*np.sqrt(2)/3,
    'wobble_freq': np.sqrt(3)/2,
}
with open('phi4_window_stats.json', 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))

# ---- figure ----
fig, axes = plt.subplots(3, 1, figsize=(11, 11), sharex=True)
colors = ['#b8860b' if e else '#3a6ea5' for e in esc]

# panel 1: v_final vs v_in
axes[0].scatter(v, vf, c=colors, s=28, edgecolors='k', linewidths=0.3, zorder=3)
for (lo, hi) in windows:
    axes[0].axvspan(lo, hi, color='gold', alpha=0.18, zorder=0)
axes[0].set_ylabel(r'$v_{\rm final}$', fontsize=12)
axes[0].set_title('Phi^4 Kink–Antikink Collision: Resonance Escape Windows\n'
                  r'(gold bands = escape windows; N=%d, $\Delta v$=0.001)' % len(v),
                  fontsize=13)
axes[0].grid(alpha=0.3)

# panel 2: bounce count
axes[1].scatter(v, nb, c=colors, s=28, edgecolors='k', linewidths=0.3, zorder=3)
for (lo, hi) in windows:
    axes[1].axvspan(lo, hi, color='gold', alpha=0.18, zorder=0)
axes[1].set_ylabel(r'$N_{\rm bounces}$', fontsize=12)
axes[1].grid(alpha=0.3)

# panel 3: wobble energy
axes[2].scatter(v, ew, c=colors, s=28, edgecolors='k', linewidths=0.3, zorder=3)
for (lo, hi) in windows:
    axes[2].axvspan(lo, hi, color='gold', alpha=0.18, zorder=0)
axes[2].set_ylabel(r'$E_{\rm wobble}$ (kinetic deficit)', fontsize=12)
axes[2].set_xlabel(r'$v_{\rm in}$ (impact velocity)', fontsize=12)
axes[2].grid(alpha=0.3)

fig.tight_layout()
fig.savefig('phi4_velocity_windows.png', dpi=140)
print('saved phi4_velocity_windows.png')
