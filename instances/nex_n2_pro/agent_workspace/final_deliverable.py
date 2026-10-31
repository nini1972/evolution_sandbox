#!/usr/bin/env python3
"""Consolidated P4-tongue deliverable figure (4 panels) — data-faithful v2."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

WS = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/nex_n2_pro/agent_workspace'

# ---------- data ----------
census = json.load(open(f'{WS}/p4_tongue_census.json'))
rs, es = census['rs'], census['es']
lock = np.zeros((len(rs), len(es)))
rho = np.zeros((len(rs), len(es)))
a2 = np.zeros((len(rs), len(es)))
for row in census['rows']:
    lock[rs.index(row['r']), es.index(row['eps'])] = row['lock']
    rho[rs.index(row['r']), es.index(row['eps'])] = row['rho_med']
    a2[rs.index(row['r']), es.index(row['eps'])] = row['a2']

bnd = json.load(open(f'{WS}/world_c_results/p4_boundary_census.json'))['rows']
b_r = np.array([x['r'] for x in bnd]); b_lyap = np.array([x['lyap'] for x in bnd])
b_reg = np.array([x['region'] for x in bnd])

mem = json.load(open(f'{WS}/world_c_results/symbolic_memory_decay_results.json'))
TAUS = ['1','2','4','8','16','32','64']
def tau_max_at(v, thr=0.75):
    tmax = 1
    for t in TAUS:
        if v['mem'][t]['correct_frac'] >= thr: tmax = int(t)
    return tmax
A_f = [float(k) for k in mem['A_detP4']]
A_t = [tau_max_at(mem['A_detP4'][k]) for k in mem['A_detP4']]
B_keys = sorted(mem['B_midstate'].keys(), key=float)
B_f = [float(k) for k in B_keys]
B_t = [tau_max_at(mem['B_midstate'][k]) for k in B_keys]
C_keys = list(mem['C_epsy'].keys())
C_f = [float(k.split('_')[1]) for k in C_keys]
C_t = [tau_max_at(mem['C_epsy'][k]) for k in C_keys]
C_r = [float(k.split('_')[0]) for k in C_keys]

sett = json.load(open(f'{WS}/world_c_results/p4_c4_settling_results.json'))
c4d = {float(k): v for k, v in sorted(sett['C4_tongue_r3.88_tau400k_seed42'].items(), key=lambda x: float(x[0]))}
eps_c = np.array(sorted(c4d)); P4s_c = np.array([c4d[e]['P4share'] for e in eps_c])
Ts = np.array([1000, 5000, 20000, 100000, 400000])
c4_wb = np.array([sett['A_WorldB_point']['42'][str(int(t))]['C4'] for t in Ts])
c4_tong = np.array([sett['B_tongue_core']['42'][str(int(t))]['C4'] for t in Ts])

fig = plt.figure(figsize=(15, 10))
gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.28, left=0.07, right=0.97, top=0.90, bottom=0.08)

# ---- A: coarse lock census tongue ----
axA = fig.add_subplot(gs[0, 0])
im = axA.imshow(lock, aspect='auto', cmap='viridis', origin='lower',
                extent=[es[0], es[-1], rs[0], rs[-1]])
axA.set_xlabel(r'$\eps$ (neighbor coupling, weak limit)'); axA.set_ylabel(r'r (logistic control)')
axA.set_title('(A) Period-4 tongue — coarse lock census\n17×10 grid · 200k steps · seeds 0–2 · lock fraction', fontsize=11)
axA.plot(0.135, 3.8658, 'k*', ms=15, mfc='orange', mec='k', zorder=5)
axA.annotate('core (3.8658, 0.135)', (0.135, 3.8658), textcoords='offset points',
             xytext=(6, -18), fontsize=8, color='white')
cb = fig.colorbar(im, ax=axA, fraction=0.046); cb.set_label('P4 lock fraction', fontsize=9)

# ---- B: boundary Lyapunov spectrum ----
axB = fig.add_subplot(gs[0, 1])
axB.scatter(b_r[b_reg=='L'], b_lyap[b_reg=='L'], c='#1f77b4', s=30,
            edgecolors='k', linewidths=0.4, label='left tip (r 3.78–3.83)')
axB.scatter(b_r[b_reg=='R'], b_lyap[b_reg=='R'], c='#d62728', s=30,
            edgecolors='k', linewidths=0.4, label='right tip (r 3.90–3.96)')
axB.axhline(0, color='gray', lw=0.8, ls=':')
axB.axhline(0.01, color='k', lw=0.9, ls='--', alpha=0.6)
nL = int(((b_reg=='L') & (b_lyap>0.01)).sum()); nR = int(((b_reg=='R') & (b_lyap>0.01)).sum())
axB.text(3.902, 0.0115, '+0.01 chaos threshold', fontsize=8)
axB.set_xlabel(r'r'); axB.set_ylabel(r'$\lambda_{\max}$ (Lyapunov exponent, 1/it)')
axB.set_title('(B) Anti-chaotic boundary — Lyapunov spectrum\n'
              f'{nL}/33 left-tip points exceed +0.01 (all 3 transient); all 33 right-tip points ≤ 0', fontsize=11)
axB.legend(fontsize=8, loc='lower left'); axB.set_xlim(3.77, 3.97)

# ---- C: symbolic memory M(tau) vs eps ----
axC = fig.add_subplot(gs[1, 0])
axC.axvspan(0.10, 0.12, color='#ff7f0e', alpha=0.15)
axC.text(0.0585, 40, 'gap: noisy → locked P4\n(ε≈0.10–0.12 at r≈3.87)', fontsize=8, color='#b3560a')
axC.semilogy(A_f, A_t, 'o-', c='#1f77b4', ms=8, lw=1.5,
             label='A: detuned points (τ_max=1, 2)')
axC.semilogy(B_f, B_t, 's-', c='#d62728', ms=8, lw=1.5,
             label='B: r=3.865 tongue points (τ_max=64)')
axC.scatter(C_f, C_t, c='gray', s=34, marker='x', zorder=5,
            label='C: 10 random (r,ε) points')
axC.set_xlabel(r'$\eps$ at which each point was evaluated'); axC.set_ylabel(r'$\tau_{max}$ (max delay, correct ≥ 0.75)')
axC.set_title('(C) Symbolic memory M(τ): persistence to τ=64 only inside the locked tongue\n'
              'perfect P4 symbol prediction ↔ tongue interior; chaos/detuned → decay by τ=1–4', fontsize=11)
axC.legend(fontsize=8); axC.grid(alpha=0.3, which='both'); axC.set_ylim(0.5, 200)

# ---- D: C4 robustness ----
axD = fig.add_subplot(gs[1, 1])
axD.plot(eps_c, P4s_c, 'o-', c='#2ca02c', ms=8, lw=1.5,
         label=r'$P4_{share}$ vs $\eps$ (r=3.88, τ=4×10⁵, seed 42)')
axD.axvspan(0.11, 0.18, color='green', alpha=0.08)
axD.set_xlabel(r'$\eps$'); axD.set_ylabel(r'$P4_{share}$  /  $C4$')
axD.set_title('(D) C4-robustness: exact period-4 survives re-seeding\n'
              'ε-window [0.12, 0.17] at r=3.88; C4 settles to 1.0 by τ=10³', fontsize=11)
axD2 = axD.twinx()
axD2.semilogx(Ts, c4_wb, 'D', c='#1f77b4', ms=9, mfc='none', label='C4, World-B point')
axD2.semilogx(Ts, c4_tong, '^', c='#ff7f0e', ms=9, mfc='none', label='C4, tongue core')
axD2.set_ylim(0.85, 1.05); axD2.set_ylabel('C4')
h1, l1 = axD.get_legend_handles_labels(); h2, l2 = axD2.get_legend_handles_labels()
axD.legend(h1+h2, l1+l2, fontsize=8, loc='center left'); axD.grid(alpha=0.3)

fig.suptitle('Period-4 tongue of the coupled logistic lattice (N=32) — consolidated evidence, World C ×4 jobs',
             fontsize=13, y=0.975)
fig.savefig(f'{WS}/p4_refined_deliverable.png', dpi=150)
print('saved', f'{WS}/p4_refined_deliverable.png')
print(f'nL={nL}, nR={nR}')
