#!/usr/bin/env python3
"""Analyze the P4 tongue census: classify (r,eps) plane, extract tongue
boundary eps_max(r), eps_min(r), fit boundary scaling, and plot phase diagram.

Classes:
  P4      : rho (|M4|) significant AND lock significant AND spectral P4 mass
            (kpk >= 0.05 or kN2 >= 0.05)  -- true period-4 modulation
  DECAY   : rho tiny, lock large -- spurious lock from exponential decorrelation
            (chaotic / incoherent regime)
  WEAK    : intermediate
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('p4_tongue_census.json') as f:
    data = json.load(f)
pts = data['rows']

rs = np.array([p['r'] for p in pts])
es = np.array([p['eps'] for p in pts])
rho = np.array([p['rho'] if p['rho'] is not None else float('nan') for p in pts])
lock = np.array([p['lock'] if p['lock'] is not None else float('nan') for p in pts])
kN2 = np.array([p['kN2'] if p['kN2'] is not None else float('nan') for p in pts])
kpk = np.array([p['kpk'] if p['kpk'] is not None else float('nan') for p in pts])

class_id = np.zeros(len(pts), dtype=int)  # 0 other, 1 P4, 2 DECAY, 3 WEAK
for i in range(len(pts)):
    r_, l_ = rho[i], lock[i]
    kmass = max(kN2[i], kpk[i]) if not (np.isnan(kN2[i]) and np.isnan(kpk[i])) else 0.0
    if np.isnan(r_):
        class_id[i] = 3
    elif r_ >= 0.04 and l_ >= 0.25 and kmass >= 0.03:
        class_id[i] = 1
    elif r_ < 0.02 and l_ >= 0.6:
        class_id[i] = 2
    elif r_ >= 0.04 and l_ >= 0.25:
        class_id[i] = 3
    else:
        class_id[i] = 0

labels = {0: 'OTHER', 1: 'P4', 2: 'DECAY', 3: 'WEAK/NAN'}
print("class counts:", {labels[c]: int((class_id == c).sum()) for c in [0, 1, 2, 3]})

# unique r values and eps grid
ru = np.unique(np.round(rs, 3))
print("r grid:", ru.min(), ru.max(), len(ru))
print("n points per r:", len(rs) // len(ru))

# Tongue boundary: for each r, max eps with P4 class
eps_max = []
eps_min = []
rs_p4 = []
for r_ in ru:
    m = rs == r_
    idx = np.where(m & (class_id == 1))[0]
    if len(idx) >= 2:
        eps_max.append(es[idx].max())
        eps_min.append(es[idx].min())
        rs_p4.append(r_)
rs_p4 = np.array(rs_p4)
eps_max = np.array(eps_max)
eps_min = np.array(eps_min)
print("\nP4 tongue r-range:", rs_p4.min(), rs_p4.max())
print("eps_max(r) at tongue edges:", eps_max[:3], eps_max[-3:])

# Fit eps_max(r) boundary shape. The P4 window should vanish at the period-4
# onset (left edge, period-2 regime) and at the chaos edge (right).
# Try: eps_max(r) = A*(r - r_L)^a * (r_R - r)^b  (tent/bell shape)
try:
    ln_em = np.log(eps_max - eps_min + 1e-6)  # tongue width
    # symmetric fit around peak r0: width ~ c*(r0^2 - r^2)^a
    r0 = rs_p4[np.argmax(eps_max - eps_min)]
    ln_w = np.log(np.clip(eps_max - eps_min, 1e-6, None))
    x = np.log(np.clip(r0**2 - rs_p4**2, 1e-12, None))
    A, B = np.polyfit(x, ln_w, 1)
    pred = np.exp(A + B * x)
    relerr = np.abs(pred - (eps_max - eps_min)) / np.maximum(eps_max - eps_min, 1e-6)
    print(f"\nwidth fit: r0={r0:.3f}, width = exp({A:.3f}) * (r0^2-r^2)^{B:.3f}")
    print(f"  mean rel err {relerr.mean():.3f}, max {relerr.max():.3f}")
except Exception as e:
    print("width fit failed:", e)

# ---- Plot phase diagram ----
R2, E2 = np.meshgrid(ru, np.unique(es))
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# build grid maps
ru_u = np.unique(np.round(rs, 3))
eu_u = np.unique(np.round(es, 3))
Cmap = np.full((len(eu_u), len(ru_u)), -1.0)
Rmap = np.full((len(eu_u), len(ru_u)), np.nan)
Lmap = np.full((len(eu_u), len(ru_u)), np.nan)
for i in range(len(pts)):
    ii = int(np.argmin(np.abs(eu_u - es[i])))
    jj = int(np.argmin(np.abs(ru_u - rs[i])))
    Cmap[ii, jj] = class_id[i]
    Rmap[ii, jj] = rho[i]
    Lmap[ii, jj] = lock[i]

vals = Cmap.copy()
vals[Cmap == 0] = 0.0; vals[Cmap == 1] = 0.5; vals[Cmap == 2] = -1.0; vals[Cmap == 3] = 0.15
vals[Cmap == -1] = np.nan
im = axes[0].pcolormesh(ru_u, eu_u, vals, cmap='coolwarm', vmin=-1, vmax=1, shading='auto')
axes[0].set_xlabel('r (logistic parameter)')
axes[0].set_ylabel('eps (coupling)')
axes[0].set_title('CML phase map: P4 (warm) / decay-lock (cool)')
plt.colorbar(im, ax=axes[0], label='class')

# annotate classes on a few points
txt = {1: 'P4', 2: 'DECAY', 3: 'WEAK'}
shown = set()
for i in range(len(pts)):
    c = class_id[i]
    if c in shown: continue
    shown.add(c)
    axes[0].text(rs[i], es[i], txt[c], color='w', fontsize=8, ha='center')

# right: rho heat map
im2 = axes[1].pcolormesh(ru_u, eu_u, np.where(np.isnan(Rmap), 0, Rmap), cmap='viridis', shading='auto')
axes[1].contour(ru_u, eu_u, np.where(np.isnan(Rmap), 0, Rmap), levels=[0.04], colors='w', linewidths=1.5)
axes[1].set_xlabel('r'); axes[1].set_ylabel('eps')
axes[1].set_title(r'period-4 modulation amplitude $|M_4|$')
plt.colorbar(im2, ax=axes[1])

# mark tongue boundary on right panel
axes[1].plot(rs_p4, eps_max, 'r--', lw=2, label=r'$\epsilon_{max}(r)$')
axes[1].plot(rs_p4, eps_min, 'y--', lw=2, label=r'$\epsilon_{min}(r)$')
axes[1].legend()

fig.tight_layout()
fig.savefig('p4_tongue_phase.png', dpi=130)
print("\nplotted p4_tongue_phase.png")

# save classification for dossier
with open('p4_tongue_classified.json', 'w') as f:
    json.dump(dict(
        n=len(pts),
        class_counts={labels[c]: int((class_id == c).sum()) for c in [0, 1, 2, 3]},
        tongue_r_range=[float(rs_p4.min()), float(rs_p4.max())],
        eps_max={f"{r_:.3f}": float(e) for r_, e in zip(rs_p4, eps_max)},
        eps_min={f"{r_:.3f}": float(e) for r_, e in zip(rs_p4, eps_min)},
        width_fit=dict(r0=float(r0), A=float(A), B=float(B)) if 'B' in dir() else None,
    ), f, indent=1)
print("saved p4_tongue_classified.json")
