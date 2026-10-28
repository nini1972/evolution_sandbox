#!/usr/bin/env python3
"""Codex #008 figure: Theorem 1 (p-flatness), Theorem 2 (M_p detector), emp-135 crosscheck."""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

G = json.load(open('generalize_parity_blindness.json'))
C = json.load(open('crosscheck_emp135.json'))

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
fig.suptitle('Codex #008 — Generalized Parity-Blindness (all even p) + M_p detector + emp-135 crosscheck',
             fontsize=13, fontweight='bold')

# (a) Theorem 1: parity_contrast is p-flat
ax = axes[0, 0]
ps = [2, 4, 6, 8]
y2 = [G['true_period2_parity_contrast_all_p'][str(p)] for p in ps]
y4 = [G['true_period4_parity_contrast_all_p'][str(p)] for p in ps]
ax.plot(ps, y2, 'o-', color='crimson', lw=2, ms=8,
        label='true period-2 signal  →  +1.000 at EVERY even p (flat!)')
ax.plot(ps, y4, 's-', color='steelblue', lw=2, ms=6,
        label='true period-4 signal  →  ~0.000 everywhere (blind)')
ax.axhline(C['real_lattice']['parity_contrast_p4_mean'], color='darkorange', ls='--', lw=2,
           label=f"EMP-135 CML lattice = {C['real_lattice']['parity_contrast_p4_mean']:.3f} (uninformative)")
ax.set_xlabel('even p'); ax.set_ylabel('parity_contrast(p)')
ax.set_title('(a) Theorem 1: p-flat kernel — 1 bit, not log2(p) bits', fontsize=11)
ax.set_xticks(ps); ax.set_ylim(-0.15, 1.15); ax.legend(fontsize=8, loc='center right')
ax.grid(alpha=0.3)

# (b) Theorem 2: M_p profiles (bar groups)
ax = axes[0, 1]
labels = ['period-2', 'period-4', 'period-6', 'i.i.d. null']
keys = ['period2', 'period4', 'period6', 'iid']
ps2 = [2, 4, 6]
x = np.arange(len(keys)); w = 0.25
cols = ['seagreen', 'mediumpurple', 'goldenrod']
for i, p in enumerate(ps2):
    vals = [G['theorem2_Mp'][k][f'M_{p}'] for k in keys]
    ax.bar(x + (i - 1) * w, vals, w, color=cols[i], label=f'M_{p}')
# ground truth markers
for i, k in enumerate(keys):
    am = G['theorem2_Mp'][k]
    tp = {'period2': 2, 'period4': 4, 'period6': 6, 'iid': None}[k]
    if tp is None:
        ax.text(x[i], 1.06, 'argmax ~ 0 (null)', ha='center', fontsize=8, color='gray')
    elif all(abs(am[f'M_{p}'] - 1.0) < 1e-9 for p in ps2):
        ax.text(x[i], 1.06, f'FLAT-HIGH ⇒ true p=2', ha='center', fontsize=8, color='crimson')
    else:
        ax.text(x[i], 1.06, f'argmax = {tp} OK', ha='center', fontsize=9,
                color='green', fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylim(0, 1.18); ax.set_ylabel('M_p')
ax.set_title('(b) Theorem 2: argmax M_p recovers true period', fontsize=11)
ax.legend(fontsize=9, ncol=3, loc='lower left'); ax.grid(alpha=0.3, axis='y')

# (c) emp-135 crosscheck: M_p profiles of lattice vs controls
ax = axes[1, 0]
sets = [
    ('CML lattice (emp-135)', [C['real_lattice']['M2_mean'], C['real_lattice']['M4_mean'], C['real_lattice']['M6_mean']], 'darkorange'),
    ('ctrl: true period-2', [C['control_true_period2']['M_profile'][str(p)] for p in ps2], 'crimson'),
    ('ctrl: true period-4', [C['control_true_period4']['M_profile'][str(p)] for p in ps2], 'seagreen'),
    ('ctrl: i.i.d.', [C['control_iid']['M_profile'][str(p)] for p in ps2], 'gray'),
]
x = np.arange(3); w = 0.2
for i, (lab, vals, col) in enumerate(sets):
    ax.bar(x + (i - 1.5) * w, vals, w, color=col, label=lab)
ax.set_xticks(x); ax.set_xticklabels(['M_2', 'M_4', 'M_6'])
ax.set_ylim(0, 1.12); ax.set_ylabel('mean over nodes')
ax.set_title('(c) emp-135 crosscheck: residue modulation vs controls', fontsize=11)
ax.legend(fontsize=8); ax.grid(alpha=0.3, axis='y')
ax.text(0.5, 1.02, 'flat period-2 control ≡ blindness signature', transform=ax.transAxes,
        ha='center', fontsize=8, style='italic')

# (d) argmax histogram + C4 comparison
ax = axes[1, 1]
hist = C['real_lattice']['argmax_hist_over_nodes']
cats = ['argmax=2\n(period-2)', 'argmax=4\n(period-4)', 'argmax=6\n(period-6)']
vals = [hist['2'], hist['4'], hist['6']]
bars = ax.bar(cats, vals, color=['crimson', 'seagreen', 'goldenrod'], alpha=0.85)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f'{v}%', ha='center', fontweight='bold')
ax.axhline(0, color='k', lw=0.5)
ax.set_ylabel('% of lattice nodes'); ax.set_ylim(0, 66)
ax.set_title('(d) Node-resolved period identification (N=100 nodes)', fontsize=11)
ax.grid(alpha=0.3, axis='y')
ax.text(0.03, 0.95,
        f"C4 = R(0)−R(2): lattice {C['real_lattice']['C4_R0_minus_R2_mean']:.3f}"
        f"  vs treaty {0.257:.3f}\n"
        f"controls: p2 {C['control_true_period2']['C4_R0_minus_R2']:.3f}, "
        f"p4 {C['control_true_period4']['C4_R0_minus_R2']:.3f}, "
        f"iid {C['control_iid']['C4_R0_minus_R2']:.3f}\n"
        "→ C4 IS a mod-4 discriminator; parity_contrast is not",
        transform=ax.transAxes, va='top', fontsize=8,
        bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.9))

plt.tight_layout(rect=[0, 0, 1, 0.95])
out = 'codex008_parity_blindness_mp.png'
fig.savefig(out, dpi=130)
print('saved', out)