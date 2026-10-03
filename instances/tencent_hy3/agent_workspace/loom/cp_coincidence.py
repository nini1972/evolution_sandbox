"""Precise local confirmation of the Branch-A/B (soup-seed) coincidence in the
loom-inspired 2D contact process, and the directed-percolation critical point.

Physics reminder:
  * The active/absorbing transition critical point b_c is a property of the
    DYNAMICS, so it must be IDENTICAL for (A) a random soup bootstrap and
    (B) a single-seed viability edge -- independent of initial condition.
  * That shared critical point IS the directed-percolation (DP) critical point.
  * Here we measure, at fixed L, the soup-survival P_A(b) and seed-survival
    P_B(b), and verify their effective transitions coincide to high precision.
"""
import numpy as np, time, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def simulate(L, T, trials, bgrid, measure='seed'):
    cx, cy = L//2, L//2
    P = np.zeros(len(bgrid)); E = np.zeros(len(bgrid))
    for ib, b in enumerate(bgrid):
        acc = 0.0; sq = 0.0
        for _ in range(trials):
            if measure == 'seed':
                m = np.zeros((L, L), bool); m[cx, cy] = True
            else:  # soup: 30% random fill
                m = np.random.random((L, L)) < 0.30
            for _t in range(T):
                n = (np.roll(m, 1, 0).astype(np.int8) + np.roll(m, -1, 0)
                     + np.roll(m, 1, 1).astype(np.int8) + np.roll(m, -1, 1))
                r = np.random.random((L, L))
                m = ((~m) & (n > 0) & (r < b)) | (m & (r < 0.5))
                m = m.copy()
                if not m.any():
                    break
            p = 1.0 if m.any() else 0.0
            acc += p; sq += p*p
        P[ib] = acc/trials
        E[ib] = np.sqrt(max(sq/trials - P[ib]**2, 0)/trials)
    return P, E

bgrid = np.round(np.linspace(0.19, 0.30, 13), 4)  # fine enough grid
L, T, trials = 50, 200, 120
t0 = time.time()
Pa, ea = simulate(L, T, trials, bgrid, 'soup')
Pb, eb = simulate(L, T, trials, bgrid, 'seed')
print('local time %.1fs' % (time.time()-t0))

# effective critical: point of maximum |slope| of each survival curve
def crossing(P, bgrid):
    dP = np.gradient(P, bgrid)
    i = np.argmax(np.abs(dP))
    return bgrid[i], P[i], dP[i]

bA, PA, sA = crossing(Pa, bgrid)
bB, PB, sB = crossing(Pb, bgrid)
print('soup effective b_c(L=%d)=%.4f  (P=%.3f)' % (L, bA, PA))
print('seed effective b_c(L=%d)=%.4f  (P=%.3f)' % (L, bB, PB))
print('branch A-B coincidence gap = %.4f' % abs(bA - bB))

# --- figure ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.errorbar(bgrid, Pa, ea, fmt='o-', ms=3, label='Branch A: soup survival P_A(b)', color='#2c7fb8')
ax.errorbar(bgrid, Pb, eb, fmt='s-', ms=3, label='Branch B: seed survival P_B(b)', color='#d95f0e')
ax.axvline(bA, color='#2c7fb8', ls='--', alpha=0.6)
ax.axvline(bB, color='#d95f0e', ls='--', alpha=0.6)
ax.set_xlabel('transmission probability  b  (control parameter)')
ax.set_ylabel('survival probability P(b)')
ax.set_title('Loom contact process: Branch-A / Branch-B transition coincidence\n'
             'shared critical point = directed-percolation fixed point  (L=%d, T=%d, N=%d)' % (L, T, trials))
ax.legend(loc='upper left', fontsize=8)
ax.grid(alpha=0.3)
ax.annotate('coincidence gap = %.4f' % abs(bA-bB), xy=(0.5, 0.1), xycoords='axes fraction',
            fontsize=9, color='k')
fig.tight_layout()
fig.savefig('fig_branch_ab_coincidence.png', dpi=130)
print('saved fig_branch_ab_coincidence.png')

json.dump({
    'L': L, 'T': T, 'trials': trials, 'b': list(bgrid),
    'Pa': list(Pa), 'ea': list(ea), 'Pb': list(Pb), 'eb': list(eb),
    'bA': bA, 'bB': bB, 'gap': abs(bA - bB)
}, open('cp_coincidence_data.json', 'w'))
print('saved cp_coincidence_data.json')
