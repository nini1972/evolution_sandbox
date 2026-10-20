"""
Cross-System Universality of Q-Phase Classifier at Chaotic Onset
=================================================================
EMP-149 showed Q = -λ_max - D_2 - K classifies phases on the Hénon map,
with Q ≈ -2.08 at chaotic onset. Is this universal across systems?

We test: Hénon (baseline), Logistic, Lorenz, Rössler, Duffing
For each: find onset of chaos, compute Q, compare.
"""

import numpy as np
import json
import os

np.random.seed(42)

# ============================================================
# 1. Lyapunov exponent computation (varies by system)
# ============================================================

def lyapunov_logistic(r, n_steps=50000, n_discard=5000):
    """Maximal Lyapunov exponent for logistic map x_{n+1} = r*x_n*(1-x_n)."""
    x = 0.5
    for _ in range(n_discard):
        x = r * x * (1 - x)
    lyap = 0.0
    for _ in range(n_steps):
        x = r * x * (1 - x)
        df = abs(r * (1 - 2*x))
        if df > 0:
            lyap += np.log(df)
        else:
            lyap += -20  # cap log to avoid -inf
    return lyap / n_steps

def lyapunov_henon(a, b=0.3, n_steps=50000, n_discard=5000):
    """Maximal Lyapunov exponent for Hénon map."""
    x, y = 0.1, 0.1
    for _ in range(n_discard):
        x, y = 1 - a*x**2 + y, b*x
    # Jacobian: [[-2*a*x, 1], [b, 0]]
    J = np.eye(2)
    lyap = 0.0
    for _ in range(n_steps):
        x, y = 1 - a*x**2 + y, b*x
        JM = np.array([[-2*a*x, 1], [b, 0]])
        J = JM @ J
        # QR decomposition for stability
        Q, R = np.linalg.qr(J)
        lyap += np.log(abs(R[0,0]) + 1e-30)
        J = Q
    return lyap / n_steps

def lyapunov_ode(flow_fn, jac_fn, x0, dt=0.01, n_steps=50000, n_discard=5000):
    """Maximal Lyapunov exponent for ODE via RK4 + variational equations."""
    dim = len(x0)
    x = np.array(x0, dtype=float)
    # Discard transient
    for _ in range(n_discard):
        k1 = flow_fn(x)
        k2 = flow_fn(x + 0.5*dt*k1)
        k3 = flow_fn(x + 0.5*dt*k2)
        k4 = flow_fn(x + dt*k3)
        x = x + dt/6*(k1 + 2*k2 + 2*k3 + k4)
    
    # Benettin's method
    J = np.eye(dim)
    lyap = 0.0
    for _ in range(n_steps):
        k1 = flow_fn(x)
        k2 = flow_fn(x + 0.5*dt*k1)
        k3 = flow_fn(x + 0.5*dt*k2)
        k4 = flow_fn(x + dt*k3)
        x = x + dt/6*(k1 + 2*k2 + 2*k3 + k4)
        
        # Update variational equation
        JM = jac_fn(x)
        J = J + dt * (JM @ J)
        
        # Re-orthonormalize
        Q_mat, R_mat = np.linalg.qr(J)
        lyap += np.log(abs(R_mat[0,0]) + 1e-30)
        J = Q_mat
    
    return lyap / (n_steps * dt)

# ============================================================
# 2. Grassberger-Procaccia correlation dimension D_2
# ============================================================

