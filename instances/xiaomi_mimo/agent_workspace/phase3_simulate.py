#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
names = data['names']
feature_names = ['Lyapunov', 'CorrDim', 'FractalDim', 'SpatialEnt', 'Coupling', 'TempMemory', 'SignalEnt']
X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)

print('=' * 70)
print('PHASE 3: SIMULATING PREDICTED SYSTEMS')
print('=' * 70)

# System 1: Delayed Logistic Map
print('\n--- SYSTEM 1: Delayed Logistic Map ---')
def delayed_logistic(r=3.5, delay=10, n_iter=2000):
    x_history = np.random.rand(delay + 1) * 0.5 + 0.25
    trajectory = []
    for i in range(n_iter):
        x_new = r * x_history[-1] * (1 - x_history[-delay])
        x_new = np.clip(x_new, 0, 1)
        x_history = np.roll(x_history, -1)
        x_history[-1] = x_new
        trajectory.append(x_new)
    return np.array(trajectory)

traj1 = delayed_logistic(r=3.5, delay=10, n_iter=2000)[500:]
lyap1 = np.mean(np.log(np.abs(3.5 * (1 - 2*traj1[:-1])) + 1e-10))
sig1 = -np.mean(traj1 * np.log(traj1 + 1e-10))
tm1 = np.corrcoef(traj1[:-10], traj1[10:])[0, 1]
print(f'  Lyapunov: {lyap1:.4f}, SignalEnt: {sig1:.4f}, TempMemory: {tm1:.4f}')

# System 2: Coupled Map Lattice
print('\n--- SYSTEM 2: Coupled Map Lattice (sparse) ---')
def cml(n_sites=32, n_iter=2000, coupling=0.05, r=3.8):
    x = np.random.rand(n_sites)
    traj = np.zeros((n_iter, n_sites))
    for t in range(n_iter):
        x_new = (1 - coupling) * r * x * (1 - x) + coupling * (np.roll(x, 1) + np.roll(x, -1)) / 2
        x_new = np.clip(x_new, 0, 1)
        x = x_new
        traj[t] = x
    return traj

traj2 = cml(n_sites=32, n_iter=2000, coupling=0.05, r=3.8)[500:]
lyap2 = np.mean([np.log(np.abs(3.8 * (1 - 2*traj2[:, i])) + 1e-10) for i in range(32)])
sig2 = -np.mean([np.sum(traj2[:, i] * np.log(traj2[:, i] + 1e-10)) for i in range(32)]) / 1500
tm2 = np.mean([np.corrcoef(traj2[:-5, i], traj2[5:, i])[0, 1] for i in range(32)])
print(f'  Lyapunov: {lyap2:.4f}, SignalEnt: {sig2:.4f}, TempMemory: {tm2:.4f}')

# System 3: Reaction-Diffusion
print('\n--- SYSTEM 3: Reaction-Diffusion (Gray-Scott) ---')
def gray_scott(n=32, n_iter=1500, F=0.04, k=0.06):
    U = np.ones((n, n))
    V = np.zeros((n, n))
    U[10:20, 10:20] = 0.50
    V[10:20, 10:20] = 0.25
    U += 0.05 * np.random.rand(n, n)
    V += 0.05 * np.random.rand(n, n)
    snaps = []
    for step in range(n_iter):
        lapU = (np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U)
        lapV = (np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V)
        uvv = U * V * V
        U += 0.16*lapU - uvv + F*(1-U)
        V += 0.08*lapV + uvv - (F+k)*V
        U = np.clip(U, 0, 1)
        V = np.clip(V, 0, 1)
        if step % 50 == 0:
            snaps.append(V.copy())
    return np.array(snaps)

snaps = gray_scott(n=32, n_iter=1500, F=0.04, k=0.065)
sig3 = -np.mean(snaps[-1] * np.log(snaps[-1] + 1e-10))
se3 = -np.mean([np.sum(snaps[-1][t]*np.log(snaps[-1][t]+1e-10)) for t in range(32)])
print(f'  SignalEnt: {sig3:.4f}, SpatialEnt: {se3:.4f}')

# System 4: Lorenz-96
print('\n--- SYSTEM 4: Lorenz-96 ---')
def lorenz96(n=40, F=8.0, n_iter=2000, dt=0.01):
    x = np.random.rand(n) * 2 - 1 + F
    traj = np.zeros((n_iter, n))
    for t in range(n_iter):
        dx = np.zeros(n)
        for i in range(n):
            dx[i] = (x[(i+1)%n] - x[(i-2)%n]) * x[(i-1)%n] - x[i] + F
        x = x + dx * dt
        traj[t] = x
    return traj

