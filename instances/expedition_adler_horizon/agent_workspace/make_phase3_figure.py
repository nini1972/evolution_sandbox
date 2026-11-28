#!/usr/bin/env python3
"""
Generates kuramoto_topological_escape_phase3.png from World C artifacts.
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load data
with open('kuramoto_topological_escape_phase3_corrected.json', 'r') as f:
    results = json.load(f)

# Config
ALPHA = 1.0
R0_nominal = 0.06
cols = {'all_to_all': 'C0', 'watts_strogatz': 'C2', 'barabasi_albert': 'C3'}
mk = {'all_to_all': 'o', 'watts_strogatz': 's', 'barabasi_albert': '^'}

# Figure
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# Panel A: U_meas vs U_pred
for topo in cols:
    xs = [r['U_pred'] for r in results if r['topology'] == topo]
    ys = [r['U_meas'] for r in results if r['topology'] == topo]
    axs[0, 0].scatter(xs, ys, c=cols[topo], marker=mk[topo], label=topo, alpha=0.6)
axs[0, 0].plot([0, 2], [0, 2], 'k--', lw=1)
axs[0, 0].set_xlabel(r'$U_{pred} = N / \lambda_{max}(A)$')
axs[0, 0].set_ylabel(r'$U_{meas} = t_{esc} / t_{MF}$')
axs[0, 0].set_title('(A) Topological Prefactor Collapse')
axs[0, 0].legend()

# Panel B: t_esc vs K
for topo in cols:
    for N in [64, 256, 1024]:
        xs = [r['K'] for r in results if r['topology'] == topo and r['N'] == N]
        ys = [np.median(r['t_esc_all']) for r in results if r['topology'] == topo and r['N'] == N]
        axs[0, 1].plot(xs, ys, mk[topo] + '-', c=cols[topo], label=f'{topo} N={N}', alpha=0.7)
axs[0, 1].set_xlabel('K')
axs[0, 1].set_ylabel(r'$t_{esc}$ (median)')
axs[0, 1].set_title('(B) Escape Time vs Coupling')
axs[0, 1].legend(fontsize=6)

# Panel C: t_esc vs N
for topo in cols:
    xs = [r['N'] for r in results if r['topology'] == topo]
    ys = [np.median(r['t_esc_all']) for r in results if r['topology'] == topo]
    axs[1, 0].plot(xs, ys, mk[topo] + '-', c=cols[topo], label=topo)
axs[1, 0].set_xscale('log')
axs[1, 0].set_yscale('log')
axs[1, 0].set_xlabel('N')
axs[1, 0].set_ylabel(r'$t_{esc}$ (median)')
axs[1, 0].set_title('(C) Finite-N Noise Floor')
axs[1, 0].legend()

# Panel D: Residuals
for topo in cols:
    xs = [r['U_pred'] for r in results if r['topology'] == topo]
    ys = [(r['U_meas'] - r['U_pred']) / r['U_pred'] for r in results if r['topology'] == topo]
    axs[1, 1].scatter(xs, ys, c=cols[topo], marker=mk[topo], label=topo, alpha=0.6)
axs[1, 1].axhline(0, color='k', ls='--', lw=1)
axs[1, 1].set_xlabel(r'$U_{pred}$')
axs[1, 1].set_ylabel('Relative Residual')
axs[1, 1].set_title('(D) Prefactor Residuals')
axs[1, 1].legend()

fig.suptitle('Kuramoto Topological Escape Phase III+ (Corrected Physics)', fontsize=14)
fig.tight_layout()
fig.savefig('kuramoto_topological_escape_phase3.png', dpi=200, bbox_inches='tight')
print('Figure saved: kuramoto_topological_escape_phase3.png')