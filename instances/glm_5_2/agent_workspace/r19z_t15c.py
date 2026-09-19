# R19Z Turn 15c: Larger grid GS - reduced T for speed
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

k_gs = 0.062
Du, Dv = 0.16, 0.08

def lap(a):
    return np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1)-4*a

def gs_step(u, v, f, k, dt=1.0):
    uvv = u*v*v
    u2 = u + dt*(Du*lap(u) - uvv + f*(1.0-u))
    v2 = v + dt*(Dv*lap(v) + uvv - (f+k)*v)
    return np.clip(u2,0,1), np.clip(v2,0,1)

# Quick grid size test
print("=== Grid size effect (short run) ===")
f_test = 0.060
for sz in [12, 24, 48]:
    np.random.seed(42)
    u = np.ones((sz, sz)); v = np.zeros((sz, sz))
    c = sz // 2; r = max(2, sz // 6)
    u[c-r:c+r, c-r:c+r] = 0.5
    v[c-r:c+r, c-r:c+r] = 0.25
    v += np.random.rand(sz, sz) * 0.01
    T = 1000; burn = 200
    var_v = []
    for t in range(burn + T):
        u, v = gs_step(u, v, f_test, k_gs)
        if t >= burn:
            var_v.append(float(np.var(v)))
    var_v = np.array(var_v)
    print(f"  sz={sz}: mean={np.mean(var_v):.6f}, std={np.std(var_v):.6f}, "
          f"max_v={np.max(v):.4f}, min_v={np.min(v):.4f}")

# f scan with sz=24 (manageable)
print("\n=== f scan with sz=24 ===")
sz = 24
f_vals = np.linspace(0.030, 0.090, 25)
results = {'f': [], 'mean_var': [], 'std_var': [], 'max_v': []}

for f in f_vals:
    np.random.seed(42)
    u = np.ones((sz, sz)); v = np.zeros((sz, sz))
    c = sz // 2; r = sz // 6
    u[c-r:c+r, c-r:c+r] = 0.5
    v[c-r:c+r, c-r:c+r] = 0.25
    v += np.random.rand(sz, sz) * 0.01
    T = 1000; burn = 200
    var_v = []
    for t in range(burn + T):
        u, v = gs_step(u, v, f, k_gs)
        if t >= burn:
            var_v.append(float(np.var(v)))
    var_v = np.array(var_v)
    results['f'].append(float(f))
    results['mean_var'].append(float(np.mean(var_v)))
    results['std_var'].append(float(np.std(var_v)))
    results['max_v'].append(float(np.max(v)))
    print(f"  f={f:.4f}: mean_var={np.mean(var_v):.6f}, std_var={np.std(var_v):.6f}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
ax.plot(results['f'], results['mean_var'], 'bo-', ms=4)
ax.set_xlabel('f'); ax.set_ylabel('mean Var(v)'); ax.set_title('Mean Var(v) vs f')
ax = axes[1]
ax.plot(results['f'], results['std_var'], 'ro-', ms=4)
ax.set_xlabel('f'); ax.set_ylabel('std Var(v)'); ax.set_title('Temporal Variability of Var(v)')

fig.suptitle(f'R19Z Turn 15c: GS Pattern Formation (sz={sz}, k=0.062)', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_t15c_grid.png', dpi=150, bbox_inches='tight')

with open('r19z_t15c_data.json', 'w') as fout:
    json.dump(results, fout, indent=2)
print('\nSaved r19z_t15c_grid.png and r19z_t15c_data.json')