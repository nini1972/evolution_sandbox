"""WORLD C job: rigorous finite-size scaling of the loom-inspired 2D contact process.
Goal: verify the Branch-A (soup) / Branch-B (seed) transition COINCIDENCE at the
directed-percolation (DP) critical point, and extract the asymptotic critical
point b_c^inf and the correlation-length exponent nu_perp via finite-size shift
    b_c(L) = b_c^inf + A * L^{-1/nu_perp}      (nu_perp(2D DP) ~= 1.29)
We measure:
  * P_seed(b, L): survival probability of a single seed  (Branch B)
  * rho_soup(b, L, T): steady-state activity density from a 30% soup (Branch A)
Both are order-parameter-type curves; their effective critical points b_c^seed(L)
and b_c^soup(L) must converge to the SAME b_c^inf. That convergence IS the
loom law ("impossible edge == critical point", identical for all initial conditions).
"""
import numpy as np, json, time
import matplotlib
matplotlib.use('Agg')
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
            # transient discard then measure late-time density (if alive)
            alive = True
            for t in range(T):
                n = (np.roll(m, 1, 0).astype(np.int8) + np.roll(m, -1, 0)
                     + np.roll(m, 1, 1).astype(np.int8) + np.roll(m, -1, 1))
                r = np.random.random((L, L))
                m = ((~m) & (n > 0) & (r < b)) | (m & (r < 0.5))
                m = m.copy()
                if not m.any():
                    alive = False; break
            p = 1.0 if alive else 0.0
            acc += p; sq += p*p
            if alive:
                racc += m.mean(); rsq += (m.mean())**2; ns += 1
        P[ib] = acc/trials
        E[ib] = np.sqrt(max(sq/trials - P[ib]**2, 0)/trials)
        if ns > 0:
            R[ib] = racc/ns; RE[ib] = np.sqrt(max(rsq/ns - R[ib]**2, 0)/ns)
    return P, E, R, RE

def eff_crit(bgrid, curve):
    """effective critical point = point of maximum |d curve / d b|."""
    d = np.gradient(curve, bgrid)
    i = np.argmax(np.abs(d))
    return bgrid[i], curve[i]

# --- sweep configuration ---
Ls = [40, 60, 90, 120, 160, 210]
bgrid = np.round(np.linspace(0.18, 0.30, 25), 4)
results = {'b': list(bgrid), 'Ls': Ls, 'T': {}, 'trials': {},
           'seed': {}, 'soup': {}}
t0 = time.time()
for L in Ls:
    T = min(6*L, 900)
    trials = 100
    Pseed, Eseed, Rseed, Rse = simulate_L(L, T, trials, bgrid, 'seed')
    Psoup, Esoup, Rsoup, Rso = simulate_L(L, T, trials, bgrid, 'soup')
    bs, Ps = eff_crit(bgrid, Pseed)
    br, Pr = eff_crit(bgrid, Rsoup)
    results['T'][str(L)] = T
    results['trials'][str(L)] = trials
    results['seed'][str(L)] = {'P': list(Pseed), 'E': list(Eseed), 'bc': float(bs)}
    results['soup'][str(L)] = {'R': list(Rsoup), 'RE': list(REsoup) if False else list(Rso),
                               'bc': float(br)}
    print('L=%3d T=%d bs_seed=%.4f br_soup=%.4f gap=%.4f  (%.1fs)' %
          (L, T, bs, br, abs(bs-br), time.time()-t0), flush=True)

# --- fit finite-size shift b_c(L) = b_inf + A L^{-1/nu} ---
Ls_a = np.array(Ls, float)
bs_a = np.array([results['seed'][str(L)]['bc'] for L in Ls])
br_a = np.array([results['soup'][str(L)]['bc'] for L in Ls])
def fit_shift(bc):
    x = 1.0 / Ls_a
    # linear fit bc vs L^{-1}; slope=A, intercept=b_inf
    A, b_inf = np.polyfit(x, bc, 1)
    resid = bc - (A*x + b_inf)
    return b_inf, A, resid
