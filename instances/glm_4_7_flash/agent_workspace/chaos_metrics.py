"""
Discovery #008: Quantitative Chaos Metrics (optimized)
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

dt = 0.01

# ---- Lorenz Lyapunov ----
def lorenz_derivs(state, sigma=10, rho=28, beta=8/3):
    x, y, z = state
    return np.array([sigma*(y-x), x*(rho-z)-y, x*y-beta*z])

def lorenz_lyap(steps=5000, warmup=2000):
    state = np.array([1.0, 1.0, 1.0])
    for _ in range(warmup):
        k1 = lorenz_derivs(state)
        k2 = lorenz_derivs(state + 0.5*dt*k1)
        k3 = lorenz_derivs(state + 0.5*dt*k2)
        k4 = lorenz_derivs(state + dt*k3)
        state = state + dt/6*(k1 + 2*k2 + 2*k3 + k4)

    tangent = np.array([1.0, 0.0, 0.0])
    lyap_sum = 0.0
    vals = []
    for i in range(steps):
        k1 = lorenz_derivs(state)
        k2 = lorenz_derivs(state + 0.5*dt*k1)
        k3 = lorenz_derivs(state + 0.5*dt*k2)
        k4 = lorenz_derivs(state + dt*k3)
        state = state + dt/6*(k1 + 2*k2 + 2*k3 + k4)

        x, y, z = state
        J = np.array([
            [-10.0, 10.0, 0.0],
            [28.0 - z, -1.0, -x],
            [y, x, -8.0/3.0]
        ])
        tangent = tangent + dt * (J @ tangent)
        norm = np.linalg.norm(tangent)
        if norm > 0:
            lyap_sum += np.log(norm)
            tangent = tangent / norm
        vals.append(lyap_sum / ((i + 1) * dt))
    return vals[-1], vals

# ---- Henon Lyapunov ----
def henon_lyap(a=1.4, b=0.3, steps=20000, warmup=1000):
    x, y = 0.1, 0.0
    for _ in range(warmup):
        x, y = 1 - a*x*x + y, b*x

    tx, ty = 1.0, 0.0
    n = np.sqrt(tx*tx + ty*ty)
    tx, ty = tx/n, ty/n
    s = 0.0
    vals = []
    for i in range(steps):
        j11 = -2*a*x
        ntx = j11*tx + ty
        nty = b*tx
        norm = np.sqrt(ntx*ntx + nty*nty)
        if norm > 0:
            s += np.log(norm)
            tx = ntx / norm
            ty = nty / norm
        vals.append(s / (i + 1))
        x, y = 1 - a*x*x + y, b*x
    return vals[-1], vals

# ---- Rossler Lyapunov ----
def rossler_derivs(state, a=0.2, b=0.2, c=5.7):
    x, y, z = state
    return np.array([-y - z, x + a*y, b + z*(x - c)])

def rossler_lyap(steps=5000, warmup=2000):
    state = np.array([1.0, 0.0, 0.0])
    for _ in range(warmup):
        k1 = rossler_derivs(state)
        k2 = rossler_derivs(state + 0.5*dt*k1)
        k3 = rossler_derivs(state + 0.5*dt*k2)
        k4 = rossler_derivs(state + dt*k3)
        state = state + dt/6*(k1 + 2*k2 + 2*k3 + k4)

    tangent = np.array([1.0, 0.0, 0.0])
    lyap_sum = 0.0
    vals = []
    for i in range(steps):
        k1 = rossler_derivs(state)
        k2 = rossler_derivs(state + 0.5*dt*k1)
        k3 = rossler_derivs(state + 0.5*dt*k2)
        k4 = rossler_derivs(state + dt*k3)
        state = state + dt/6*(k1 + 2*k2 + 2*k3 + k4)

        x, y, z = state
        J = np.array([
            [0.0, -1.0, -1.0],
            [1.0, 0.2, 0.0],
            [0.0, 0.0, x - 5.7]
        ])
        tangent = tangent + dt * (J @ tangent)
        norm = np.linalg.norm(tangent)
        if norm > 0:
            lyap_sum += np.log(norm)
            tangent = tangent / norm
        vals.append(lyap_sum / ((i + 1) * dt))
    return vals[-1], vals

# ---- Correlation dimension ----
def corr_dim(data, max_pts=2000):
    N = min(len(data), max_pts)
    if len(data) > max_pts:
        idx = np.random.choice(len(data), max_pts, replace=False)
        pts = data[idx]
    else:
        pts = data[:N]
    N = len(pts)

    diff = pts[:, None, :] - pts[None, :, :]
    dists = np.sqrt(np.sum(diff**2, axis=2))
    dists = dists[np.triu_indices(N, k=1)]

    r_min = np.percentile(dists, 2)
    r_max = np.percentile(dists, 85)
    rs = np.logspace(np.log10(r_min), np.log10(r_max), 40)
    C_r = np.array([np.mean(dists <= r) for r in rs])

    mask = (C_r > 0) & (C_r < 1)
    lr = np.log(rs[mask])
    lc = np.log(C_r[mask])
    n = len(lr)
    if n > 6:
        a = n // 4
        b = 3 * n // 4
        slope = np.polyfit(lr[a:b], lc[a:b], 1)[0]
    else:
        slope = np.polyfit(lr, lc, 1)[0]
    return slope, lr, lc

# ===== RUN =====
print("Computing Lorenz Lyapunov...")
lam_l, hist_l = lorenz_lyap()
print(f"  lambda_max = {lam_l:.4f}")

print("Computing Henon Lyapunov...")
lam_h, hist_h = henon_lyap()
print(f"  lambda_max = {lam_h:.4f}")

print("Computing Rossler Lyapunov...")
lam_r, hist_r = rossler_lyap()
print(f"  lambda_max = {lam_r:.4f}")

print("Generating trajectories for correlation dimension...")
state = np.array([1.0, 1.0, 1.0])
lpts = []
for _ in range(8000):
    k1 = lorenz_derivs(state)
    k2 = lorenz_derivs(state + 0.5*dt*k1)
    k3 = lorenz_derivs(state + 0.5*dt*k2)
    k4 = lorenz_derivs(state + dt*k3)
    state = state + dt/6*(k1 + 2*k2 + 2*k3 + k4)
    lpts.append(state.copy())
lpts = np.array(lpts[2000:])

x, y = 0.1, 0.0
hpts = []
for _ in range(10000):
    x, y = 1 - 1.4*x*x + y, 0.3*x
    hpts.append([x, y])
hpts = np.array(hpts[500:])

state = np.array([1.0, 0.0, 0.0])
rpts = []
for _ in range(8000):
    k1 = rossler_derivs(state)
    k2 = rossler_derivs(state + 0.5*dt*k1)
    k3 = rossler_derivs(state + 0.5*dt*k2)
    k4 = rossler_derivs(state + dt*k3)
    state = state + dt/6*(k1 + 2*k2 + 2*k3 + k4)
    rpts.append(state.copy())
rpts = np.array(rpts[2000:])

print("Computing correlation dimensions...")
cd_l, lr_l, lc_l = corr_dim(lpts)
print(f"  D2 (Lorenz) = {cd_l:.4f}")
cd_h, lr_h, lc_h = corr_dim(hpts)
print(f"  D2 (Henon) = {cd_h:.4f}")
cd_r, lr_r2, lc_r2 = corr_dim(rpts)
print(f"  D2 (Rossler) = {cd_r:.4f}")

results = {
    "lorenz": {"lyapunov_max": lam_l, "correlation_dim": cd_l},
    "henon": {"lyapunov_max": lam_h, "correlation_dim": cd_h},
    "rossler": {"lyapunov_max": lam_r, "correlation_dim": cd_r}
}
with open('chaos_metrics.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*50)
print(f"{'System':<15} {'Lyapunov':>12} {'Corr. Dim':>12}")
print("-"*40)
for name, m in results.items():
    print(f"{name:<15} {m['lyapunov_max']:>12.4f} {m['correlation_dim']:>12.4f}")

# ===== PLOT =====
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.patch.set_facecolor('#0a0a1a')

for ax, hist, name, color in [
    (axes[0,0], hist_l, 'Lorenz', 'cyan'),
    (axes[0,1], hist_h, 'Henon', 'gold'),
    (axes[0,2], hist_r, 'Rossler', 'magenta')
]:
    ax.set_facecolor('#0a0a1a')
    ax.plot(hist, linewidth=0.5, color=color, alpha=0.8)
    ax.set_title(f'{name} Lyapunov Convergence', color='white', fontsize=12)
    ax.set_xlabel('Step', color='gray')
    ax.set_ylabel('lambda_max', color='gray')
    ax.tick_params(colors='gray')

for ax, lr, lc, name, color, cd_val in [
    (axes[1,0], lr_l, lc_l, 'Lorenz', 'cyan', cd_l),
    (axes[1,1], lr_h, lc_h, 'Henon', 'gold', cd_h),
    (axes[1,2], lr_r2, lc_r2, 'Rossler', 'magenta', cd_r)
]:
    ax.set_facecolor('#0a0a1a')
    ax.scatter(lr, lc, s=3, c=color, alpha=0.6)
    ax.set_title(f'{name} Corr. Dim (D2={cd_val:.3f})', color='white', fontsize=12)
    ax.set_xlabel('log(r)', color='gray')
    ax.set_ylabel('log(C(r))', color='gray')
    ax.tick_params(colors='gray')

fig.suptitle('Quantitative Chaos Metrics: Lyapunov Exponents & Correlation Dimensions',
             fontsize=16, color='white', fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('chaos_metrics.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("\nSaved chaos_metrics.png and chaos_metrics.json")
