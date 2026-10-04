"""Corrected re-analysis of the loom 2D-CP FSS data (cp_fss_results.json).
Fixes the nu sign bug and tests the Branch-A==Branch-B COINCIDENCE at the DP
critical point via:
  (a) corrected finite-size-shift fits b_inf = b_c(L) + A L^{-1/nu}  (proper sign),
  (b) a JOINT data-collapse: find the single (b_c, nu) that collapses BOTH
      branches' curves; if both collapse well under one shared pair, the two
      branches coincide at a single critical point.
"""
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = json.load(open('world_c_results/cp_fss_results.json'))
b = np.array(R['b']); Ls = np.array(R['Ls'], float)
seed = R['seed']; soup = R['soup']
P = {int(L): np.array(seed[str(int(L))]['P']) for L in Ls}
rho = {int(L): np.array(soup[str(int(L))]['R']) for L in Ls}

# ---- (a) corrected FSS shift fits ----
def bc_inf_fit(bc):
    A, b_inf = np.polyfit(1.0/Ls, bc, 1)   # bc(L) = A*(1/L) + b_inf
    return b_inf, A
def nu_from(bc, b_inf):
    dy = np.clip(b_inf - bc, 1e-4, None)   # finite-size correction >= 0
    sl, _ = np.polyfit(np.log(Ls), np.log(dy), 1)
    return -1.0/sl
bs = np.array([seed[str(int(L))]['bc'] for L in Ls])
br = np.array([soup[str(int(L))]['bc'] for L in Ls])
b_inf_s, A_s = bc_inf_fit(bs); b_inf_r, A_r = bc_inf_fit(br)
nu_s = nu_from(bs, b_inf_s); nu_r = nu_from(br, b_inf_r)
gap = abs(b_inf_s - b_inf_r)
print('SEED bc(L)=', np.round(bs,3), ' b_inf=%.4f A=%.3f nu=%.2f' % (b_inf_s, A_s, nu_s))
print('SOUP bc(L)=', np.round(br,3), ' b_inf=%.4f A=%.3f nu=%.2f' % (b_inf_r, A_r, nu_r))
print('coincidence gap b_inf = %.4f' % gap)

# ---- (b) joint data-collapse test ----
def collapse_err(b_c, nu, curves, ref=0.30):
    """spread (std across sizes) of curves rescaled by x=(b-b_c)L^(1/nu),
    amplitude-normalized by ref (active-state density ~0.30)."""
    xs = []; ys = []
    for L in Ls:
        x = (b - b_c) * (L**(1.0/nu))
        ys.append(curves[int(L)] / ref)
        xs.append(x)
    xgrid = np.linspace(min(x.min() for x in xs), max(x.max() for x in xs), 200)
    vals = []
    for x, y in zip(xs, ys):
        vals.append(np.interp(xgrid, x, y, left=np.nan, right=np.nan))
    M = np.nanmean(vals, 0); S = np.nanstd(vals, 0)
    good = ~np.isnan(M)
    return np.sqrt(np.mean(S[good]**2))

# search shared (b_c, nu) minimizing total error across both branches
bc_grid = np.linspace(0.17, 0.24, 29)
nu_grid = np.linspace(1.0, 1.7, 36)
best = None
Emat = np.zeros((len(nu_grid), len(bc_grid)))
for i, nu in enumerate(nu_grid):
    for j, bc in enumerate(bc_grid):
        e = collapse_err(bc, nu, rho) + collapse_err(bc, nu, P)
        Emat[i, j] = e
        if best is None or e < best[0]:
            best = (e, bc, nu)
e_best, bc_best, nu_best = best
print('SHARED collapse: bc=%.4f nu=%.3f err=%.4f' % (bc_best, nu_best, e_best))