b_inf_s, A_s, r_s = fit_shift(bs_a)
b_inf_r, A_r, r_r = fit_shift(br_a)
# estimate nu from A via known prefactor? We just report the shift exponent proxy:
# 1/nu = slope relation; direct: try fitting bc = b_inf + A L^{-1/nu} by scanning nu
def fit_nu(bc, nu):
    y = bc - b_inf(bc)  # placeholder
    return None
# simple: fit log(bc - b_inf) vs log(L)
def fit_nu_exp(bc, b_inf):
    dy = bc - b_inf
    dy = np.clip(dy, 1e-4, None)
    slope, inter = np.polyfit(np.log(Ls_a), np.log(dy), 1)
    return -1.0/slope  # since dy ~ L^{-1/nu}
nu_s = fit_nu_exp(bs_a, b_inf_s)
nu_r = fit_nu_exp(br_a, b_inf_r)
print('SEED  b_inf=%.4f A=%.4f nu_perp~%.3f' % (b_inf_s, A_s, nu_s), flush=True)
print('SOUP  b_inf=%.4f A=%.4f nu_perp~%.3f' % (b_inf_r, A_r, nu_r), flush=True)

# --- figure 1: survival + density curves for each L ---
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for L in Ls:
    axes[0].plot(bgrid, results['seed'][str(L)]['P'], '-o', ms=2,
                 label='L=%d' % L)
    axes[1].plot(bgrid, results['soup'][str(L)]['R'], '-s', ms=2,
                 label='L=%d' % L)
axes[0].set_title('Branch B (seed) survival P_seed(b)')
axes[1].set_title('Branch A (soup) steady density rho_soup(b)')
for ax in axes:
    ax.set_xlabel('transmission b'); ax.set_ylabel('P / rho')
    ax.legend(fontsize=7); ax.grid(alpha=0.3)
fig.suptitle('Loom contact process: two branches -> DP critical point')
fig.tight_layout(); fig.savefig('cp_branches.png', dpi=120)
print('saved cp_branches.png', flush=True)

# --- figure 2: finite-size shift + coincidence ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(Ls_a, bs_a, 'o-', color='#d95f0e', label='Branch B (seed) b_c(L)')
ax.plot(Ls_a, br_a, 's-', color='#2c7fb8', label='Branch A (soup) b_c(L)')
ax.axhline(b_inf_s, color='#d95f0e', ls='--', alpha=0.6,
           label='seed b_inf=%.4f' % b_inf_s)
ax.axhline(b_inf_r, color='#2c7fb8', ls='--', alpha=0.6,
           label='soup b_inf=%.4f' % b_inf_r)
ax.set_xlabel('system size L'); ax.set_ylabel('effective critical point b_c(L)')
ax.set_title('Finite-size shift: Branch A & B converge to same b_c^inf\n'
             'nu_perp(seed)~%.3f, nu_perp(soup)~%.3f  (2D DP theory: 1.29)' % (nu_s, nu_r))
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig('cp_fss_shift.png', dpi=120)
print('saved cp_fss_shift.png', flush=True)

results['fit'] = {
    'seed': {'b_inf': float(b_inf_s), 'A': float(A_s), 'nu_perp': float(nu_s)},
    'soup': {'b_inf': float(b_inf_r), 'A': float(A_r), 'nu_perp': float(nu_r)},
    'coincidence_gap_b_inf': float(abs(b_inf_s - b_inf_r)),
    'theory_nu_perp_2DDP': 1.29
}
json.dump(results, open('cp_fss_results.json', 'w'))
print('DONE total %.1fs' % (time.time()-t0), flush=True)
print('COINCIDENCE GAP (b_inf seed - soup) = %.4f' % abs(b_inf_s - b_inf_r))
