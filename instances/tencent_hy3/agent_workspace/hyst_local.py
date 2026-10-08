import numpy as np
import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rng = np.random.default_rng(20261007)

def step(a, A, X, b):
    a2 = X*a*a + (1.0-X)*(a + b*np.sin(2*np.pi*(a-A)))
    return np.clip(a2, 0.0, 1.0)

def static_curve(L, b_grid, n_trials, T, kind):
    out = np.zeros(len(b_grid))
    for tr in range(n_trials):
        A = rng.random(L)
        for j,b in enumerate(b_grid):
            if kind=='soup':
                a = A.copy()
            else:
                a = rng.random(L)
            X = rng.random((T,L))
            for t in range(T):
                a = step(a, A, X[t], b)
            out[j] += np.mean(np.abs(a-A))
    return out/n_trials

def sweep(L, b_grid, direction, n_trials, T):
    # adiabatic sweep carrying state between consecutive b
    out = np.zeros((n_trials, len(b_grid)))
    order = list(range(len(b_grid))) if direction=='up' else list(range(len(b_grid)-1,-1,-1))
    for tr in range(n_trials):
        A = rng.random(L)
        if direction=='up':
            a = A.copy()  # coherent start
            Xall = rng.random((len(b_grid), T, L))
        else:
            # start at highest b from random (fractured) then carry down
            a = rng.random(L)
            Xall = rng.random((len(b_grid), T, L))
        # we will iterate in order, using Xall[j]
        for j in order:
            b = b_grid[j]
            for t in range(T):
                a = step(a, A, Xall[j,t], b)
            out[tr, j] = np.mean(np.abs(a-A))
    return out.mean(axis=0)

def jump_up(phi, b_grid, thr=0.1):
    for j in range(1,len(b_grid)):
        if phi[j] >= thr and phi[j-1] < thr:
            return b_grid[j]
    return np.nan
def drop_down(phi, b_grid, thr=0.1):
    # last index where phi>=thr
    idxs = np.where(phi>=thr)[0]
    return b_grid[idxs[-1]] if len(idxs) else np.nan

Lvals = [40, 80, 120]
b_grid = np.linspace(0, 0.45, 21)
T = 1500
n = 10
res = {}
plt.figure(figsize=(11,7))
colors = {40:'tab:blue',80:'tab:green',120:'tab:red'}
for L in Lvals:
    sf = static_curve(L, b_grid, max(6, n), T, 'soup')
    ss = static_curve(L, b_grid, max(6, n), T, 'seed')
    fu = sweep(L, b_grid, 'up', n, T)
    bd = sweep(L, b_grid, 'down', n, T)
    b_f = jump_up(fu, b_grid)
    b_b = drop_down(bd, b_grid)
    width = (b_b - b_f) if (b_f==b_f and b_b==b_b) else np.nan
    res[L] = dict(b_f=b_f, b_b=b_b, width=width,
                  b_static_soup=jump_up(sf,b_grid), b_static_seed=drop_down(ss,b_grid))
    print(f"L={L}: fwd_jump={b_f}, bwd_drop={b_b}, HYST_WIDTH={width}, static_soup_jump={res[L]['b_static_soup']}, static_seed_drop={res[L]['b_static_seed']}")
    ax = plt.subplot(2,2, Lvals.index(L)+1)
    ax.plot(b_grid, sf, '-', color='tab:blue', label='static soup')
    ax.plot(b_grid, ss, '-', color='tab:orange', label='static seed')
    ax.plot(b_grid, fu, '--', color='tab:green', lw=2, label='sweep up (coherent->)')
    ax.plot(b_grid, bd, ':', color='tab:red', lw=2, label='sweep down (<-coherent)')
    ax.axvline(b_f, color='tab:green', ls='--', alpha=0.4)
    ax.axvline(b_b, color='tab:red', ls=':', alpha=0.4)
    ax.set_title(f'L={L}  hyst width={width}')
    ax.set_xlabel(r'b'); ax.set_ylabel(r'$\Phi$'); ax.legend(fontsize=7)

# summary axis: hysteresis width vs L
ax = plt.subplot(2,2,4)
ws = [res[L]['width'] for L in Lvals]
ax.plot(Lvals, ws, 'o-', color='black')
for L,w in zip(Lvals,ws):
    ax.annotate(f'{w:.3f}', (L,w), textcoords='offset points', xytext=(5,5))
ax.set_title('hysteresis loop width vs L'); ax.set_xlabel('L'); ax.set_ylabel('width (b_b - b_f)')
plt.tight_layout()
plt.savefig('hyst_loop.png', dpi=130)
json.dump(res, open('hyst_local_results.json','w'), indent=2)
print("saved hyst_loop.png")
