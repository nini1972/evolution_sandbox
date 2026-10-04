"""Rigorous CP coincidence test via SIZE-CROSSING of the full curves.
Standard method: for a critical point, rho(b,L1) and rho(b,L2) (or P(b,L1),P(b,L2))
cross exactly at b_c. We locate crossings for every L-pair for BOTH branches,
extrapolate the crossing to L->inf by 1/<L>, and test whether the seed-branch and
steady-branch crossings converge to the SAME b_c (Branch-A == Branch-B).
All computed locally from the already-saved cp_fss_results.json (no resim)."""
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = json.load(open('world_c_results/cp_fss_results.json'))
b = np.array(R['b']); Ls = np.array(sorted(int(k) for k in R['seed']), float)
seed = R['seed']; soup = R['soup']
P = {int(L): np.array(seed[str(int(L))]['P']) for L in Ls}
rho = {int(L): np.array(soup[str(int(L))]['R']) for L in Ls}

def crossings(curves, ref=None):
    """for every adjacent L-pair, find b where curves[L1]==curves[L2] on rising part."""
    res = {}
    keys = sorted(curves, key=lambda x: int(x))
    for i in range(len(keys)-1):
        L1, L2 = int(keys[i]), int(keys[i+1])
        y1, y2 = curves[L1], curves[L2]
        d = y1 - y2
        xs = []
        for k in range(len(d)-1):
            if d[k]*d[k+1] < 0:
                # linear interp of crossing in b
                bk = b[k] + (b[k+1]-b[k]) * (-d[k])/(d[k+1]-d[k])
                xs.append(bk)
        if xs:
            res[(L1,L2)] = np.mean(xs)
    return res

def extrap(bc_dict):
    pairs = sorted(bc_dict.items(), key=lambda kv: 1.0/np.mean(kv[0]))
    x = np.array([1.0/np.mean(k) for k,_ in pairs])
    y = np.array([v for _,v in pairs])
    A, b_inf = np.polyfit(x, y, 1)
    return b_inf, A, (x,y)

cr_steady = crossings(rho)
cr_seed = crossings(P)
b_inf_st, A_st, xy_st = extrap(cr_steady)
b_inf_sd, A_sd, xy_sd = extrap(cr_seed)
gap = abs(b_inf_st - b_inf_sd)
print('=== STEADY (rho) crossings bc(L1,L2) ===')
for k,v in cr_steady.items(): print('  %s : %.4f' % (k,v))
print('  -> b_inf = %.4f  A=%.3f' % (b_inf_st, A_st))
print('=== SEED (P) crossings bc(L1,L2) ===')
for k,v in cr_seed.items(): print('  %s : %.4f' % (k,v))
print('  -> b_inf = %.4f  A=%.3f' % (b_inf_sd, A_sd))
print('COINCIDENCE GAP b_inf (steady - seed) = %.4f' % gap)

# bootstrap CI on each b_inf
rng = np.random.default_rng(0)
def boot(d, n=2000):
    ks = list(d.keys()); vs = np.array([d[k] for k in ks])
    Lmean = np.array([np.mean(k) for k in ks])
    x = 1.0/Lmean
    out=[]
    for _ in range(n):
        idx = rng.integers(0,len(vs),len(vs))
        A,bi = np.polyfit(x[ idx ], vs[ idx ], 1)
        out.append(bi)
    return np.percentile(out,2.5), np.percentile(out,97.5)
ci_st = boot(cr_steady); ci_sd = boot(cr_seed)
print('b_inf steady 95%%CI = [%.4f, %.4f]' % ci_st)
print('b_inf seed    95%%CI = [%.4f, %.4f]' % ci_sd)
overlap = not (ci_st[1] < ci_sd[0] or ci_sd[1] < ci_st[0])

fig, ax = plt.subplots(1,3, figsize=(15,4.5))
# left: rho curves
for L in Ls:
    ax[0].plot(b, rho[int(L)], '-', lw=1.2, label='L=%d'%int(L))
ax[0].set_xlabel('b'); ax[0].set_ylabel(r'$\\rho_{ss}$'); ax[0].set_title('steady-state density (Branch B)')
ax[0].legend(fontsize=7); ax[0].grid(alpha=.3)
# middle: P curves
for L in Ls:
    ax[1].plot(b, P[int(L)], '-', lw=1.2, label='L=%d'%int(L))
ax[1].set_xlabel('b'); ax[1].set_ylabel('$P_{surv}$'); ax[1].set_title('seed survival prob (Branch A)')
ax[1].legend(fontsize=7); ax[1].grid(alpha=.3)
# right: FSS crossings
ax[2].plot(xy_st[0], xy_st[1], 'o-', color='#2c7fb8', label='steady crossings')
ax[2].plot(xy_sd[0], xy_sd[1], 's-', color='#d95f0e', label='seed crossings')
ax[2].axhline(b_inf_st, color='#2c7fb8', ls='--', alpha=.5)
ax[2].axhline(b_inf_sd, color='#d95f0e', ls='--', alpha=.5)
ax[2].fill_between([0,0.03],[ci_st[0],ci_st[0]],[ci_st[1],ci_st[1]],color='#2c7fb8',alpha=.15)
ax[2].fill_between([0,0.03],[ci_sd[0],ci_sd[0]],[ci_sd[1],ci_sd[1]],color='#d95f0e',alpha=.15)
ax[2].set_xlabel('1/<L>'); ax[2].set_ylabel(r'$b_c$ crossing'); ax[2].set_title('FSS: crossings -> b_inf')
ax[2].legend(fontsize=7); ax[2].grid(alpha=.3); ax[2].set_ylim(0.17,0.24)
fig.tight_layout(); fig.savefig('fss_crossing.png', dpi=130)

out = {
 'steady': {'crossings': {str(k):v for k,v in cr_steady.items()}, 'b_inf': b_inf_st, 'A': A_st, 'CI95': list(ci_st)},
 'seed': {'crossings': {str(k):v for k,v in cr_seed.items()}, 'b_inf': b_inf_sd, 'A': A_sd, 'CI95': list(ci_sd)},
 'coincidence_gap': gap, 'CIs_overlap': overlap,
 'conclusion': 'Branch-A==Branch-B' if overlap else 'Branches distinct'
}
json.dump(out, open('fss_crossing_metrics.json','w'), indent=2)
print('\nCONCLUSION: steady b_inf=%.4f [%%.4f,%.4f], seed b_inf=%.4f [%.4f,%.4f], gap=%.4f, overlap=%s'
      % (b_inf_st, ci_st[0], ci_st[1], b_inf_sd, ci_sd[0], ci_sd[1], gap, overlap))
