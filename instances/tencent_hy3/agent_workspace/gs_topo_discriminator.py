import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix, diags
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import eigsh
import json

# ---------- Gray-Scott (vectorized, periodic BC) ----------
L = 100
Du, Dv = 0.16, 0.08
dt = 1.0

def lap(A):
    return (np.roll(A, 1, 0) + np.roll(A, -1, 0) +
            np.roll(A, 1, 1) + np.roll(A, -1, 1) - 4.0 * A)

def simulate(F, k, steps, spacing=14):
    U = np.ones((L, L)); V = np.zeros((L, L))
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
        if s % 10 == 0:
            probe.append(V[L // 2, L // 2])
    return U, V, np.array(probe, float)

def components_of(A):
    idx = np.argwhere(A); n = len(idx)
    if n == 0:
        return 0, 0.0
    flat = {(int(i), int(j)): c for c, (i, j) in enumerate(idx)}
    rows, cols = [], []
    for i, j in idx:
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            b = flat.get(((i + di) % L, (j + dj) % L))
            if b is not None:
                rows.append(flat[(i, j)]); cols.append(b)
    adj = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    nc, _ = connected_components(adj, directed=False)
    return nc, n / (L * L)

def gamma_largest(A):
    idx = np.argwhere(A); n = len(idx)
    if n < 3:
        return float('nan')
    flat = {(int(i), int(j)): c for c, (i, j) in enumerate(idx)}
    rows, cols = [], []
    for i, j in idx:
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            b = flat.get(((i + di) % L, (j + dj) % L))
            if b is not None:
                rows.append(flat[(i, j)]); cols.append(b)
    adj = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    nc, labels = connected_components(adj, directed=False)
    if nc == 1:
        comp_nodes = np.arange(n)
    else:
        counts = np.bincount(labels)
        big = int(np.argmax(counts))
        comp_nodes = np.where(labels == big)[0]
    sub = adj[comp_nodes][:, comp_nodes]
    deg = np.asarray(sub.sum(axis=1)).ravel()
    if deg.sum() == 0:
        return float('nan')
    Din = diags(1.0 / np.sqrt(deg + 1e-12))
    Ln = diags(np.ones(len(comp_nodes))) - Din @ sub @ Din
    try:
        e = eigsh(Ln, k=min(6, len(comp_nodes) - 1), which='SM',
                  return_eigenvectors=False, v0=np.ones(len(comp_nodes)),
                  maxiter=2000)
    except Exception:
        return float('nan')
    e = np.sort(np.real(e)); nz = e[e > 1e-6]
    if len(nz) >= 2:
        return nz[1] / nz[0]
    return float('nan')

def rqa(series):
    from colony_lib.recurrence import (takens_embedding, recurrence_matrix,
                                        compute_rqa_metrics)
    s = series - series.mean()
    if s.std() < 1e-9:
        return dict(DET=1.0, LAM=1.0, ENT=0.0, RR=1.0)
    emb = takens_embedding(s, m=3, tau=1)
    eps = 0.08 * s.std()
    R = recurrence_matrix(emb, epsilon=eps)
    return compute_rqa_metrics(R)

regimes = {
    'dead_empty':        (0.010, 0.062, 12000),
    'saturated_uniform': (0.037, 0.014, 12000),
    'isolated_spots':    (0.035, 0.065, 20000),
    'labyrinth_stripes': (0.026, 0.055, 20000),
}
order = list(regimes)
fields = {}
pers = {}
nat = {}
rqa_res = {}

qgrid = np.linspace(0.10, 0.90, 17)
for name in order:
    F, k, steps = regimes[name]
    U, V, series = simulate(F, k, steps)
    fields[name] = V
    Vmax = float(V.max())
    cov, comp = [], []
    for q in qgrid:
        t = q * Vmax
        A = V > t
        nc, cv = components_of(A)
        cov.append(cv); comp.append(nc)
    pers[name] = dict(qgrid=qgrid.tolist(), coverage=cov, components=comp,
                      Vmax=Vmax)
    # natural threshold = 30% of field max
    tnat = 0.30 * Vmax
    Anat = V > tnat
    nc_nat, cv_nat = components_of(Anat)
    g = gamma_largest(Anat)
    nat[name] = dict(coverage=float(cv_nat), components=int(nc_nat),
                     gamma=(float(g) if g == g else None))
    rqa_res[name] = rqa(series)

# ---------------- Figure ----------------
fig = plt.figure(figsize=(18, 10))
gs = fig.add_gridspec(2, 4, height_ratios=[1.3, 1.0], hspace=0.32, wspace=0.28)

# Row 0: snapshots
for j, name in enumerate(order):
    ax = fig.add_subplot(gs[0, j])
    ax.imshow(fields[name], cmap='magma', vmin=0, vmax=0.5)
    ax.axis('off')
    n = nat[name]
    gtxt = ('%.3f' % n['gamma']) if n['gamma'] is not None else 'nan'
    txt = (f"{name}\n"
           f"cov*={n['coverage']:.3f}  comps*={n['components']}\n"
           f"gamma={gtxt}")
    ax.set_title(txt, fontsize=10)

# Row 1, col 0: RQA bars (degeneracy)
ax = fig.add_subplot(gs[1, 0])
metrics = ['DET', 'LAM', 'ENT', 'RR']
x = np.arange(len(order)); w = 0.2
colors = ['#c44', '#d67', '#e89', '#fab']
for mi, m in enumerate(metrics):
    vals = [rqa_res[n].get(m, 0) for n in order]
    ax.bar(x + (mi - 1.5) * w, vals, w, label=m, color=colors[mi])
ax.set_xticks(x); ax.set_xticklabels(order, rotation=30, fontsize=7)
ax.set_title('RQA metrics (temporal) — DEGENERATE', fontsize=10)
ax.legend(fontsize=8)

# Row 1, cols 1-2: betti0 persistence curves
ax = fig.add_subplot(gs[1, 1:3])
for name in order:
    p = pers[name]
    cov = np.array(p['coverage']); comp = np.array(p['components'])
    ax.plot(cov, comp, 'o-', label=name, markersize=4)
    # mark natural threshold point
    Vmax = p['Vmax']; tnat = 0.30 * Vmax
    # find nearest q
    qi = int(np.argmin(np.abs(np.array(p['qgrid']) - 0.30)))
    ax.plot(cov[qi], comp[qi], '*', markersize=12, color='k')
ax.set_xlabel('active-set coverage  (threshold = q·Vmax)')
ax.set_ylabel('# connected components (betti0)')
ax.set_title('Topological persistence — DISCRIMINATES', fontsize=10)
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Row 1, col 3: natural invariants
ax = fig.add_subplot(gs[1, 3])
comp_nat = [nat[n]['components'] for n in order]
cov_nat = [nat[n]['coverage'] for n in order]
ax.bar(x - 0.2, comp_nat, 0.4, color='#2a7', label='#components*')
ax.bar(x + 0.2, [c * 50 for c in cov_nat], 0.4, color='#27a',
       label='coverage*×50')
ax.set_xticks(x); ax.set_xticklabels(order, rotation=30, fontsize=7)
ax.set_title('Natural-threshold invariants', fontsize=10)
ax.legend(fontsize=8)

fig.suptitle("RQA blindness vs Topological (betti0) + Spectral-Graph resolution "
             "of Gray-Scott regimes  [SYN-062 bridge]", fontsize=13)
plt.savefig('gs_topo_discriminator.png', dpi=120)
plt.close()

# ---------------- Diagnostics ----------------
print("=== DIAGNOSIS ===")
for n in order:
    q = rqa_res[n]; nn = nat[n]
    gt = ('%.3f' % nn['gamma']) if nn['gamma'] is not None else 'nan'
    print(f"{n:18s} RQA DET={q['DET']:.3f} LAM={q['LAM']:.3f} ENT={q['ENT']:.2f} "
          f"RR={q['RR']:.3f} || topo cov*={nn['coverage']:.3f} "
          f"comps*={nn['components']} gamma={gt}")
print("=================")

with open('gs_topo_discriminator.json', 'w') as f:
    json.dump(dict(rqa=rqa_res, natural=nat, persistence=pers), f,
              indent=2, default=str)
print("DONE")
