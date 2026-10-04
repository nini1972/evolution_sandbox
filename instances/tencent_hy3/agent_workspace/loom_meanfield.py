"""Understand WHY the loom's CP sits at b_c ~ 0.24 by deriving its effective
dynamics (mean-field) and measuring live micro-sim activity balance."""
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

def R_rule(x, b):
    nn = (((x>>2)&1) | (((x>>3)&1)<<1) | (((x>>4)&1)<<2) | (((x>>5)&1)<<3))
    return (x ^ ((nn < b).astype(np.int64))) & 1

def mf_fixedpoint(b):
    from math import comb
    def rhs(p):
        s = 0.0
        for c in range(5):
            pc = comb(4, c) * p**c * (1-p)**(4-c)
            s += pc * ((1-p) if c < b else p)
        return s
    ps = np.linspace(0, 1, 4001)
    r = np.array([rhs(p) for p in ps])
    lam = rhs(1e-4) / 1e-4
    p_star = 0.0
    for i in range(len(ps)-1):
        if (r[i]-ps[i])*(r[i+1]-ps[i+1]) < 0 and ps[i] > 0.001:
            p_star = ps[i] - (r[i]-ps[i])*(ps[i+1]-ps[i])/(r[i+1]-r[i])
            break
    return lam, p_star

bs = np.linspace(0.05, 0.9, 171)
lams = []; pstars = []
for b in bs:
    lam, ps_ = mf_fixedpoint(b); lams.append(lam); pstars.append(ps_)
lams = np.array(lams); pstars = np.array(pstars)
sig = np.diff(np.sign(lams - 1.0))
b_mf = bs[np.where(sig)[0][0]] if np.any(sig) else np.nan
b_appear = bs[np.argmax(pstars > 0.001)]
print('MEAN-FIELD bifurcation b_c (lambda=1) ~ %.3f' % b_mf)
print('  b where active branch p_star first appears: %.3f' % b_appear)

# live micro-sim (vectorized per-step over numpy arrays)
def step_2d(grid, b):
    L = grid.shape[0]
    up = np.roll(grid, 1, 0); down = np.roll(grid, -1, 0)
    left = np.roll(grid, 1, 1); right = np.roll(grid, -1, 1)
    neigh = (up | (down<<1) | (left<<2) | (right<<3)).astype(np.int64)
    return (grid ^ (neigh < b)) & 1

def measure(b, L=200, steps=400, seed=1):
    rng = np.random.default_rng(seed)
    grid = rng.integers(0, 2, (L, L), dtype=np.uint8)
    a = []
    for t in range(steps):
        grid = step_2d(grid, b)
        a.append(grid.mean())
    return np.array(a)

a24 = measure(0.24)
print('Live sim at b=0.24: activity -> %.3f' % a24[-1])

fig, ax = plt.subplots(1, 3, figsize=(14, 4))
ax[0].plot(bs, lams, '-', color='#2c7fb8'); ax[0].axhline(1.0, color='k', ls='--', label='lambda=1')
ax[0].axvline(b_mf, color='r', ls=':', label='MF b_c=%.3f'%b_mf)
ax[0].set_xlabel('b'); ax[0].set_ylabel(r'$\lambda$'); ax[0].set_title('Mean-field bifurcation')
ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[1].plot(bs, pstars, '-', color='#d95f0e'); ax[1].set_xlabel('b')
ax[1].set_ylabel(r'$p_*$'); ax[1].set_title('MF order parameter'); ax[1].grid(alpha=.3)
xs = np.arange(256)
for bi, col in [(0.20,'#1b9e77'),(0.24,'#d95f0e'),(0.30,'#7570b3')]:
    rv = np.array([R_rule(x, bi) for x in xs])
    ax[2].plot(bi, np.mean(rv[xs < 128]), 'o', color=col)
    ax[2].plot(bi, np.mean(rv[xs >= 128]), 's', color=col, markerfacecolor='none')
ax[2].set_xlabel('b'); ax[2].set_ylabel('P(out=1|central bit)')
ax[2].set_title('Effective rule'); ax[2].grid(alpha=.3)
ax[2].legend(['b=0.20','b=0.24','b=0.30'], fontsize=8)
fig.tight_layout(); fig.savefig('loom_meanfield.png', dpi=130)

import json
json.dump({'b_mf_bifurcation': float(b_mf), 'b_mf_active_appear': float(b_appear),
           'activity_at_0.24': float(a24[-1])},
          open('loom_meanfield_metrics.json','w'), indent=2)
print('wrote loom_meanfield.png / .json')
