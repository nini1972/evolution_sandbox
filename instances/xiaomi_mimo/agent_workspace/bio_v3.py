#!/usr/bin/env python3
"""Add biological systems to morphospace - Part 1: features and simulations"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import json

with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

def safe_entropy(ts, bins=20):
    ts = np.array(ts).flatten()
    ts = ts[np.isfinite(ts)]
    if len(ts) < bins: return 0.5
    h, _ = np.histogram(ts, bins=bins, density=True)
    h = h[h > 0]
    return float(np.clip(-np.sum(h * np.log(h + 1e-10)), 0, 10))

def safe_fractal(ts):
    ts = np.array(ts).flatten()
    if len(ts) < 20: return 1.0
    ts = ts[np.isfinite(ts)]
    ts_n = (ts - ts.min()) / (ts.max() - ts.min() + 1e-10)
    scales = [int(s) for s in np.logspace(0.3, np.log10(len(ts)//3), 8) if s >= 2]
    if len(scales) < 3: return 1.0
    counts = []
    for s in scales:
        boxes = set()
        for i in range(0, len(ts_n) - s, s):
            boxes.add((i // s, int(ts_n[i] * s)))
        counts.append(len(boxes))
    coeffs = np.polyfit(np.log(scales), np.log(np.array(counts) + 1), 1)
    return float(np.clip(coeffs[0], 1.0, 2.0))

def safe_lyap(ts, dt=1.0):
    ts = np.array(ts).flatten()
    ts = ts[np.isfinite(ts)]
    if len(ts) < 50: return 0.0
    n = len(ts) // 2
    d0 = abs(ts[0] - ts[n]) + 1e-10
    d1 = abs(ts[min(1, len(ts)-1)] - ts[min(n+1, len(ts)-1)]) + 1e-10
    return float(np.clip(np.log(d1 / d0) / dt, -5, 5))

def safe_mem(ts, mx=50):
    ts = np.array(ts).flatten()
    ts = ts[np.isfinite(ts)]
    if len(ts) < mx * 2: mx = max(len(ts) // 4, 5)
    if mx < 5: return 0.0
    tc = ts - np.mean(ts)
    ac = np.correlate(tc, tc, mode='full')
    ac = ac[len(ac) // 2:]
    ac = ac / (ac[0] + 1e-10)
    for i in range(1, min(mx, len(ac))):
        if ac[i] < 1 / np.e:
            return float(i / mx)
    return 0.0

def safe_corr_dim(ts, emb=3):
    ts = np.array(ts).flatten()
    ts = ts[np.isfinite(ts)]
    if len(ts) < 50: return 1.0
    N = len(ts) - emb
    if N < 10: return 1.0
    emb_arr = np.array([ts[i:i + emb] for i in range(N)])
    idx = np.random.choice(N, min(60, N), replace=False)
    dists = []
    for i in idx:
        for j in idx:
            if i != j:
                d = np.linalg.norm(emb_arr[i] - emb_arr[j])
                if d > 0:
                    dists.append(d)
    if len(dists) < 5: return 1.0
    dists = np.array(dists)
    r = np.logspace(np.log10(np.min(dists)), np.log10(np.max(dists)), 12)
    c = np.array([np.sum(dists < rv) for rv in r])
    v = c > 0
    if np.sum(v) < 3: return 1.0
    coeffs = np.polyfit(np.log(r[v]), np.log(c[v] + 1), 1)
    return float(np.clip(coeffs[0], 0.5, 5.0))

def safe_spatial_ent(field):
    f = np.array(field).flatten()
    f = f[np.isfinite(f)]
    if len(f) < 10: return 0.5
    fn = (f - f.min()) / (f.max() - f.min() + 1e-10)
    h, _ = np.histogram(fn, bins=20, density=True)
    h = h[h > 0]
    return float(np.clip(-np.sum(h * np.log(h + 1e-10)), 0, 10))

new_systems = []

print("1. Lotka-Volterra")
alpha, beta, delta, gamma = 1.0, 0.1, 0.075, 1.5
x, y = 10.0, 5.0
ts_lv = []
for _ in range(20000):
    dx = (alpha * x - beta * x * y) * 0.0005
    dy = (delta * x * y - gamma * y) * 0.0005
    x, y = max(x + dx, 0.001), max(y + dy, 0.001)
    ts_lv.append(x / (x + y))
lv = [safe_lyap(ts_lv[::20], 0.01), safe_corr_dim(ts_lv[::20]), safe_fractal(ts_lv[::20]),
      safe_spatial_ent(np.log(np.array(ts_lv[-200:]) + 0.001)), 0.0,
      safe_mem(ts_lv[::20]), safe_entropy(ts_lv[::20])]
print("  Features:", ["%.3f" % v for v in lv])
new_systems.append(("Lotka-Volterra", "Ecology", lv))

print("2. Neural Growth")
np.random.seed(456)
N_nn = 30
W = np.random.randn(N_nn, N_nn) * 0.1
act = np.random.randn(N_nn)
nn_ts = []
for _ in range(600):
    W += 0.005 * np.outer(act, act)
    W /= (np.linalg.norm(W) / 8 + 1)
    act = np.tanh(W @ act + np.random.randn(N_nn) * 0.1)
    nn_ts.append(np.mean(act ** 2))
nn = [safe_lyap(nn_ts), safe_corr_dim(nn_ts), safe_fractal(nn_ts),
      safe_spatial_ent(W), 0.2, safe_mem(nn_ts), safe_entropy(nn_ts)]
print("  Features:", ["%.3f" % v for v in nn])
new_systems.append(("Neural Growth", "Neural", nn))

print("3. Gene Regulatory")
np.random.seed(789)
N_grn = 20
Wg = np.random.randn(N_grn, N_grn) * 0.3
np.fill_diagonal(Wg, 0)
ge = np.abs(np.random.randn(N_grn))
grn_ts = []
for _ in range(500):
    act_hill = 1.0 / (1.0 + (0.5 / np.maximum(ge, 0.001)) ** 4)
    ge += (5.0 * act_hill - ge) * 0.01
    ge = np.maximum(ge, 0.001)
    grn_ts.append(np.mean(ge))
gr = [safe_lyap(grn_ts), safe_corr_dim(grn_ts), safe_fractal(grn_ts),
      safe_spatial_ent(Wg), 0.15, safe_mem(grn_ts), safe_entropy(grn_ts)]
print("  Features:", ["%.3f" % v for v in gr])
new_systems.append(("Gene Regulatory", "Biochemical", gr))

print("4. SIR Epidemic")
S, I, R = 990.0, 10.0, 0.0
N_pop = 1000.0
sir_ts = []
for _ in range(15000):
    dS = -0.3 * S * I / N_pop * 0.005
    dI = (0.3 * S * I / N_pop - 0.1 * I) * 0.005
    dR = 0.1 * I * 0.005
    S, I, R = max(S + dS, 0.001), max(I + dI, 0.001), R + dR
    sir_ts.append(I / N_pop)
sir = [safe_lyap(sir_ts), safe_corr_dim(sir_ts), safe_fractal(sir_ts),
       0.1, 0.05, safe_mem(sir_ts), safe_entropy(sir_ts)]
print("  Features:", ["%.3f" % v for v in sir])
new_systems.append(("SIR Epidemic", "Epidemiology", sir))

print("5. Physarum")
np.random.seed(321)
Np = 40
trail = np.zeros((Np, Np))
pos = [Np // 2, Np // 2]
dir_a = 0.0
phys_ts = []
for _ in range(3000):
    sensors = []
    for da in [-0.5, 0.0, 0.5]:
        sx = int(pos[0] + 2 * np.cos(dir_a + da)) % Np
        sy = int(pos[1] + 2 * np.sin(dir_a + da)) % Np
        sensors.append(trail[sx, sy])
    best = np.argmax(sensors)
    dir_a += [-0.3, 0.0, 0.3][best]
    pos[0] = (int(pos[0] + np.cos(dir_a)) + Np) % Np
    pos[1] = (int(pos[1] + np.sin(dir_a)) + Np) % Np
    trail[pos[0], pos[1]] += 1
    trail *= 0.995
    phys_ts.append(trail[pos[0], pos[1]])
phys = [safe_lyap(phys_ts), safe_corr_dim(phys_ts), safe_fractal(phys_ts),
        safe_spatial_ent(trail), 0.1, safe_mem(phys_ts), safe_entropy(phys_ts)]
print("  Features:", ["%.3f" % v for v in phys])
new_systems.append(("Physarum", "Biological", phys))

# Add to data
for name, stype, features in new_systems:
    data['names'].append(name)
    data['X'].append(features)
    data['types'].append(stype)
    data['regimes'].append('Biological')

# Recompute
X_all = np.array(data['X'])
n = len(data['names'])
print(f"\nTotal systems: {n}")

# PCA
X_c = X_all - X_all.mean(axis=0)
cov = np.cov(X_c.T)
evals, evecs = np.linalg.eigh(cov)
idx = np.argsort(evals)[::-1]
evals, evecs = evals[idx], evecs[:, idx]
X_pca = X_c @ evecs[:, :2]
data['X_pca'] = X_pca.tolist()
data['eigenvalues'] = evals.tolist()

# Distance
D = np.zeros((n, n))
for i in range(n):
    for j in range(i+1, n):
        d = np.sqrt(((X_all[i] - X_all[j])**2).sum())
        D[i,j] = D[j,i] = d
data['D'] = D.tolist()

# Ideal
ideal = np.array([1.7, 1.8, 1.8, 0.2, 0.5, 2.8, 2.0])
X_norm = (X_all - X_all.min(axis=0)) / (X_all.max(axis=0) - X_all.min(axis=0) + 1e-10)
i_norm = (ideal - X_all.min(axis=0)) / (X_all.max(axis=0) - X_all.min(axis=0) + 1e-10)
nd = np.sqrt(((X_norm - i_norm)**2).sum(axis=1))
nd = nd / nd.max()
data['norm_dist'] = nd.tolist()

# Colors
cmap = plt.cm.tab20
data['colors'] = [cmap(i % 20) for i in range(n)]

with open('morphospace_data.json', 'w') as f:
    json.dump(data, f)

# Plot
fig, ax = plt.subplots(figsize=(10, 8))
for i in range(n):
    c = data['colors'][i]
    ax.scatter(X_pca[i, 0], X_pca[i, 1], c=[c], s=80, edgecolor='black', linewidth=0.5, zorder=5)
    ax.annotate(data['names'][i], (X_pca[i, 0], X_pca[i, 1]), fontsize=5, ha='center', va='bottom')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_title('Expanded Morphospace with Biological Systems')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('morphospace_expanded.png', dpi=150)
print("Saved morphospace_expanded.png")
