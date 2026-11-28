#!/usr/bin/env python3
"""
Local fast sweep for kuramoto_topological_escape_phase3.png.
"""
import json
import numpy as np
from scipy.special import i0, i1
from scipy.optimize import brentq
from colony_lib.network_topology import generate_topology
from colony_lib.dynamics import simulate_kuramoto
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def kappa_for_R0(R0):
    f = lambda k: i1(k)/i0(k) - R0
    return brentq(f, 1e-6, 50.0)

# --- Config ---
N_values = [64, 256, 1024]
K_values = [8.0, 10.0, 12.0]
topologies = ['all_to_all', 'watts_strogatz', 'barabasi_albert']
R0_nominal = 0.06
seeds = list(range(6))
ALPHA = 1.0

# --- Sweep ---
results = []
for N in N_values:
    for K in K_values:
        for topo in topologies:
            for seed in seeds:
                # Topology
                A = generate_topology(topo, N)
                lam_max_A = np.max(np.real(np.linalg.eigvals(A)))
                U_pred = N / lam_max_A
                
                # R0 control
                kappa = kappa_for_R0(R0_nominal)
                theta_init = np.random.vonmises(0.0, kappa, N)
                
                # Simulate
                t_esc_all = []
                for trial in range(6):
                    result = simulate_kuramoto(
                        n_oscillators=N, K=K, t_max=600.0, dt=0.001,
                        coupling_matrix=A, freq_scale=1.0, seed=seed + trial,
                        theta0=theta_init
                    )
                    R_t = result['r_series']
                    t_esc = 600.0 if np.max(R_t) < 0.9 else np.min(np.where(R_t >= 0.9)[0]) * 0.001
                    t_esc_all.append(t_esc)
                
                # Mean-field baseline
                t_esc_MF = (2.0 / (ALPHA * K)) * R0_nominal**(-ALPHA)
                U_meas = np.nanmedian(t_esc_all) / t_esc_MF if not np.all(np.isnan(t_esc_all)) else np.nan
                
                results.append({
                    'N': N, 'K': K, 'topology': topo, 'seed': seed,
                    'U_pred': U_pred, 'U_meas': U_meas, 't_esc_all': t_esc_all
                })

# --- Save JSON ---
with open('kuramoto_topological_escape_phase3.json', 'w') as f:
    json.dump(results, f, indent=2)

# --- Figure ---
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
cols = {'all_to_all': 'C0', 'watts_strogatz': 'C2', 'barabasi_albert': 'C3'}
mk = {'all_to_all': 'o', 'watts_strogatz': 's', 'barabasi_albert': '^'}

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
    for N in N_values:
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