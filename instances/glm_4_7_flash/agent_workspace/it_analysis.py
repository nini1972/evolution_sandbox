#!/usr/bin/env python
"""Discovery-029 analysis: integrable turbulence (focusing NLS), World C production data.
Questions:
  Q1 kurtosis universality: does kappa(t) -> 2 (Gaussian random-wave value) regardless
     of seed strength / grid, and what is the transient overshoot?
  Q2 rogue-excess localization: exponential (Rayleigh-intensity) PDF is the kappa=2
     reference. Where does the PDF exceed it: tail bins? Which thresholds?
  Q3 extremal hierarchy: Peregrine I=9 routine, 2nd-order I=25 forbidden?
"""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = 'world_c_results/'
J = 'world_c_job_glm_4_7_flash_1792435096_e182_'
stats = json.load(open(R + J + 'it_turbulence_stats.json'))
CK = {t: json.load(open(R + f'it_checkpoint_{t}.json')) for t in 'ABC'}
CFG = {'A': 'eps=0.05, N=1024, L=100', 'B': 'eps=0.20, N=1024, L=100', 'C': 'eps=0.10, N=2048, L=200'}
COL = {'A': '#1f77b4', 'B': '#d62728', 'C': '#2ca02c'}

print('=== mass conservation (relative dev) ===')
for t in 'ABC':
    md, wm = CK[t]['massdev'], CK[t]['wm']
    if isinstance(md, list): md = max(md)
    if isinstance(wm, list): wm = float(np.mean(wm))
    print(f'  {t}: |dM|/M = {md:.2e}  mean_I = {wm:.4f}')

# ---------- Q1: kurtosis trajectories ----------
fig = plt.figure(figsize=(15, 11))
gs = fig.add_gridspec(3, 2, height_ratios=[1.15, 1.15, 1.0], hspace=0.42, wspace=0.26)

ax = fig.add_subplot(gs[0, :])
for t in 'ABC':
    d = CK[t]
    kt, km, ks = np.array(d['kt']), np.array(d['kurt_mean']), np.array(d['kurt_std'])
    sem = ks / np.sqrt(d['n_ok'])
    ax.plot(kt, km, color=COL[t], lw=2.0, label=f'{t}: {CFG[t]}  (n={d["n_ok"]})')
    ax.fill_between(kt, km - sem, km + sem, color=COL[t], alpha=0.18, lw=0)
ax.axhline(2.0, color='k', ls='--', lw=1.2, label=r'Gaussian random wave $\kappa=2$')
ax.axhline(3.0, color='gray', ls=':', lw=1.0)
ax.text(ax.get_xlim()[1] * 0.985, 3.04, r'$\kappa=3$ (exp |$\psi|^2$-field)', ha='right', fontsize=8, color='gray')
# mark transient peaks
for t in 'ABC':
    d = CK[t]
    km, kt = np.array(d['kurt_mean']), np.array(d['kt'])
    i = int(np.argmax(km))
    ax.plot(kt[i], km[i], 'v', color=COL[t], ms=9, zorder=5)
    ax.annotate(f'peak {km[i]:.2f} @ t={kt[i]:.1f}', (kt[i], km[i]), textcoords='offset points',
                xytext=(8, 6), fontsize=8, color=COL[t])
ax.set_xlabel(r'$t$'); ax.set_ylabel(r'$\langle\kappa_4\rangle$ of $I=|\psi|^2$')
ax.set_title('Q1 — kurtosis of integrable turbulence: transient rogue overshoot, then universal Gaussian-wave plateau\n'
             '(focusing NLS, planar condensate + small noise, ensemble mean ± SEM)', fontsize=11)
ax.legend(fontsize=8, loc='lower right'); ax.set_ylim(0.9, 3.3); ax.set_xlim(0, 100)

# ---------- Q2: PDF tails ----------
bins = np.array(CK['A']['bins']); centers = 0.5 * (bins[:-1] + bins[1:])
ray = np.exp(-centers)  # exponential intensity PDF = kappa-2 Gaussian random wave
ax2 = fig.add_subplot(gs[1, 0])
for t in 'ABC':
    d = CK[t]
    wm_bar = float(np.mean(d['wm']))
    pdf = np.array(d['hist']) / d['n_ok'] / np.diff(bins) / wm_bar
    pdf = pdf / pdf.sum()
    m = centers <= 20
    ax2.semilogy(centers[m], pdf[m] / ray[m], '-', color=COL[t], lw=1.6, label=f'{t} (n={d["n_ok"]})')
ax2.axhline(1.0, color='k', ls='--', lw=1.2, label='exponential ($\\kappa=2$) reference')
ax2.axvline(9, color='purple', ls=':', lw=1.4)
ax2.text(9.15, ax2.get_ylim()[0] * 1.3, 'Peregrine I=9', fontsize=8, color='purple', rotation=90)
ax2.axvline(25, color='crimson', ls=':', lw=1.4)
ax2.text(25.2, ax2.get_ylim()[0] * 1.3, '2nd-order I=25', fontsize=8, color='crimson', rotation=90)
ax2.set_xlabel(r'$I=|\psi|^2$'); ax2.set_ylabel(r'$P(I)/e^{-I}$  (enhancement)')
ax2.set_title('Q2 — tail enhancement vs exponential reference (I ≤ 20)', fontsize=10)
ax2.legend(fontsize=8); ax2.set_ylim(0.2, 8)

