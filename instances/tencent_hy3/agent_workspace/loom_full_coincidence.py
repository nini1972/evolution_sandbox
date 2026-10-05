"""DEFINITIVE loom coincidence test (fast, vectorized).

Single loom dynamics: each cell holds a PAIR (raw bit-plane 0, structure plane 1).
Gate:  b_eff(cell) = b * (1 - gamma * struct_bit)
       y0 = raw XOR (neighborhood(raw) < b_eff)     # structure locally gates raw
       y1 = structure (advects/persists)
This is ONE deterministic emulation of the stochastic rule R(x)=x XOR(NN(x)<b)
but with a local structural bias -- the architectural 'loom' point.

TWO BRANCHES = two order parameters measured on the SAME dynamics & same b:
  Branch A (seed): start sparse raw + random structure; order parameter =
                  seed-survival proxy P = fraction of cells that became active.
  Branch B (steady): start dense; order parameter = steady density rho_ss.
If the CP is intrinsic, both branches' CPs coincide in the L->inf limit.
"""
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

B0_C = 0.38; GAMMA = 0.55

def step(grid, b):
    L = grid.shape[0]
    x0 = (grid >> 4) & 1
    x1 = grid & 1
    up = np.roll(x0, 1, 0); down = np.roll(x0, -1, 0)
    left = np.roll(x0, 1, 1); right = np.roll(x0, -1, 1)
    nn = (up | (down << 1) | (left << 2) | (right << 3)).astype(np.float32)
    b_eff = np.clip(b * (1.0 - GAMMA * x1.astype(np.float32)), 0, 1)
    y0 = ((x0 ^ (nn < b_eff)) & 1).astype(np.uint8)
    y1 = x1.astype(np.uint8)
    return (y0 << 4) | y1

def run(b, L, steps, sparse):
    rng = np.random.default_rng(7*L + int(b*1e5))
    if sparse:
        g0 = (rng.random((L, L)) < 0.12).astype(np.uint8)
    else:
        g0 = (rng.random((L, L)) < 0.5).astype(np.uint8)
    g1 = rng.integers(0, 2, (L, L), dtype=np.uint8)
    grid = (g0 << 4) | g1
    ever = np.zeros((L, L), dtype=bool)
    for t in range(steps):
        ng = step(grid, b)
        ever |= (ng != 0)
        grid = ng
    rho = float(((grid >> 4) & 1).mean())
    P = float(ever.mean())          # fraction that was ever active (survival proxy)
    return P, rho

Ls = np.array([30, 50, 70, 100, 140, 190], dtype=int)
bs = np.round(np.arange(0.18, 0.30, 0.004), 4)
STEPS = 350
Pa = {L: [] for L in Ls}; Rb = {L: [] for L in Ls}
for j, b in enumerate(bs):
    for L in Ls:
        P, rho = run(b, L, STEPS, sparse=True)   # Branch A
        Pa[L].append(P)
        _, rhoB = run(b, L, STEPS, sparse=False)  # Branch B
        Rb[L].append(rhoB)
    if j % 5 == 0: print('b=%.3f' % b)

Pa = {L: np.array(v) for L, v in Pa.items()}
Rb = {L: np.array(v) for L, v in Rb.items()}

def crossings(curves):
    res = {}
    ks = sorted(curves, key=lambda x: int(x))
    for i in range(len(ks)-1):
        L1, L2 = int(ks[i]), int(ks[i+1])
        d = curves[L1] - curves[L2]; xs = []
        for k in range(len(d)-1):
            if d[k]*d[k+1] < 0:
                xs.append(bs[k] + (bs[k+1]-bs[k])*(-d[k])/(d[k+1]-d[k]))
        if xs: res[(L1, L2)] = np.mean(xs)
    return res

def extrap(d):
    pairs = sorted(d.items(), key=lambda kv: 1.0/np.mean(kv[0]))
    x = np.array([1.0/np.mean(k) for k, _ in pairs]); y = np.array([v for _, v in pairs])
    A, bi = np.polyfit(x, y, 1); return bi, A

cr_st = crossings(Rb); cr_sd = crossings(Pa)
bi_st, _ = extrap(cr_st); bi_sd, _ = extrap(cr_sd)
gap = abs(bi_st - bi_sd)
print('\nsteady b_inf = %.4f  seed b_inf = %.4f  gap = %.4f' % (bi_st, bi_sd, gap))

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
for L in Ls: ax[0].plot(bs, Rb[L], '-', lw=1.2, label='L=%d'%L)
ax[0].set_title('Branch B steady density'); ax[0].set_xlabel('b'); ax[0].set_ylabel(r'$\rho_{ss}$'); ax[0].legend(fontsize=7)
for L in Ls: ax[1].plot(bs, Pa[L], '-', lw=1.2, label='L=%d'%L)
ax[1].set_title('Branch A survival proxy'); ax[1].set_xlabel('b'); ax[1].set_ylabel('P'); ax[1].legend(fontsize=7)
fig.tight_layout(); fig.savefig('loom_full_coincidence.png', dpi=130)

json.dump({'b_grid': list(map(float, bs)), 'Ls': list(map(int, Ls)),
           'Pa': {str(L): list(map(float, Pa[L])) for L in Ls},
           'Rb': {str(L): list(map(float, Rb[L])) for L in Ls},
           'steady_binf': float(bi_st), 'seed_binf': float(bi_sd), 'gap': float(gap)},
          open('loom_full_coincidence.json','w'), indent=2)
print('wrote loom_full_coincidence.png / .json')
