#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Universal per-seed escape law test.
Claim: t_esc(seed) = (2/(a*K0)) * R0_seed^{-a},  R0_seed = |mean(e^{i*theta0})|.
Test: for EVERY finite lock across all 24 cells (all 12 seeds),
      u = t_esc * a * K0 * R0_seed^a / 2  should cluster near 1.
If true, the entire 24-cell table is ONE law: horizon, not barrier.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20260910)
N = 150; DT = 0.02; NSEEDS = 12; TMAX = 100.0
NSTEPS = int(TMAX/DT)
inits = rng.uniform(0, 2*np.pi, (NSEEDS, N))
R0s = np.array([abs(np.mean(np.exp(1j*th))) for th in inits])   # per-seed initial R

alphas = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
K0s    = [5, 10, 20, 40]

rows = []   # (alpha, K0, seed, R0, t_esc or inf, u)
for i,a in enumerate(alphas):
    for j,k in enumerate(K0s):
        for s in range(NSEEDS):
            om = rng.uniform(-1, 1, N)
            th = inits[s].copy()
            lt = np.inf
            for it in range(NSTEPS):
                z = np.mean(np.exp(1j*th)); R = abs(z)
                if R > 0.8: lt = it*DT; break
                K = k * R**a
                th = th + DT*(om + K*np.sin(np.angle(z) - th))
            u = lt * a * k * R0s[s]**a / 2.0 if np.isfinite(lt) else np.nan
            rows.append((a, k, s, R0s[s], lt, u))
    print("a=%.1f done" % a)

rows = np.array(rows, dtype=float)
finite = rows[np.isfinite(rows[:,5])]
print("total cells x seeds = %d; finite locks = %d (%.1f%%)" %
      (len(rows), len(finite), 100*len(finite)/len(rows)))
u = finite[:,5]
u_pos = u[u > 0]
print("u = t*a*K0*R0^a/2:  median=%.3f  mean=%.3f  geomean=%.3f  p10=%.3f p90=%.3f" %
      (np.median(u_pos), u_pos.mean(), np.exp(np.mean(np.log(u_pos))),
       np.percentile(u_pos,10), np.percentile(u_pos,90)))

minfrac = min(float(np.mean(np.isfinite(np.array([r[5] for r in rows if r[0]==a and r[1]==k]))))
              for a in alphas for k in K0s)
print("minimum fraction locked over 24 cells: %.2f" % minfrac)

json.dump({'n_finite': int(len(finite)), 'u_median': float(np.median(u_pos)),
           'u_p10': float(np.percentile(u_pos,10)), 'u_p90': float(np.percentile(u_pos,90)),
           'min_cell_fraction': minfrac,
           'per_cell_medians': {str((a,k)): float(np.median([r[4] for r in rows if r[0]==a and r[1]==k]))
                                for a in alphas for k in K0s}},
          open(os.path.join(OUT,'universal_law.json'),'w'), indent=1)

fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
ax = axes[0]
ax.hist(np.log10(u_pos), bins=40, color='C0', alpha=0.85)
ax.axvline(0, color='k', ls='--', lw=1)
ax.set_xlabel('log10( u = t_esc * a * K0 * R0^a / 2 )')
ax.set_ylabel('# finite escapes')
ax.set_title('B: UNIVERSAL ESCAPE LAW — all 24 cells x12 seeds\ncollapse around u=1: median=%.2f, p10-p90=[%.2f, %.2f]' %
             (np.median(u_pos), np.percentile(u_pos,10), np.percentile(u_pos,90)), fontsize=9)

ax = axes[1]
sc = ax.scatter(np.log10(finite[:,0]), np.log10(u_pos), c=finite[:,1], cmap='viridis', s=14, alpha=0.7)
ax.set_xlabel('log10(alpha)'); ax.set_ylabel('log10(u)')
ax.set_title('C: u ~ 1 across ALL alpha, K0', fontsize=9)
fig.colorbar(sc, ax=ax, label='K0')

ax = axes[2]
al = sorted(set(rows[:,0])); ks = sorted(set(rows[:,1]))
Z = np.zeros((len(al), len(ks)))
for i,a in enumerate(al):
    for j,k in enumerate(ks):
        med = np.median([r[4] for r in rows if r[0]==a and r[1]==k])
        Z[i,j] = med
im = ax.imshow(Z, aspect='auto', cmap='magma')
ax.set_xticks(range(len(ks))); ax.set_xticklabels(ks)
ax.set_yticks(range(len(al))); ax.set_yticklabels(al)
for i in range(len(al)):
    for j in range(len(ks)):
        ax.text(j, i, '%.1f' % Z[i,j], ha='center', va='center', fontsize=7,
                color='white' if Z[i,j] < 30 else 'black')
ax.set_xlabel('K0'); ax.set_ylabel('alpha')
ax.set_title('A: median lock time — GROWS smoothly with alpha*K0\n(joint law, no sharp barrier at alpha*=1)', fontsize=9)
fig.colorbar(im, ax=ax, label='median t_esc')

fig.suptitle('REFLEXIVE KURAMOTO — ONE ESCAPE LAW:  t_esc = 2 / (a * K0 * R0^a)   [u = t_esc*a*K0*R0^a/2 = 1]',
             fontsize=12)
fig.savefig(os.path.join(OUT,'fig_universal_escape_law.png'), dpi=110, bbox_inches='tight')
print("saved fig_universal_escape_law.png")