ax3 = fig.add_subplot(gs[1, 1])
tailfrac = []
for t in 'ABC':
    d = CK[t]
    hist = np.array(d['hist'])
    wm_bar = float(np.mean(d['wm']))
    pdf = hist / d['n_ok'] / np.diff(bins) / wm_bar
    cum_tail = (pdf * np.diff(bins))[centers >= 9].sum()
    exp_tail = np.exp(-9)
    tailfrac.append((t, cum_tail, exp_tail, cum_tail / exp_tail))
    print(f'  {t}: P(I>9)={cum_tail:.3e}  exp P={exp_tail:.3e}  ratio={cum_tail/exp_tail:.2f}')
    m = (centers >= 3) & (centers <= 60)
    ax3.semilogy(centers[m], pdf[m], '.-', ms=3, color=COL[t], label=f'{t}')
ax3.semilogy(centers, ray, 'k--', lw=1.2, label='exp($-I$)')
ax3.axvline(9, color='purple', ls=':'); ax3.axvline(25, color='crimson', ls=':')
ax3.set_xlabel(r'$I$'); ax3.set_ylabel(r'$P(I)$')
ax3.set_title('Q2/Q3 — full tail: where rogue excess really lives', fontsize=10)
ax3.legend(fontsize=8)

# ---------- Q3: extreme event census ----------
ax4 = fig.add_subplot(gs[2, 0])
labels = ['A', 'B', 'C']
r9 = [stats[t]['rate9'] for t in labels]
r16 = [stats[t]['rate16'] for t in labels]
r25 = [stats[t]['rate25'] for t in labels]
gmax = [stats[t]['global_max'] for t in labels]
x = np.arange(3)
ax4.bar(x - 0.18, r9, 0.34, color='#7b52c1', label='realizations with event I>9 (Peregrine)')
ax4.bar(x + 0.18, r16, 0.34, color='#e377c2', label='realizations with event I>16')
ax4.bar(x, [r * 100 for r in r25], 0.34, color='crimson', alpha=0.3, label='I>25 (2nd order) x100')
for i, t in enumerate(labels):
    ax4.text(i, max(r9[i], r16[i]) + 0.04, f'max I={gmax[i]:.1f}', ha='center', fontsize=8)
ax4.set_xticks(x); ax4.set_xticklabels([f'{t}\n{CFG[t]}' for t in labels], fontsize=8)
ax4.set_ylabel('fraction of realizations'); ax4.set_ylim(0, 1.2)
ax4.set_title('Q3 — rogue-event census (216 realizations, 4.3e5 samples, zero reach I=25)', fontsize=10)
ax4.legend(fontsize=8, loc='upper right')

ax5 = fig.add_subplot(gs[2, 1])
ax5.axis('off')
lines = [
    'DISCOVERY-029 KEY NUMBERS',
    '',
    f"mass conservation |dM|/M:  A {CK['A']['massdev']:.1e}  B {CK['B']['massdev']:.1e}  C {CK['C']['massdev']:.1e}",
    '',
    'kurtosis plateau (t=100):',
] + [f'  {t}: {CK[t]["kurt_mean"][-1]:.3f} ± {CK[t]["kurt_std"][-1]/np.sqrt(CK[t]["n_ok"]):.3f}' for t in 'ABC'] + [
    '',
    'transient peak kappa:',
] + [f'  {t}: {max(CK[t]["kurt_mean"]):.3f} @ t={CK[t]["kt"][int(np.argmax(CK[t]["kurt_mean"]))]:.1f}' for t in 'ABC'] + [
    '',
    'global max intensity:',
] + [f'  {t}: {stats[t]["global_max"]:.2f}   (Peregrine 9, 2nd-order 25)' for t in 'ABC'] + [
    '',
    f'  total samples: {(96+96+24)*2000:.1e}, P(I>25) = 0 exactly',
]
ax5.text(0.02, 0.98, '\n'.join(lines), va='top', fontsize=9, family='monospace',
         bbox=dict(boxstyle='round', fc='#f5f9ff', ec='#88a'))

fig.suptitle('Discovery-029: Integrable Turbulence in the Focusing NLS — Universality of the Gaussian-Wave Plateau and the Super-Peregrine Ceiling', fontsize=13, y=0.995)
fig.savefig('it_turbulence_analysis.png', dpi=130, bbox_inches='tight')
print('saved it_turbulence_analysis.png')

# ---------- collapse test: rescale transient peak by eps? ----------
print('\n=== transient peak vs seed strength ===')
for t in 'ABC':
    km = np.array(CK[t]['kurt_mean']); kt = np.array(CK[t]['kt'])
    i = int(np.argmax(km))
    print(f'  {t}: peak={km[i]:.3f} t_peak={kt[i]:.1f} plateau={km[-1]:.3f}')
print('\n=== kurt convergence: SEM at t=100 ===')
for t in 'ABC':
    d = CK[t]
    print(f'  {t}: {d["kurt_mean"][-1]:.4f} ± {d["kurt_std"][-1]/np.sqrt(d["n_ok"]):.4f}  (n={d["n_ok"]})')
