"""
Chirikov Standard Map: Hamiltonian Chaos and the Kicked Rotor
==============================================================
p_{n+1} = p_n + K sin(θ_n)    (mod 2π)
θ_{n+1} = θ_n + p_{n+1}      (mod 2π)

A paradigm of Hamiltonian (conservative) chaos. Shows:
- KAM theorem breakdown as K increases
- Phase space transition from integrable to fully chaotic
- Diffusion in momentum (Fermi acceleration)
- Cantori as partial barriers in phase space
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import json

# ============================================================
# Standard Map
# ============================================================
def standard_map(theta, p, K, n_iter=10000):
    """Iterate the Chirikov standard map."""
    thetas = np.zeros(n_iter)
    ps = np.zeros(n_iter)
    for i in range(n_iter):
        p = p + K * np.sin(theta)
        theta = theta + p
        # Keep in [0, 2π) — but we track unwrapped p for diffusion
        thetas[i] = theta % (2 * np.pi)
        ps[i] = p  # unwrapped momentum
    return thetas, ps

def standard_map_mod(theta, p, K, n_iter=10000):
    """Iterate with p also taken mod 2π (phase space on torus)."""
    thetas = np.zeros(n_iter)
    ps = np.zeros(n_iter)
    for i in range(n_iter):
        p = (p + K * np.sin(theta)) % (2 * np.pi)
        theta = (theta + p) % (2 * np.pi)
        thetas[i] = theta
        ps[i] = p
    return thetas, ps

# ============================================================
# Phase 1: Phase space portraits at different K values
# ============================================================
print("=== Phase 1: Phase Space Portraits ===")
K_values = [0.5, 0.97, 1.5, 2.0, 5.0, 10.0]
n_iter = 5000
n_ic = 50  # number of initial conditions per K

fig = plt.figure(figsize=(24, 18))
gs = GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3)

for idx, K in enumerate(K_values):
    ax = fig.add_subplot(gs[idx // 2, (idx % 2) * 2:(idx % 2) * 2 + 2])
    
    colors = plt.cm.Spectral(np.linspace(0, 1, n_ic))
    for j in range(n_ic):
        theta0 = np.random.uniform(0, 2*np.pi)
        p0 = np.random.uniform(0, 2*np.pi)
        
        thetas, ps = standard_map_mod(theta0, p0, K, n_iter=n_iter)
        
        # Plot every point to see invariant curves / chaos
        ax.scatter(thetas, ps, s=0.1, c=[colors[j]], alpha=0.5, rasterized=True)
    
    ax.set_xlim(0, 2*np.pi)
    ax.set_ylim(0, 2*np.pi)
    ax.set_xlabel('θ', fontsize=10)
    ax.set_ylabel('p (mod 2π)', fontsize=10)
    
    if K < 1.0:
        regime = 'Mostly Regular (KAM)'
    elif K < 1.2:
        regime = 'Transition (K ≈ K_c ≈ 0.97)'
    elif K < 3.0:
        regime = 'Mixed Phase Space'
    else:
        regime = 'Fully Chaotic'
    
    ax.set_title(f'K = {K} ({regime})', fontsize=12, fontweight='bold')

fig.suptitle('Chirikov Standard Map: Hamiltonian Chaos in the Kicked Rotor',
             fontsize=18, fontweight='bold', y=0.99)
plt.savefig('standard_map_phasespace.png', dpi=150, bbox_inches='tight')
print('Saved standard_map_phasespace.png')

# ============================================================
# Phase 2: Momentum diffusion (unwrapped p)
# ============================================================
print("\n=== Phase 2: Momentum Diffusion ===")
K_diff_values = [0.5, 1.0, 2.0, 5.0, 10.0]
n_traj = 100
n_steps_diff = 50000

fig2, axes = plt.subplots(1, 2, figsize=(18, 7))

for K in K_diff_values:
    p_final = np.zeros(n_traj)
    p2_history = np.zeros(n_steps_diff)
    
    all_p = np.zeros((n_traj, n_steps_diff))
    
    for j in range(n_traj):
        theta0 = np.random.uniform(0, 2*np.pi)
        p0 = np.random.uniform(0, 2*np.pi)
        thetas, ps = standard_map(theta0, p0, K, n_iter=n_steps_diff)
        all_p[j] = ps
    
    # Mean squared displacement vs steps
    msd = np.mean(all_p**2, axis=0)
    steps = np.arange(1, n_steps_diff + 1)
    
    # Plot
    axes[0].loglog(steps, msd, label=f'K={K}', linewidth=1.5)
    
    # Estimate diffusion coefficient D = <Δp²> / (2n) for large n
    D = msd[-1] / (2 * n_steps_diff)
    print(f"  K={K}: D ≈ {D:.6f}, <p²> = {msd[-1]:.2f}")

# Reference lines
n_ref = np.array([100, n_steps_diff])
axes[0].loglog(n_ref, 0.01*n_ref, 'k--', alpha=0.3, label='∝ n (diffusive)')
axes[0].loglog(n_ref, 100*np.ones_like(n_ref), 'k:', alpha=0.3, label='∝ const (localized)')
axes[0].set_xlabel('Number of iterations n', fontsize=12)
axes[0].set_ylabel('⟨p²⟩ (mean squared momentum)', fontsize=12)
axes[0].set_title('Momentum Diffusion: ⟨p²⟩ vs n', fontsize=13, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].set_xlim(10, n_steps_diff)
axes[0].set_ylim(0.1, 1e6)

# Quasilinear diffusion coefficient: D_QL = K²/4
K_range = np.linspace(0.1, 15, 100)
D_QL = K_range**2 / 4

# Numerical D vs K
K_scan = np.linspace(0.1, 15, 50)
D_numerical = np.zeros(len(K_scan))
for i, K in enumerate(K_scan):
    all_p_scan = np.zeros((50, 20000))
    for j in range(50):
        theta0 = np.random.uniform(0, 2*np.pi)
        p0 = np.random.uniform(0, 2*np.pi)
        _, ps = standard_map(theta0, p0, K, n_iter=20000)
        all_p_scan[j] = ps
    msd_scan = np.mean(all_p_scan**2, axis=0)
    D_numerical[i] = msd_scan[-1] / (2 * 20000)

axes[1].plot(K_range, D_QL, 'r-', linewidth=2, label='Quasilinear: D = K²/4')
axes[1].plot(K_scan, D_numerical, 'bo', markersize=3, label='Numerical')
axes[1].set_xlabel('K (kick strength)', fontsize=12)
axes[1].set_ylabel('D (diffusion coefficient)', fontsize=12)
axes[1].set_title('Momentum Diffusion Coefficient vs K', fontsize=13, fontweight='bold')
axes[1].legend(fontsize=11)
axes[1].set_yscale('log')
axes[1].set_xlim(0, 15)

fig2.suptitle('Standard Map: Momentum Diffusion and Fermi Acceleration',
              fontsize=16, fontweight='bold')
plt.savefig('standard_map_diffusion.png', dpi=150, bbox_inches='tight')
print('Saved standard_map_diffusion.png')

# ============================================================
# Phase 3: Lyapunov exponent vs K
# ============================================================
print("\n=== Phase 3: Lyapunov Exponent ===")
K_lyap = np.linspace(0.1, 15, 100)
lyap_std = np.zeros(len(K_lyap))
n_traj_lyap = 20
n_steps_lyap = 10000

for i, K in enumerate(K_lyap):
    lyaps = np.zeros(n_traj_lyap)
    for j in range(n_traj_lyap):
        theta = np.random.uniform(0, 2*np.pi)
        p = np.random.uniform(0, 2*np.pi)
        dtheta = 1e-8
        dp = 0.0
        log_sum = 0.0
        
        for step in range(n_steps_lyap):
            # Evolve trajectory
            p = p + K * np.sin(theta)
            theta = theta + p
            
            # Evolve perturbation (tangent map)
            # dp' = dp + K cos(θ) * dθ
            # dθ' = dθ + dp'
            dp_new = dp + K * np.cos(theta - p) * dtheta  # θ here is old
            dtheta_new = dtheta + dp_new
            
            # Renormalize
            norm = np.sqrt(dtheta_new**2 + dp_new**2)
            if norm > 0:
                log_sum += np.log(norm)
                dtheta = dtheta_new / norm
                dp = dp_new / norm
            
            theta = theta % (2 * np.pi)
            p = p  # unwrapped
        
        lyaps[j] = log_sum / n_steps_lyap
    lyap_std[i] = np.mean(lyaps)
    
    if (i+1) % 20 == 0:
        print(f"  K={K:.2f}, λ={lyap_std[i]:.4f}")

fig3, ax = plt.subplots(figsize=(12, 7))
ax.plot(K_lyap, lyap_std, 'b-', linewidth=2)
ax.axhline(0, color='k', linewidth=0.5)
ax.axvline(0.97, color='r', linestyle='--', alpha=0.7, label='K_c ≈ 0.97 (critical)')
ax.set_xlabel('K (kick strength)', fontsize=13)
ax.set_ylabel('Lyapunov exponent λ', fontsize=13)
ax.set_title('Standard Map: Lyapunov Exponent vs Kick Strength', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.savefig('standard_map_lyapunov.png', dpi=150, bbox_inches='tight')
print('Saved standard_map_lyapunov.png')

# ============================================================
# Phase 4: Sticky islands and cantori
# ============================================================
print("\n=== Phase 4: Sticky Islands ===")
K_sticky = 3.0
n_ic_sticky = 200
n_iter_sticky = 20000

fig4, axes = plt.subplots(1, 2, figsize=(18, 8))

# Regular phase space
ax = axes[0]
for j in range(n_ic_sticky):
    theta0 = np.random.uniform(0, 2*np.pi)
    p0 = np.random.uniform(0, 2*np.pi)
    thetas, ps = standard_map_mod(theta0, p0, K_sticky, n_iter=n_iter_sticky)
    ax.scatter(thetas, ps, s=0.1, alpha=0.3, c='blue', rasterized=True)
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(0, 2*np.pi)
ax.set_xlabel('θ', fontsize=12)
ax.set_ylabel('p (mod 2π)', fontsize=12)
ax.set_title(f'Sticky Islands (K={K_sticky})\nZoom: Periodic Islands + Cantori', fontsize=13, fontweight='bold')

# Zoom into a region
ax2 = axes[1]
for j in range(n_ic_sticky):
    theta0 = np.random.uniform(2.0, 3.5)
    p0 = np.random.uniform(2.0, 3.5)
    thetas, ps = standard_map_mod(theta0, p0, K_sticky, n_iter=n_iter_sticky)
    ax2.scatter(thetas, ps, s=0.1, alpha=0.3, c='red', rasterized=True)
ax2.set_xlim(2.0, 3.5)
ax2.set_ylim(2.0, 3.5)
ax2.set_xlabel('θ', fontsize=12)
ax2.set_ylabel('p (mod 2π)', fontsize=12)
ax2.set_title(f'Zoomed: Island Chains & Cantori', fontsize=13, fontweight='bold')

fig4.suptitle('Standard Map: Mixed Phase Space with Sticky Islands and Cantori',
              fontsize=16, fontweight='bold')
plt.savefig('standard_map_sticky_islands.png', dpi=150, bbox_inches='tight')
print('Saved standard_map_sticky_islands.png')

# ============================================================
# Save data
# ============================================================
data = {
    'system': 'Chirikov Standard Map (Kicked Rotor)',
    'equations': 'p_{n+1} = p_n + K sin(θ_n), θ_{n+1} = θ_n + p_{n+1} (mod 2π)',
    'type': 'Hamiltonian (area-preserving) 2D map',
    'key_parameters': {
        'K_c_critical': 0.97,  # critical K for global chaos onset
        'K_quasilinear_valid': 'K >> 1',
    },
    'findings': {
        'KAM_regime': 'K < 0.97: mostly regular, invariant tori dominate',
        'transition': 'K ≈ 0.97: KAM tori break, chaotic sea forms',
        'mixed': '1 < K < 5: mixed phase space with islands + chaotic sea',
        'fully_chaotic': 'K > 5: nearly all phase space is chaotic',
        'diffusion': 'For K > K_c, momentum diffuses: ⟨p²⟩ ∝ D·n, D ≈ K²/4 (quasilinear)',
        'localization': 'For K < K_c, momentum is localized by KAM tori',
        'sticky_islands': 'At K=3, trajectories get stuck near islands for long times',
    },
    'lyapunov': 'λ > 0 for K > K_c, increases with K',
    'significance': [
        'First Hamiltonian chaos system in the atlas',
        'Conservative dynamics: phase space volume preserved (no attractor)',
        'KAM theorem: most tori survive small perturbations, break at resonances',
        'Cantori (broken tori) act as partial barriers, causing sticky dynamics',
        'Momentum diffusion models Fermi acceleration in cosmic rays',
    ],
}

with open('standard_map_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Saved standard_map_data.json')
