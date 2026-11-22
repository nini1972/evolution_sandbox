import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix, diags
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import eigsh
import json, os

# ---- Gray-Scott simulation (vectorized, periodic BC) ----
L = 100
Du, Dv = 0.16, 0.08
dt = 1.0

def lap(A):
    return (np.roll(A, 1, 0) + np.roll(A, -1, 0) +
            np.roll(A, 1, 1) + np.roll(A, -1, 1) - 4.0 * A)

def simulate(F, k, steps, spacing=14):
    rng = np.random.default_rng(7)
    U = np.ones((L, L)); V = np.zeros((L, L))
    # regular lattice of seeds (keeps spots isolated / gives clean stripes)
    for i in range(spacing // 2, L, spacing):
        for j in range(spacing // 2, L, spacing):
            U[i-2:i+2, j-2:j+2] = 0.5
            V[i-2:i+2, j-2:j+2] = 0.25
    probe = []
    for s in range(steps):
        Lu, Lv = lap(U), lap(V)
        uvv = U * V * V
        U += (Du * Lu - uvv + F * (1.0 - U)) * dt
        V += (Dv * Lv + uvv - (F + k) * V) * dt
        if s % 20 == 0:
            probe.append(V[L // 2, L // 2])
    return U, V, np.array(probe, float)

def active_graph(V, thresh=0.20):
    A = (V > thresh)
    n_active = int(A.sum())
    if n_active == 0:
        return dict(n_active=0, n_components=0, lam1=0.0, lam2=0.0,
                    gamma=float('inf'), e_small=[])
    idx = np.argwhere(A)
    flat = {(int(i), int(j)): c for c, (i, j) in enumerate(idx)}
    rows, cols = [], []
    for i, j in idx:
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = (i + di) % L, (j + dj) % L
            b = flat.get((ni, nj))
            if b is not None:
                rows.append(flat[(i, j)]); cols.append(b)
    N = n_active
    adj = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N))
    n_comp, _ = connected_components(adj, directed=False)
    deg = np.asarray(adj.sum(axis=1)).ravel()
    Din = diags(1.0 / np.sqrt(deg + 1e-12))
    Lnorm = diags(np.ones(N)) - Din @ adj @ Din
    k = min(10, N - 1)
    try:
        e = eigsh(Lnorm, k=k, which='SM', return_eigenvectors=False,
                  v0=np.ones(N), maxiter=2000)
    except Exception:
        e = eigsh(Lnorm, k=k, which='LM', return_eigenvectors=False,
                  v0=np.ones(N))
    e = np.sort(np.real(e))
    nz = e[e > 1e-6]
    if len(nz) >= 2:
        lam1, lam2 = nz[0], nz[1]; gamma = lam2 / lam1
    elif len(nz) == 1:
        lam1, lam2, gamma = nz[0], nz[0], 1.0
    else:
        lam1 = lam2 = 0.0; gamma = float('inf')
    return dict(n_active=n_active, n_components=int(n_comp),
                lam1=float(lam1), lam2=float(lam2),
                gamma=float(gamma), e_small=[float(x) for x in e[:6]])

def rqa(series):
    from colony_lib.recurrence import (takens_embedding, recurrence_matrix,
                                        compute_rqa_metrics)
    s = series - series.mean()
    if s.std() < 1e-9:  # constant (dead) signal
        return dict(DET=1.0, LAM=1.0, ENT=0.0, RR=1.0, Lmax=float(len(s)))
    emb = takens_embedding(s, m=3, tau=1)
    eps = 0.08 * s.std()
    R = recurrence_matrix(emb, epsilon=eps)
    return compute_rqa_metrics(R)

regimes = {
    'dead_empty':        dict(F=0.010, k=0.062, steps=12000),  # V decays -> empty
    'saturated_uniform': dict(F=0.037, k=0.014, steps=12000),  # V fills space
    'isolated_spots':    dict(F=0.035, k=0.065, steps=20000),  # discrete spots
    'labyrinth_stripes': dict(F=0.026, k=0.055, steps=20000),  # connected stripes
}

results = {}
snaps = {}
for name, r in regimes.items():
    U, V, series = simulate(r['F'], r['k'], r['steps'])
    g = active_graph(V)
    q = rqa(series)
    results[name] = dict(F=r['F'], k=r['k'], graph=g, rqa=q)
    snaps[name] = V

# ---- Figure ----
order = list(regimes.keys())
fig, ax = plt.subplots(2, 4, figsize=(18, 8))
for j, name in enumerate(order):
    ax[0, j].imshow(snaps[name], cmap='magma', vmin=0, vmax=0.5)
    ax[0, j].set_title(f"{name}\n(F={results[name]['F']}, k={results[name]['k']})")
    ax[0, j].axis('off')
    g = results[name]['graph']
    txt = (f"active px: {g['n_active']}\n"
           f"components: {g['n_components']}\n"
           f"λ1={g['lam1']:.4f}  γ={g['gamma']:.3f}")
    ax[0, j].text(0.02, 0.95, txt, transform=ax[0, j].transAxes,
                  color='white', fontsize=9, va='top',
                  bbox=dict(boxstyle='round', fc='black', alpha=0.5))

# RQA bars (show degeneracy)
metrics = ['DET', 'LAM', 'ENT', 'RR']
for mi, m in enumerate(metrics):
    vals = [results[n]['rqa'].get(m, 0) for n in order]
    ax[1, mi].bar(order, vals, color='#c44')
    ax[1, mi].set_title(f"RQA {m} (temporal) — DE/GENERATE")
    ax[1, mi].set_ylim(0, 1.05 if m != 'ENT' else max(vals)*1.2+0.01)
    ax[1, mi].tick_params(axis='x', rotation=35, labelsize=8)

# n_components + gamma panel replaces 4th bottom? use ax[1,3] for components/gamma
comp = [results[n]['graph']['n_components'] for n in order]
gam = [min(results[n]['graph']['gamma'], 50) for n in order]
ax[1, 3].bar(np.arange(len(order)) - 0.2, comp, width=0.4, color='#2a7',
             label='#components (topology)')
ax[1, 3].bar(np.arange(len(order)) + 0.2, gam, width=0.4, color='#27a',
             label='γ=λ2/λ1 (clamped 50)')
ax[1, 3].set_xticks(range(len(order)))
ax[1, 3].set_xticklabels(order, rotation=35, fontsize=8)
ax[1, 3].set_title("Spectral graph invariants — DISCRIMINATE")
ax[1, 3].legend(fontsize=8)
fig.suptitle("RQA blindness vs Spectral-Graph resolution of Gray-Scott regimes",
             fontsize=14)
plt.tight_layout()
plt.savefig('spectral_discrimination.png', dpi=120)
plt.close()

with open('spectral_discrimination.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

# textual diagnosis
diag = []
for n in order:
    g = results[n]['graph']; q = results[n]['rqa']
    diag.append(f"{n}: comp={g['n_components']} γ={g['gamma']:.3f} | "
                f"RQA DET={q['DET']:.3f} LAM={q['LAM']:.3f} ENT={q['ENT']:.2f}")
print("DIAGNOSIS")
for d in diag:
    print(" ", d)
print("DONE")
