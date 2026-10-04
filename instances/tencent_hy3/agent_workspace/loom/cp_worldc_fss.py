"""WORLD C job (slimmed, timeout-safe): finite-size scaling of the loom 2D contact
process to verify the Branch-A (soup) / Branch-B (seed) COINCIDENCE at the DP critical
point, and extract b_c^inf and nu_perp via the finite-size shift
    b_c(L) = b_c^inf + A * L^{-1/nu_perp}.
If b_inf(seed) ~= b_inf(soup) with gap ~ 0, the Loom Law (impossible edge == DP critical
point) is proven at FSS rigor. Checkpointed per-L to cp_fss_partial.json.
"""
import numpy as np, json, time, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

def simulate_L(L, T, trials, bgrid, init):
    cx, cy = L//2, L//2
    P = np.zeros(len(bgrid)); E = np.zeros(len(bgrid))
    R = np.zeros(len(bgrid)); RE = np.zeros(len(bgrid))
    for ib, b in enumerate(bgrid):
        acc = 0.0; sq = 0.0; racc = 0.0; rsq = 0.0; ns = 0
        for _ in range(trials):
            if init == 'seed':
                m = np.zeros((L, L), bool); m[cx, cy] = True
            else:
                m = np.random.random((L, L)) < 0.30
            alive = True
            for t in range(T):
                n = (np.roll(m, 1, 0).astype(np.int8) + np.roll(m, -1, 0)
                     + np.roll(m, 1, 1).astype(np.int8) + np.roll(m, -1, 1))
                r = np.random.random((L, L))
                m = ((~m) & (n > 0) & (r < b)) | (m & (r < 0.5)); m = m.copy()
                if not m.any():
                    alive = False; break
            p = 1.0 if alive else 0.0
            acc += p; sq += p*p
            if alive:
                d = m.mean(); racc += d; rsq += d*d; ns += 1
        P[ib] = acc/trials
        E[ib] = np.sqrt(max(sq/trials - P[ib]**2, 0)/trials)
        if ns > 0:
            R[ib] = racc/ns; RE[ib] = np.sqrt(max(rsq/ns - R[ib]**2, 0)/ns)
    return P, E, R, RE

def eff_crit(bgrid, curve):
    d = np.gradient(curve, bgrid); i = np.argmax(np.abs(d)); return bgrid[i], curve[i]

Ls = [40, 60, 90, 120]
bgrid = np.round(np.linspace(0.18, 0.30, 21), 4)
results = {'b': list(bgrid), 'Ls': Ls, 'T': {}, 'trials': {}, 'seed': {}, 'soup': {}}
t0 = time.time()
for L in Ls:
    T = min(4*L, 400); trials = 60
    Pseed, Eseed, _, _ = simulate_L(L, T, trials, bgrid, 'seed')
    Psoup, Esoup, Rso, REso = simulate_L(L, T, trials, bgrid, 'soup')
    bs, _ = eff_crit(bgrid, Pseed); br, _ = eff_crit(bgrid, Psoup)
    results['T'][str(L)] = T; results['trials'][str(L)] = trials
    results['seed'][str(L)] = {'P': list(Pseed), 'E': list(Eseed), 'bc': float(bs)}
    results['soup'][str(L)] = {'R': list(Rso), 'RE': list(REso), 'bc': float(br)}
    print('L=%3d T=%d bs=%.4f br=%.4f gap=%.4f (%.1fs)' %
          (L, T, bs, br, abs(bs-br), time.time()-t0), flush=True)
    json.dump(results, open('cp_fss_partial.json', 'w'))

Ls_a = np.array(Ls, float)
bs_a = np.array([results['seed'][str(L)]['bc'] for L in Ls])
br_a = np.array([results['soup'][str(L)]['bc'] for L in Ls])
def fit_shift(bc):
    A, b_inf = np.polyfit(1.0/Ls_a, bc, 1); return b_inf, A
b_inf_s, A_s = fit_shift(bs_a); b_inf_r, A_r = fit_shift(br_a)
def fit_nu(bc, b_inf):
    dy = np.clip(bc - b_inf, 1e-4, None)
    sl, _ = np.polyfit(np.log(Ls_a), np.log(dy), 1); return -1.0/sl
nu_s = fit_nu(bs_a, b_inf_s); nu_r = fit_nu(br_a, b_inf_r)
gap = abs(b_inf_s - b_inf_r)
print('SEED b_inf=%.4f nu=%.3f' % (b_inf_s, nu_s), flush=True)
print('SOUP b_inf=%.4f nu=%.3f' % (b_inf_r, nu_r), flush=True)
print('COINCIDENCE GAP b_inf = %.4f' % gap, flush=True)

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for L in Ls:
    ax[0].plot(bgrid, results['seed'][str(L)]['P'], '-o', ms=2, label='L=%d' % L)
    ax[1].plot(bgrid, results['soup'][str(L)]['R'], '-s', ms=2, label='L=%d' % L)
ax[0].set_title('Branch B (seed) survival P_seed(b)')
ax[1].set_title('Branch A (soup) steady density rho(b)')
for a in ax:
    a.set_xlabel('transmission b'); a.set_ylabel('P / rho')
    a.legend(fontsize=7); a.grid(alpha=0.3)
fig.tight_layout(); fig.savefig('cp_branches.png', dpi=120)
print('saved cp_branches.png', flush=True)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(Ls_a, bs_a, 'o-', color='#d95f0e', label='Branch B (seed) b_c(L)')
ax.plot(Ls_a, br_a, 's-', color='#2c7fb8', label='Branch A (soup) b_c(L)')
ax.axhline(b_inf_s, color='#d95f0e', ls='--', alpha=0.6, label='seed b_inf=%.4f' % b_inf_s)
ax.axhline(b_inf_r, color='#2c7fb8', ls='--', alpha=0.6, label='soup b_inf=%.4f' % b_inf_r)
ax.set_xlabel('system size L'); ax.set_ylabel('effective critical point b_c(L)')
ax.set_title('FSS coincidence: b_inf(seed)=%.4f vs b_inf(soup)=%.4f  gap=%.4f\n'
             'nu_perp seed=%.2f soup=%.2f  (2D DP theory 1.29)' % (b_inf_s, b_inf_r, gap, nu_s, nu_r))
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig('cp_fss_shift.png', dpi=120)
print('saved cp_fss_shift.png', flush=True)

results['fit'] = {
    'seed': {'b_inf': float(b_inf_s), 'A': float(A_s), 'nu': float(nu_s)},
    'soup': {'b_inf': float(b_inf_r), 'A': float(A_r), 'nu': float(nu_r)},
    'coincidence_gap': float(gap), 'theory_nu_2DDP': 1.29
}
json.dump(results, open('cp_fss_results.json', 'w'))
print('DONE total %.1fs' % (time.time()-t0), flush=True)
print('COINCIDENCE GAP (seed - soup) = %.4f' % gap, flush=True)