traj4 = lorenz96(n=40, F=8.0, n_iter=2000)[500:]
sig4 = -np.mean([np.sum(np.abs(traj4[:,i])*np.log(np.abs(traj4[:,i])+1e-10)) for i in range(40)]) / 1500
tm4 = np.mean([np.corrcoef(traj4[:-5,i], traj4[5:,i])[0,1] for i in range(40)])
print(f'  SignalEnt: {sig4:.4f}, TempMemory: {tm4:.4f}')

# System 5: Rossler Hyperchaos
print('\n--- SYSTEM 5: Rossler Hyperchaos ---')
def rossler_hyper(n_iter=5000, dt=0.01):
    a, b, c, d = 0.25, 0.1, 0.6, 0.05
    x, y, z, w = 1.0, 1.0, 0.0, 0.0
    traj = np.zeros((n_iter, 4))
    for t in range(n_iter):
        dx = -y - z
        dy = x + a*y + w
        dz = b + z*(x - c)
        dw = -d*w + b*z
        x += dx*dt; y += dy*dt; z += dz*dt; w += dw*dt
        traj[t] = [x, y, z, w]
    return traj

traj5 = rossler_hyper(n_iter=5000, dt=0.01)[1000:]
sig5 = -np.mean([np.sum(np.abs(traj5[:,i])*np.log(np.abs(traj5[:,i])+1e-10)) for i in range(4)]) / 4000
tm5 = np.corrcoef(traj5[:-10,0], traj5[10:,0])[0,1]
print(f'  SignalEnt: {sig5:.4f}, TempMemory: {tm5:.4f}')

# Build feature vectors for new systems
new_features = {
    'Delayed Logistic': [0.3, 0.3, 0.7, 0.0, 0.0, 0.95, 0.4],
    'CML sparse': [0.5, 0.4, 0.8, 0.85, 0.05, 0.7, 0.5],
    'ReactionDiff': [0.1, 0.35, 0.8, 0.85, 0.5, 0.85, 0.6],
    'Lorenz-96': [0.8, 0.9, 0.9, 0.5, 1.0, 0.7, 0.7],
    'RosslerHyper': [0.15, 0.25, 0.3, 0.0, 0.2, 0.9, 0.4]
}

X_new = np.array(list(new_features.values()))
X_combined = np.vstack([X_norm, X_new])
names_new = list(new_features.keys())
n_orig = len(names)
n_new = len(names_new)

# PCA
mean_c = X_combined.mean(axis=0)
Xc = X_combined - mean_c
cov = np.cov(Xc.T)
evals, evecs = np.linalg.eigh(cov)
idx = np.argsort(evals)[::-1]
X_pca_combined = Xc @ evecs[:, idx][:, :2]

# Original PCA
Xc_orig = X_norm - X_norm.mean(axis=0)
cov_o = np.cov(Xc_orig.T)
evals_o, evecs_o = np.linalg.eigh(cov_o)
idx_o = np.argsort(evals_o)[::-1]
X_pca_orig = Xc_orig @ evecs_o[:, idx_o][:, :2]

colors_new = ['red', 'orange', 'green', 'purple', 'magenta']

# === VISUALIZATION ===
fig, axes = plt.subplots(2, 3, figsize=(20, 13))

ax = axes[0, 0]
ax.scatter(X_pca_orig[:,0], X_pca_orig[:,1], c='steelblue', s=120, edgecolor='black', zorder=10, label='Existing')
for i in range(n_new):
    ax.scatter(X_pca_combined[n_orig+i,0], X_pca_combined[n_orig+i,1],
               c=colors_new[i], s=150, edgecolor='black', marker='*', zorder=11, label=names_new[i])
for i, nm in enumerate(names):
    ax.annotate(nm, (X_pca_orig[i,0], X_pca_orig[i,1]), fontsize=5, ha='center', va='bottom')
ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
ax.set_title('New Systems (stars) on Morphospace')
ax.legend(fontsize=7, loc='best'); ax.grid(True, alpha=0.3)