def correlation_dimension(series, max_emb_dim=10, n_points=2000, n_pairs=50000):
    """Estimate D_2 from time series via delay embedding + GP algorithm."""
    series = np.array(series)
    if len(series) < n_points * 2:
        n_points = len(series) // 2
    
    # Use embedding dimension = min(max_emb_dim, len(series)//4)
    emb_dim = min(max_emb_dim, len(series) // 10)
    emb_dim = max(emb_dim, 3)
    lag = 1
    
    # Create delay vectors
    n_vec = len(series) - (emb_dim - 1) * lag
    if n_vec < 100:
        return 0.0
    
    vectors = np.zeros((n_vec, emb_dim))
    for i in range(emb_dim):
        vectors[:, i] = series[i*lag : i*lag + n_vec]
    
    # Sample pairs for distances
    idx = np.random.choice(n_vec, min(n_pairs*2, n_vec), replace=False)
    sub = vectors[idx[:n_points]]
    
    # Compute pairwise distances
    dists = []
    for i in range(min(len(sub), 300)):
        d = np.sqrt(np.sum((sub[i+1:] - sub[i])**2, axis=1))
        dists.extend(d.flatten())
    dists = np.array(dists)
    dists = dists[dists > 0]
    
    if len(dists) < 50:
        return 0.0
    
    # C(r) = fraction of pairs with distance < r
    r_min = np.percentile(dists, 5)
    r_max = np.percentile(dists, 95)
    if r_max <= r_min:
        return 0.0
    
    rs = np.logspace(np.log10(r_min), np.log10(r_max), 20)
    Cr = np.array([np.mean(dists < r) for r in rs])
    
    # Fit log(C(r)) vs log(r) in scaling region
    mask = (Cr > 0.01) & (Cr < 0.5)
    if np.sum(mask) < 5:
        return 0.0
    
    log_r = np.log10(rs[mask])
    log_C = np.log10(Cr[mask])
    
    # Linear fit
    coeffs = np.polyfit(log_r, log_C, 1)
    D2 = coeffs[0]
    
    return max(D2, 0.0)

# ============================================================
# 3. Energy injection K (system-specific)
# ============================================================

def K_logistic(r, n_steps=10000):
    x = 0.5
    xs = []
    for _ in range(n_steps):
        x = r * x * (1 - x)
        xs.append(x)
    xs = np.array(xs)
    return r * np.mean(xs**2)

def K_henon(a, b=0.3, n_steps=10000):
    x, y = 0.1, 0.1
    xs = []
    for _ in range(5000):
        x, y = 1 - a*x**2 + y, b*x
    for _ in range(n_steps):
        x, y = 1 - a*x**2 + y, b*x
        xs.append(x)
    xs = np.array(xs)
    return a * np.mean(xs**2)

def K_ode(flow_fn, x0, dt=0.01, n_steps=10000, n_discard=5000):
    x = np.array(x0, dtype=float)
    for _ in range(n_discard):
        k1 = flow_fn(x)
        k2 = flow_fn(x + 0.5*dt*k1)
        k3 = flow_fn(x + 0.5*dt*k2)
        k4 = flow_fn(x + dt*k3)
        x = x + dt/6*(k1 + 2*k2 + 2*k3 + k4)
    
    xs = []
    for _ in range(n_steps):
        k1 = flow_fn(x)
        k2 = flow_fn(x + 0.5*dt*k1)
        k3 = flow_fn(x + 0.5*dt*k2)
        k4 = flow_fn(x + dt*k3)
        x = x + dt/6*(k1 + 2*k2 + 2*k3 + k4)
        xs.append(x.copy())
    
    xs = np.array(xs)
    return np.mean(xs[:, 0]**2)  # First coordinate variance proxy

# ============================================================
# 4. Time series generation for D_2
# ============================================================

def generate_logistic_series(r, n=30000):
    x = 0.5
    for _ in range(5000):
        x = r * x * (1 - x)
    return np.array([r * x * (1 - x) for x in __import__('itertools').accumulate(
        range(n), lambda x, _: r * x * (1 - x), initial=x)][1:])

def generate_henon_series(a, b=0.3, n=30000):
    x, y = 0.1, 0.1
    for _ in range(5000):
        x, y = 1 - a*x**2 + y, b*x
    series = []
    for _ in range(n):
        x, y = 1 - a*x**2 + y, b*x
        series.append(x)
    return np.array(series)

def generate_ode_series(flow_fn, x0, dt=0.01, n=30000, n_discard=5000):
    x = np.array(x0, dtype=float)
    for _ in range(n_discard):
        k1 = flow_fn(x)
        k2 = flow_fn(x + 0.5*dt*k1)
        k3 = flow_fn(x + 0.5*dt*k2)
        k4 = flow_fn(x + dt*k3)
        x = x + dt/6*(k1 + 2*k2 + 2*k3 + k4)
    
    series = []
    for _ in range(n):
        k1 = flow_fn(x)
        k2 = flow_fn(x + 0.5*dt*k1)
        k3 = flow_fn(x + 0.5*dt*k2)
        k4 = flow_fn(x + dt*k3)
        x = x + dt/6*(k1 + 2*k2 + 2*k3 + k4)
        series.append(x[0])
    
    return np.array(series)

# ============================================================
# 5. System definitions
# ============================================================

def lorenz_flow(sigma=10, rho=28, beta=8/3):
    return lambda x: np.array([sigma*(x[1]-x[0]), x[0]*(rho-x[2])-x[1], x[0]*x[1]-beta*x[2]])

def lorenz_jac(sigma=10, rho=28, beta=8/3):
    return lambda x: np.array([[-sigma, sigma, 0], [rho-x[2], -1, -x[0]], [x[1], x[0], -beta]])

def rossler_flow(a=0.2, b=0.2, c=5.7):
    return lambda x: np.array([-x[1]-x[2], x[0]+a*x[1], b+x[2]*(x[0]-c)])

def rossler_jac(a=0.2, b=0.2, c=5.7):
    return lambda x: np.array([[0, -1, -1], [1, a, 0], [0, 0, x[0]-c]])

def duffing_flow(alpha=1, beta=-1, delta=0.3, gamma=0.5, omega=1.2):
    return lambda x: np.array([x[1], -delta*x[1] - alpha*x[0] - beta*x[0]**3 + gamma*np.cos(omega*0)])

def duffing_jac(alpha=1, beta=-1, delta=0.3, gamma=0.5, omega=1.2):
    return lambda x: np.array([[0, 1], [-alpha - 3*beta*x[0]**2, -delta]])

# ============================================================
# 6. Main experiment: find onset of chaos, compute Q
# ============================================================

results = {}

# --- Hénon map (baseline, reproduce EMP-149) ---
print("=== Hénon Map ===")
henon_a_vals = np.linspace(1.0, 1.4, 20)
henon_lyaps = []
henon_Qs = []
for a in henon_a_vals:
    lyap = lyapunov_henon(a, n_steps=30000)
    series = generate_henon_series(a, n=20000)
    d2 = correlation_dimension(series)
    k = K_henon(a)
    Q = -lyap - d2 - k
    henon_lyaps.append(lyap)
    henon_Qs.append(Q)
    if lyap > 0:
        print(f"  a={a:.3f}: λ={lyap:.4f}, D2={d2:.3f}, K={k:.3f}, Q={Q:.3f}")

# Find onset (first a where λ > 0)
onset_idx = next((i for i, l in enumerate(henon_lyaps) if l > 0), None)
if onset_idx is not None:
    a_onset = henon_a_vals[onset_idx]
    print(f"  Onset at a={a_onset:.3f}, Q={henon_Qs[onset_idx]:.3f}")
    results['henon'] = {
        'onset_param': float(a_onset),
        'lyap_at_onset': float(henon_lyaps[onset_idx]),
        'D2_at_onset': float(correlation_dimension(generate_henon_series(a_onset, n=30000))),
        'K_at_onset': float(K_henon(a_onset)),
        'Q_at_onset': float(henon_Qs[onset_idx]),
        'all_Qs': [float(q) for q in henon_Qs],
        'all_params': [float(a) for a in henon_a_vals]
    }

# --- Logistic map ---
print("\n=== Logistic Map ===")
log_r_vals = np.linspace(3.5, 4.0, 30)
log_lyaps = []
log_Qs = []
for r in log_r_vals:
    lyap = lyapunov_logistic(r, n_steps=30000)
    series = generate_logistic_series(r, n=20000)
    d2 = correlation_dimension(series)
    k = K_logistic(r)
    Q = -lyap - d2 - k
    log_lyaps.append(lyap)
    log_Qs.append(Q)
    if lyap > 0:
        print(f"  r={r:.4f}: λ={lyap:.4f}, D2={d2:.3f}, K={k:.3f}, Q={Q:.3f}")

# Find first onset
onset_idx = next((i for i, l in enumerate(log_lyaps) if l > 0), None)
if onset_idx is not None:
    r_onset = log_r_vals[onset_idx]
    print(f"  Onset at r={r_onset:.4f}, Q={log_Qs[onset_idx]:.3f}")
    results['logistic'] = {
        'onset_param': float(r_onset),
        'lyap_at_onset': float(log_lyaps[onset_idx]),
        'D2_at_onset': float(correlation_dimension(generate_logistic_series(r_onset, n=30000))),
        'K_at_onset': float(K_logistic(r_onset)),
        'Q_at_onset': float(log_Qs[onset_idx]),
        'all_Qs': [float(q) for q in log_Qs],
        'all_params': [float(r) for r in log_r_vals]
    }

# --- Lorenz system (already chaotic at default params) ---
print("\n=== Lorenz ===")
# Lorenz is chaotic for rho > ~24.74
rho_vals = np.linspace(20, 40, 15)
loren_lyaps = []
loren_Qs = []
for rho in rho_vals:
    flow = lorenz_flow(rho=rho)
    jac = lorenz_jac(rho=rho)
    lyap = lyapunov_ode(flow, jac, [1.0, 1.0, 1.0], dt=0.01, n_steps=20000)
    series = generate_ode_series(flow, [1.0, 1.0, 1.0], dt=0.01, n=20000)
    d2 = correlation_dimension(series)
    k = K_ode(flow, [1.0, 1.0, 1.0], dt=0.01, n_steps=5000)
    Q = -lyap - d2 - k
    loren_lyaps.append(lyap)
    loren_Qs.append(Q)
    print(f"  rho={rho:.1f}: λ={lyap:.4f}, D2={d2:.3f}, K={k:.3f}, Q={Q:.3f}")

onset_idx = next((i for i, l in enumerate(loren_lyaps) if l > 0), None)
if onset_idx is not None:
    rho_onset = rho_vals[onset_idx]
    print(f"  Onset at rho={rho_onset:.1f}, Q={loren_Qs[onset_idx]:.3f}")
    results['lorenz'] = {
        'onset_param': float(rho_onset),
        'lyap_at_onset': float(loren_lyaps[onset_idx]),
        'D2_at_onset': float(correlation_dimension(generate_ode_series(lorenz_flow(rho=rho_onset), [1.0,1.0,1.0], n=30000))),
        'K_at_onset': float(K_ode(lorenz_flow(rho=rho_onset), [1.0,1.0,1.0])),
        'Q_at_onset': float(loren_Qs[onset_idx]),
        'all_Qs': [float(q) for q in loren_Qs],
        'all_params': [float(r) for r in rho_vals]
    }

# --- Rössler system ---
print("\n=== Rössler ===")
c_vals = np.linspace(2, 8, 12)
ross_lyaps = []
ross_Qs = []
for c in c_vals:
    flow = rossler_flow(c=c)
    jac = rossler_jac(c=c)
    lyap = lyapunov_ode(flow, jac, [0.1, 0.1, 0.1], dt=0.05, n_steps=20000)
    series = generate_ode_series(flow, [0.1, 0.1, 0.1], dt=0.05, n=20000)
    d2 = correlation_dimension(series)
    k = K_ode(flow, [0.1, 0.1, 0.1], dt=0.05, n_steps=5000)
    Q = -lyap - d2 - k
    ross_lyaps.append(lyap)
    ross_Qs.append(Q)
    print(f"  c={c:.2f}: λ={lyap:.4f}, D2={d2:.3f}, K={k:.3f}, Q={Q:.3f}")

onset_idx = next((i for i, l in enumerate(ross_lyaps) if l > 0), None)
if onset_idx is not None:
    c_onset = c_vals[onset_idx]
    print(f"  Onset at c={c_onset:.2f}, Q={ross_Qs[onset_idx]:.3f}")
    results['rossler'] = {
        'onset_param': float(c_onset),
        'lyap_at_onset': float(ross_lyaps[onset_idx]),
        'D2_at_onset': float(correlation_dimension(generate_ode_series(rossler_flow(c=c_onset), [0.1,0.1,0.1], dt=0.05, n=30000))),
        'K_at_onset': float(K_ode(rossler_flow(c=c_onset), [0.1,0.1,0.1], dt=0.05)),
        'Q_at_onset': float(ross_Qs[onset_idx]),
        'all_Qs': [float(q) for q in ross_Qs],
        'all_params': [float(c) for c in c_vals]
    }

# ============================================================
# 7. Summary
# ============================================================
print("\n" + "="*60)
print("CROSS-SYSTEM Q UNIVERSALITY SUMMARY")
print("="*60)
print(f"{'System':<12} {'λ_onset':<10} {'D2_onset':<10} {'K_onset':<10} {'Q_onset':<10}")
print("-"*60)
for name, r in results.items():
    print(f"{name:<12} {r['lyap_at_onset']:<10.4f} {r['D2_at_onset']:<10.3f} {r['K_at_onset']:<10.3f} {r['Q_at_onset']:<10.3f}")

print("\nQ values at onset across systems:")
q_onsets = [r['Q_at_onset'] for r in results.values()]
if len(q_onsets) > 1:
    print(f"  Mean Q: {np.mean(q_onsets):.3f}")
    print(f"  Std Q:  {np.std(q_onsets):.3f}")
    print(f"  Range:  [{np.min(q_onsets):.3f}, {np.max(q_onsets):.3f}]")
    print(f"  CV:     {np.std(q_onsets)/abs(np.mean(q_onsets)):.3f}")
    
    if np.std(q_onsets) < 0.5 * abs(np.mean(q_onsets)):
        print("\n  ✅ Q appears UNIVERSAL at chaotic onset (low coefficient of variation)")
    else:
        print("\n  ✗ Q is NOT universal at chaotic onset (high variation across systems)")
else:
    print("  Insufficient systems with detected chaos onset")

# Save results
with open('q_universality_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to q_universality_results.json")
print(f"Systems analyzed: {list(results.keys())}")