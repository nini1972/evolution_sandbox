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
b_P4 = np.array([1 if (x['rho'] >= 0.05 and x['lock'] >= 0.25) else 0 for x in bnd])
# correct boundary statistics (data-driven)
nP4_R = int(b_P4[b_reg == 'R'].sum()); nR = int((b_reg == 'R').sum())
nP4_L = int(b_P4[b_reg == 'L'].sum()); nL = int((b_reg == 'L').sum())
lamP4_R = b_lyap[(b_reg == 'R') & (b_P4 == 1)]
lamP4_L = b_lyap[(b_reg == 'L') & (b_P4 == 1)]
lamNonP4_R = b_lyap[(b_reg == 'R') & (b_P4 == 0)]
lamNonP4_L = b_lyap[(b_reg == 'L') & (b_P4 == 0)]
print('P4/right:', nP4_R, 'of', nR, '| P4 left mean lam:', lamP4_L.mean(), 'right:', lamP4_R.mean())

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
axA.set_xlabel(r'$\varepsilon$ (neighbor coupling, weak limit)'); axA.set_ylabel(r'r (logistic control)')
axA.set_title('(A) Period-4 tongue — coarse lock census\n17×10 grid · 200k steps · seeds 0–2 · lock fraction', fontsize=11)
axA.plot(0.135, 3.8658, 'k*', ms=15, mfc='orange', mec='k', zorder=5)
axA.annotate('core (3.8658, 0.135)', (0.135, 3.8658), textcoords='offset points',
             xytext=(6, -18), fontsize=8, color='white')
cb = fig.colorbar(im, ax=axA, fraction=0.046); cb.set_label('P4 lock fraction', fontsize=9)

# ---- B: boundary Lyapunov spectrum (corrected: two-edge regime) ----
axB = fig.add_subplot(gs[0, 1])
# non-P4 (chaotic background) points as gray scatter
axB.scatter(b_r[(b_reg=='L')&(b_P4==0)], b_lyap[(b_reg=='L')&(b_P4==0)],
            c='#9aa0a6', s=20, alpha=0.55, marker='o', label='non-P4 (left, chaotic bg)')
axB.scatter(b_r[(b_reg=='R')&(b_P4==0)], b_lyap[(b_reg=='R')&(b_P4==0)],
            c='#9aa0a6', s=20, alpha=0.55, marker='o', label='non-P4 (right, chaotic bg)')
# P4 points highlighted
axB.scatter(b_r[(b_reg=='L')&(b_P4==1)], b_lyap[(b_reg=='L')&(b_P4==1)],
            c='#1f77b4', s=70, marker='*', edgecolors='k', linewidths=0.6,
            label=f'P4 @ left cap ({nP4_L}/{nL}, λ̄={lamP4_L.mean():+.3f})')
axB.scatter(b_r[(b_reg=='R')&(b_P4==1)], b_lyap[(b_reg=='R')&(b_P4==1)],
            c='#d62728', s=70, marker='*', edgecolors='k', linewidths=0.6,
            label=f'P4 @ right cap ({nP4_R}/{nR}, λ̄={lamP4_R.mean():+.3f})')
axB.axhline(0, color='k', lw=0.9, ls='--', alpha=0.6)
axB.axhline(0.01, color='gray', lw=0.7, ls=':')
axB.text(3.962, 0.0115, 'λ=+0.01 chaos threshold', fontsize=7.5, ha='right')
# two distinct regimes annotated
axB.annotate('ONSET edge: P4 points sit\nINSIDE chaos (λ≈+0.155)\n→ intermittent P4 (crisis)',
             xy=(3.828, 0.155), xytext=(3.800, 0.075), fontsize=7.5, color='#0d47a1',
             arrowprops=dict(arrowstyle='->', color='#0d47a1', lw=0.9))
axB.annotate('DEATH edge: P4 points are\nSTABLE (λ≈0 or <0) amid\nstrongly chaotic neighbors',
             xy=(3.915, -0.012), xytext=(3.855, 0.30), fontsize=7.5, color='#b71c1c',
             arrowprops=dict(arrowstyle='->', color='#b71c1c', lw=0.9))
axB.set_xlabel(r'r'); axB.set_ylabel(r'$\lambda_{\max}$ (largest Lyapunov, 1/it)')
axB.set_title('(B) Boundary Lyapunov spectrum — two distinct caps\n'
              'P4 (P4-criterion: ρ≥0.05 ∧ lock≥0.25) = stars; grey = non-P4 chaotic background',
              fontsize=10.5)
axB.legend(fontsize=7.6, loc='upper left'); axB.set_xlim(3.77, 3.97); axB.set_ylim(-0.05, 0.42)

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
axC.set_xlabel(r'$\varepsilon$ at which each point was evaluated'); axC.set_ylabel(r'$\tau_{max}$ (max delay, correct ≥ 0.75)')
axC.set_title('(C) Symbolic memory M(τ): persistence to τ=64 only inside the locked tongue\n'
              'perfect P4 symbol prediction ↔ tongue interior; chaos/detuned → decay by τ=1–4', fontsize=11)
axC.legend(fontsize=8); axC.grid(alpha=0.3, which='both'); axC.set_ylim(0.5, 200)

# ---- D: C4 robustness ----
axD = fig.add_subplot(gs[1, 1])
axD.plot(eps_c, P4s_c, 'o-', c='#2ca02c', ms=8, lw=1.5,
         label=r'$P4_{share}$ vs $\varepsilon$ (r=3.88, τ=4×10⁵, seed 42)')
axD.axvspan(0.11, 0.18, color='green', alpha=0.08)
axD.set_xlabel(r'$\varepsilon$'); axD.set_ylabel(r'$P4_{share}$  /  $C4$')
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
print(f'Left cap P4={nP4_L}/{nL} (mean lam={lamP4_L.mean():+.4f}) | Right cap P4={nP4_R}/{nR} (mean lam={lamP4_R.mean():+.4f})')
print(f'Non-P4 left mean lam={lamNonP4_L.mean():+.4f} | Non-P4 right mean lam={lamNonP4_R.mean():+.4f}')