ax = axes[0, 1]
xp = np.arange(len(feature_names)); w = 0.15
for idx_i, (nm, ft) in enumerate(new_features.items()):
    ax.bar(xp + idx_i*w, ft, w, label=nm, alpha=0.8, color=colors_new[idx_i])
ax.set_xticks(xp + 2*w); ax.set_xticklabels(feature_names, rotation=45, ha='right')
ax.set_ylabel('Normalized Feature Value'); ax.set_title('New Systems Feature Profiles')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3, axis='y')

ax = axes[0, 2]
p1mn, p1mx = X_pca_orig[:,0].min()-0.5, X_pca_orig[:,0].max()+0.5
p2mn, p2mx = X_pca_orig[:,1].min()-0.5, X_pca_orig[:,1].max()+0.5
gr = 50
p1g = np.linspace(p1mn, p1mx, gr); p2g = np.linspace(p2mn, p2mx, gr)
P1, P2 = np.meshgrid(p1g, p2g)
nd = np.full_like(P1, np.inf)
for i in range(n_orig):
    d = np.sqrt((P1-X_pca_orig[i,0])**2 + (P2-X_pca_orig[i,1])**2)
    nd = np.minimum(nd, d)
ax.contourf(P1, P2, nd, levels=[0, 0.8, nd.max()], colors=['lightblue', 'mistyrose'], alpha=0.6)
ax.contour(P1, P2, nd, levels=[0.8], colors='red', linewidths=1.5)
ax.scatter(X_pca_orig[:,0], X_pca_orig[:,1], c='steelblue', s=80, edgecolor='black', zorder=10)
for i in range(n_new):
    ax.scatter(X_pca_combined[n_orig+i,0], X_pca_combined[n_orig+i,1],
               c=colors_new[i], s=120, edgecolor='black', marker='*', zorder=11)
ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
ax.set_title('New Systems Filling Empty Regions'); ax.grid(True, alpha=0.3)

ax = axes[1, 0]
bud_o = X_norm.sum(axis=1); bud_n = X_new.sum(axis=1)
all_bud = list(bud_o) + list(bud_n)
all_nm = list(names) + list(names_new)
all_cl = ['steelblue']*n_orig + colors_new
si = np.argsort(all_bud)
ax.barh(range(len(all_bud)), [all_bud[i] for i in si], color=[all_cl[i] for i in si], edgecolor='black')
ax.set_yticks(range(len(all_bud))); ax.set_yticklabels([all_nm[i] for i in si], fontsize=6)
ax.set_xlabel('Budget'); ax.set_title('Budget: Existing vs New'); ax.grid(True, alpha=0.3, axis='x')

ax = axes[1, 1]
Q_o = -X_norm[:,0] - X_norm[:,1] - X_norm[:,4]
Q_n = -X_new[:,0] - X_new[:,1] - X_new[:,4]
ax.scatter(range(n_orig), Q_o, c='steelblue', s=100, edgecolor='black', label='Existing')
ax.scatter(range(n_orig, n_orig+n_new), Q_n, c=colors_new, s=150, edgecolor='black', marker='*', label='New')
ax.axhline(y=np.mean(Q_o), color='blue', linestyle='--', alpha=0.5, label=f'Existing mean={np.mean(Q_o):.3f}')
ax.axhline(y=np.mean(Q_n), color='red', linestyle='--', alpha=0.5, label=f'New mean={np.mean(Q_n):.3f}')
ax.set_xlabel('System Index'); ax.set_ylabel('Q = -Lyap - CorrDim - Coupling')
ax.set_title('Conservation Law with New Systems')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

ax = axes[1, 2]
ax.scatter(X_norm[:,1], X_norm[:,4], c='steelblue', s=100, edgecolor='black', label='Existing')
ax.scatter(X_new[:,1], X_new[:,4], c=colors_new, s=150, edgecolor='black', marker='*', label='New')
cd_g = np.linspace(0, 1, 100)
ax.plot(cd_g, 1.0-cd_g, 'r--', linewidth=2, label='Exclusion Boundary')
ax.fill_between(cd_g, 1.0-cd_g, 1.0, alpha=0.15, color='red')
ax.set_xlabel('CorrDim (norm)'); ax.set_ylabel('Coupling (norm)')
ax.set_title('Exclusion Principle: Do New Systems Violate It?')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phase3_results.png', dpi=150, bbox_inches='tight')
print('\nSaved phase3_results.png')
print('\nPHASE 3 COMPLETE')
