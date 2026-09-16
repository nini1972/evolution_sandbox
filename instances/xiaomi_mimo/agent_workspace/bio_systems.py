#!/usr/bin/env python3
"""Add biological substrate types to the morphospace"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

def lyapunov(ts, dt=1.0):
    ts = np.array(ts)
    if len(ts) < 50: return 0.0
    n = len(ts) // 2
    d0 = abs(ts[0] - ts[n]) + 1e-10
    d1 = abs(ts[1] - ts[min(n+1, len(ts)-1)]) + 1e-10
    return np.clip(np.log(d1/d0) / dt, -5, 5)

def fractal_dim(ts):
    ts = np.array(ts)
    if len(ts) < 10: return 1.0
    ts_n = (ts - ts.min()) / (ts.max() - ts.min() + 1e-10)
    scales = np.unique(np.logspace(0, np.log10(len(ts)//4), 10).astype(int))
    scales = scales[scales >= 2]
    counts = []
    for s in scales:
        boxes = set()
        for i in range(0, len(ts_n) - s, s):
            boxes.add((i//s, int(ts_n[i]*s)))
        counts.append(len(boxes))
    if len(counts) < 2: return 1.0
    coeffs = np.polyfit(np.log(scales[:len(counts)]), np.log(np.array(counts)+1), 1)
    return np.clip(coeffs[0], 1.0, 2.0)

def spatial_entropy(field):
    fn = (field - field.min()) / (field.max() - field.min() + 1e-10)
    h, _ = np.histogram(fn.flatten(), bins=20, density=True)
    h = h[h > 0]
    return -np.sum(h * np.log(h + 1e-10))

def sync_order(phases):
    return abs(np.mean(np.exp(1j * np.array(phases))))

def memory_depth(ts, mx=50):
    ts = np.array(ts)
    if len(ts) < mx*2: mx = len(ts)//3
    if mx < 5: return 0.0
    tc = ts - np.mean(ts)
    ac = np.correlate(tc, tc, mode='full')
    ac = ac[len(ac)//2:]
    ac = ac / (ac[0] + 1e-10)
    for i in range(1, min(mx, len(ac))):
        if ac[i] < 1/np.e: return i/mx
    return 0.0

def temporal_entropy(ts, bins=20):
    h, _ = np.histogram(ts, bins=bins, density=True)
    h = h[h > 0]
    return -np.sum(h * np.log(h + 1e-10))

def corr_dim(ts, emb=3):
    ts = np.array(ts)
    if len(ts) < 50: return 1.0
    N = len(ts) - emb
    if N < 10: return 1.0
    emb_arr = np.array([ts[i:i+emb] for i in range(N)])
    idx = np.random.choice(N, min(50, N), replace=False)
    dists = []
    for i in idx:
        for j in idx:
            if i != j:
                d = np.linalg.norm(emb_arr[i] - emb_arr[j])
                if d > 0: dists.append(d)
    if len(dists) < 5: return 1.0
    dists = np.array(dists)
    r = np.logspace(np.log10(np.min(dists)), np.log10(np.max(dists)), 15)
    c = np.array([np.sum(dists < rv) for rv in r])
    v = c > 0
    if np.sum(v) < 3: return 1.0
    coeffs = np.polyfit(np.log(r[v]), np.log(c[v]+1), 1)
    return np.clip(coeffs[0], 0.5, 5.0)

print("ADDING BIOLOGICAL SYSTEMS")

new_systems = []

# 1. Lotka-Volterra
print("1. Lotka-Volterra")
a, b, d, g = 1.0, 0.1, 0.075, 1.5
x, y = 10.0, 5.0
ts, lx, ly = [], [], []
for _ in range(100000):
    dx = (a*x - b*x*y)*0.001
    dy = (d*x*y - g*y)*0.001
    x, y = max(x+dx, 0.001), max(y+dy, 0.001)
    lx.append(x); ly.append(y); ts.append(x/(x+y))
lv = [lyapunov(ts[::100], 0.1), corr_dim(ts[::100]), fractal_dim(ts[::100]),
      spatial_entropy(np.outer(lx[-100:], ly[-100:])), 0.0,
      memory_depth(ts[::100]), temporal_entropy(ts[::100])]
print(f"  Features: {[round(v,3) for v in lv]}")
new_systems.append({'name':'Lotka-Volterra','type':'Ecology','features':lv})

# 2. Neural Growth
print("2. Neural Growth")
np.random.seed(456)
N = 30
W = np.random.randn(N,N)*0.1
act = np.random.randn(N)
nts = []
for _ in range(500):
    W += 0.01*np.outer(act, act)
    W /= (np.linalg.norm(W)/10+1)
    act = np.tanh(W@act + np.random.randn(N)*0.1)
    nts.append(np.mean(act**2))
nn = [lyapunov(nts), corr_dim(nts), fractal_dim(nts),
      spatial_entropy(W), 0.2, memory_depth(nts), temporal_entropy(nts)]
print(f"  Features: {[round(v,3) for v in nn]}")
new_systems.append({'name':'Neural Growth','type':'Neural','features':nn})

# 3. Gene Regulatory
print("3. Gene Regulatory")
np.random.seed(789)
N = 20
Wg = np.random.randn(N,N)*0.3
np.fill_diagonal(Wg, 0)
ge = np.abs(np.random.randn(N))
gts = []
for _ in range(500):
    act = 1/(1+(0.5/np.maximum(ge,0.001))**4)
    ge += (5*act - ge)*0.01
    ge = np.maximum(ge, 0.001)
    gts.append(np.mean(ge))
gr = [lyapunov(gts), corr_dim(gts), fractal_dim(gts),
      spatial_entropy(Wg), 0.15, memory_depth(gts), temporal_entropy(gts)]
print(f"  Features: {[round(v,3) for v in gr]}")
new_systems.append({'name':'Gene Regulatory','type':'Biochemical','features':gr})

# 4. SIR Epidemic
print("4. SIR Epidemic")
S, I, R = 990.0, 10.0, 0.0
Np = 1000.0
sir_ts = []
for _ in range(10000):
    dS = -0.3*S*I/Np*0.01
    dI = (0.3*S*I/Np - 0.1*I)*0.01
    dR = 0.1*I*0.01
    S += dS; I += dI; R += dR
    sir_ts.append(I/Np)
sir = [lyapunov(sir_ts), corr_dim(sir_ts), fractal_dim(sir_ts),
       0.1, 0.05, memory_depth(sir_ts), temporal_entropy(sir_ts)]
print(f"  Features: {[round(v,3) for v in sir]}")
new_systems.append({'name':'SIR Epidemic','type':'Epidemiology','features':sir})

# 5. Physarum (slime mold)
print("5. Physarum Slug")
np.random.seed(321)
N = 40
trail = np.zeros((N, N))
pos = [N//2, N//2]
dir_angle = 0.0
ps = []
for _ in range(2000):
    # Sense
    sensors = []
    for da in [-0.5, 0, 0.5]:
        sx = int(pos[0] + 2*np.cos(dir_angle+da))
        sy = int(pos[1] + 2*np.sin(dir_angle+da))
        sx, sy = sx%N, sy%N
        sensors.append(trail[sx, sy])
    # Move toward highest
    best = np.argmax(sensors)
    dir_angle += [-0.3, 0, 0.3][best]
    pos[0] = int(pos[0] + np.cos(dir_angle))
    pos[1] = int(pos[1] + np.sin(dir_angle))
    pos[0], pos[1] = pos[0]%N, pos[1]%N
    trail[pos[0], pos[1]] += 1
    # Diffuse
    trail *= 0.99
    ps.append(trail[pos[0], pos[1]])
ps = np.array(ps)
phys = [lyapunov(ps), corr_dim(ps), fractal_dim(ps),
        spatial_entropy(trail), 0.1, memory_depth(ps), temporal_entropy(ps)]
print(f"  Features: {[round(v,3) for v in phys]}")
new_systems.append({'name':'Physarum','type':'Biological','features':phys})

# Add to existing data
for ns in new_systems:
    data['names'].append(ns['name'])
    data['X'].append(ns['features'])
    data['types'].append(ns['type'])
    data['regimes'].append('Biological')

# Recompute PCA/MDS/distance from scratch
X_all = np.array(data['X'])
n = len(data['names'])

# PCA
X_centered = X_all - X_all.mean(axis=0)
cov = np.cov(X_centered.T)
eigenvalues, eigenvectors = np.linalg.eigh(cov)
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]
X_pca = X_centered @ eigenvectors[:, :2]
data['X_pca'] = X_pca.tolist()
data['eigenvalues'] = eigenvalues.tolist()
data['eigenvectors'] = eigenvectors.tolist()

# MDS from Euclidean distance
D = np.zeros((n, n))
for i in range(n):
    for j in range(i+1, n):
        d = np.sqrt(((X_all[i] - X_all[j])**2).sum())
        D[i,j] = D[j,i] = d
data['D'] = D.tolist()

# Simple MDS
n = len(X_all)
H = np.eye(n) - np.ones((n,n))/n
B = -0.5 * H @ (D**2) @ H
evals, evecs = np.linalg.eigh(B)
ei = np.argsort(evals)[::-1]
X_mds = evecs[:, ei[:2]] * np.sqrt(np.maximum(evals[ei[:2]], 0))
data['X_mds'] = X_mds.tolist()

# Colors and distances
ideal = np.array([1.7, 1.8, 1.8, 0.2, 0.5, 2.8, 2.0])
ideal_norm = (ideal - X_all.min(axis=0)) / (X_all.max(axis=0) - X_all.min(axis=0) + 1e-10)
X_norm = (X_all - X_all.min(axis=0)) / (X_all.max(axis=0) - X_all.min(axis=0) + 1e-10)
nd = np.sqrt(((X_norm - ideal_norm)**2).sum(axis=1))
nd = nd / nd.max()
data['norm_dist'] = nd.tolist()

# Generate colors
cmap = plt.cm.get_cmap('tab20', n)
data['colors'] = [cmap(i) for i in range(n)]

with open('morphospace_data.json', 'w') as f:
    json.dump(data, f)

print(f"\nAdded {len(new_systems)} biological systems. Total: {n}")
print("Updated morphospace_data.json")

# Quick plot
fig, ax = plt.subplots(figsize=(10, 8))
for i in range(n):
    ax.scatter(X_pca[i, 0], X_pca[i, 1], c=[data['colors'][i]], s=80,
               edgecolor='black', linewidth=0.5, zorder=5)
    ax.annotate(data['names'][i], (X_pca[i, 0], X_pca[i, 1]),
                fontsize=5, ha='center', va='bottom')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_title('Morphospace with Biological Systems Added')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('morphospace_with_bio.png', dpi=150)
print("Saved morphospace_with_bio.png")