# null hypothesis: impose each branch's OWN bc on the OTHER (should be worse if
# they don't coincide). Use the soup individual bc on seed and vice versa.
e_seed_under_soup = collapse_err(b_inf_r, nu_r, P)
e_soup_under_seed = collapse_err(b_inf_s, nu_s, rho)
print('seed curves collapsed under SOUP (bc,nu): err=%.4f' % e_seed_under_soup)
print('soup curves collapsed under SEED (bc,nu): err=%.4f' % e_soup_under_seed)

# ---- figures ----
fig, ax = plt.subplots(2, 2, figsize=(13, 9))
ax[0,0].plot(Ls, bs, 'o-', color='#d95f0e', label='seed bc(L)')
ax[0,0].plot(Ls, br, 's-', color='#2c7fb8', label='soup bc(L)')
ax[0,0].axhline(b_inf_s, color='#d95f0e', ls='--', alpha=.5, label='seed b_inf=%.3f'%b_inf_s)
ax[0,0].axhline(b_inf_r, color='#2c7fb8', ls='--', alpha=.5, label='soup b_inf=%.3f'%b_inf_r)
ax[0,0].axhline(bc_best, color='k', ls=':', label='shared collapse bc=%.3f'%bc_best)
ax[0,0].set_xlabel('L'); ax[0,0].set_ylabel('bc(L)'); ax[0,0].legend(fontsize=7); ax[0,0].grid(alpha=.3)
ax[0,0].set_title('FSS shift (corrected)')

# collapse error landscape
im = ax[0,1].imshow(Emat, origin='lower', aspect='auto',
    extent=[bc_grid[0],bc_grid[-1],nu_grid[0],nu_grid[-1]])
ax[0,1].scatter([bc_best],[nu_best], color='r', marker='x', s=80, label='shared min')
ax[0,1].set_xlabel('b_c'); ax[0,1].set_ylabel('nu'); ax[0,1].set_title('joint collapse error')
ax[0,1].legend(loc='upper right'); plt.colorbar(im, ax=ax[0,1])

# collapse of soup under shared params
for L in Ls:
    x = (b - bc_best) * (L**(1.0/nu_best))
    ax[1,0].plot(x, rho[int(L)]/0.30, '-', lw=1, alpha=.8, label='L=%d'%int(L))
ax[1,0].set_xlabel('(b-bc)L^{1/nu}'); ax[1,0].set_ylabel('rho/0.30')
ax[1,0].set_title('SOUP branch collapse (shared bc,nu)'); ax[1,0].legend(fontsize=7); ax[1,0].grid(alpha=.3)

for L in Ls:
    x = (b - bc_best) * (L**(1.0/nu_best))
    ax[1,1].plot(x, P[int(L)], '-', lw=1, alpha=.8, label='L=%d'%int(L))
ax[1,1].set_xlabel('(b-bc)L^{1/nu}'); ax[1,1].set_ylabel('P_surv')
ax[1,1].set_title('SEED branch collapse (shared bc,nu)'); ax[1,1].legend(fontsize=7); ax[1,1].grid(alpha=.3)
fig.tight_layout(); fig.savefig('fss_coincidence.png', dpi=130)

out = {
 'seed': {'bc_L': list(bs), 'b_inf': b_inf_s, 'A': A_s, 'nu': nu_s},
 'soup': {'bc_L': list(br), 'b_inf': b_inf_r, 'A': A_r, 'nu': nu_r},
 'coincidence_gap_binf': gap,
 'shared_collapse': {'bc': bc_best, 'nu': nu_best, 'err': e_best},
 'seed_under_soup_err': e_seed_under_soup, 'soup_under_seed_err': e_soup_under_seed,
 'theory': {'nu_2DDP': 1.29, 'rho_active': 0.30}
}
json.dump(out, open('fss_coincidence_metrics.json','w'), indent=2)
print('wrote fss_coincidence.png and fss_coincidence_metrics.json')
print('SUMMARY: gap_binf=%.4f  shared_bc=%.4f shared_nu=%.3f  (2D DP nu=1.29)'
      % (gap, bc_best, nu_best))
