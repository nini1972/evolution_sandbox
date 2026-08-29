"""
Hénon-Heiles System: Hamiltonian Chaos in a Gravitational Potential
===================================================================
The Hénon-Heiles system models the motion of a star in a galaxy with an
axisymmetric potential. It was one of the first systems where chaos was
discovered in conservative (Hamiltonian) mechanics (1964).

H = 1/2 (px^2 + py^2) + 1/2 (x^2 + y^2) + x^2 y - y^3/3

Equations of motion:
  dx/dt = px
  dy/dt = py
  dpx/dt = -x - 2xy
  dpy/dt = -y - x^2 + y^2

The potential V = 1/2(x^2 + y^2) + x^2 y - y^3/3 has a triangular symmetry
and forms a bounded well with three escape channels at E > 1/6.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import json
from scipy.integrate import solve_ivp

def henon_heiles(t, state):
    x, y, px, py = state
    dxdt = px
    dydt = py
    dpxdt = -x - 2*x*y
    dpydt = -y - x**2 + y**2
    return [dxdt, dydt, dpxdt, dpydt]

def potential(x, y):
    return 0.5*(x**2 + y**2) + x**2*y - y**3/3.0

def energy(state):
    x, y, px, py = state
    return 0.5*(px**2 + py**2) + potential(x, y)

# ============================================================
# Phase 1: Potential surface and equipotential lines
# ============================================================
print("=== Phase 1: Potential Surface ===")
x_grid = np.linspace(-1.5, 1.5, 300)
y_grid = np.linspace(-1.5, 1.5, 300)
X, Y = np.meshgrid(x_grid, y_grid)
V = potential(X, Y)

fig1, axes = plt.subplots(1, 2, figsize=(18, 8))

# 3D-like contour plot
ax = axes[0]
levels = np.linspace(0, 0.5, 50)
cf = ax.contourf(X, Y, V, levels=levels, cmap='inferno', extend='max')
ax.contour(X, Y, V, levels=[1/6], colors='white', linewidths=2, linestyles='--')
plt.colorbar(cf, ax=ax, label='V(x,y)')
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_title('Hénon-Heiles Potential V(x,y)\n(white dashed: E=1/6, escape threshold)', fontsize=13, fontweight='bold')
ax.set_aspect('equal')

# Equipotential lines showing triangular symmetry
ax2 = axes[1]
levels2 = [0.01, 0.05, 0.1, 1/6, 0.2, 0.3, 0.4, 0.5]
cs = ax2.contour(X, Y, V, levels=levels2, cmap='viridis')
ax2.clabel(cs, inline=True, fontsize=8, fmt='%.3f')
ax2.set_xlabel('x', fontsize=12)
ax2.set_ylabel('y', fontsize=12)
ax2.set_title('Equipotential Lines\n(Triangular symmetry, 3 escape channels)', fontsize=13, fontweight='bold')
ax2.set_aspect('equal')
ax2.set_xlim(-1.5, 1.5)
ax2.set_ylim(-1.5, 1.5)

fig1.suptitle('Hénon-Heiles Potential: Star Motion in a Galactic Potential', fontsize=16, fontweight='bold')
plt.savefig('henon_heiles_potential.png', dpi=150, bbox_inches='tight')
print('Saved henon_heiles_potential.png')

# ============================================================
# Phase 2: Poincaré sections at different energies
# ============================================================
print("\n=== Phase 2: Poincaré Sections ===")

# Poincaré section: plot (y, py) whenever x=0 and px>0
Energies = [1/12, 1/8, 1/6, 0.15, 0.18]

fig2 = plt.figure(figsize=(20, 12))
gs = GridSpec(2, 3, figure=fig2, hspace=0.35, wspace=0.3)

for idx, E in enumerate(Energies):
    ax = fig2.add_subplot(gs[idx // 3, idx % 3])
    
    n_ic = 30
    colors = plt.cm.Spectral(np.linspace(0, 1, n_ic))
    
    for j in range(n_ic):
        # Initialize: x=0, random y, random py, compute px from energy
        y0 = np.random.uniform(-0.5, 0.5)
        py0 = np.random.uniform(-0.5, 0.5)
        # px^2 = 2E - 2V(0,y0) - py0^2
        V0 = potential(0, y0)
        px2 = 2*E - 2*V0 - py0**2
        if px2 < 0:
            continue
        px0 = np.sqrt(px2)
        
        state0 = [0, y0, px0, py0]
        
        # Verify energy
        if abs(energy(state0) - E) > 1e-8:
            continue
        
        # Integrate
        sol = solve_ivp(henon_heiles, [0, 2000], state0, 
                       method='DOP853', rtol=1e-10, atol=1e-12,
                       max_step=0.1, dense_output=True)
        
        if sol.success and len(sol.t) > 100:
            # Find crossings of x=0 with px>0
            x_traj = sol.y[0]
            px_traj = sol.y[2]
            
            crossings = []
            for k in range(len(x_traj)-1):
                if x_traj[k] * x_traj[k+1] < 0 and px_traj[k] > 0:  # x crosses 0 upward
                    # Linear interpolation
                    alpha = x_traj[k] / (x_traj[k] - x_traj[k+1])
                    y_cross = sol.y[1, k] + alpha * (sol.y[1, k+1] - sol.y[1, k])
                    py_cross = sol.y[3, k] + alpha * (sol.y[3, k+1] - sol.y[3, k])
                    crossings.append((y_cross, py_cross))
            
            if len(crossings) > 5:
                cy, cpy = zip(*crossings)
                ax.scatter(cy, cpy, s=0.3, c=[colors[j]], alpha=0.5, rasterized=True)
    
    ax.set_xlim(-0.8, 0.8)
    ax.set_ylim(-0.8, 0.8)
    ax.set_xlabel('y', fontsize=10)
    ax.set_ylabel('p_y', fontsize=10)
    
    if E < 1/12:
        regime = 'Regular (KAM tori)'
    elif E < 1/8:
        regime = 'Mostly regular'
    elif E < 1/6:
        regime = 'Mixed (chaos appears)'
    elif E == 1/6:
        regime = 'Escape threshold'
    else:
        regime = 'Chaotic (escapes possible)'
    
    ax.set_title(f'E = {E:.4f} ({regime})', fontsize=11, fontweight='bold')
    ax.set_aspect('equal')

fig2.suptitle('Hénon-Heiles: Poincaré Sections at Different Energies\n(x=0, p_x>0 crossings)',
              fontsize=16, fontweight='bold')
plt.savefig('henon_heiles_poincare.png', dpi=150, bbox_inches='tight')
print('Saved henon_heiles_poincare.png')

# ============================================================
# Phase 3: Trajectories at different energies
# ============================================================
print("\n=== Phase 3: Trajectories ===")

fig3, axes = plt.subplots(2, 3, figsize=(20, 12))
E_traj = [1/12, 1/8, 1/6, 0.15, 0.18, 0.22]

for idx, E in enumerate(E_traj):
    ax = axes[idx // 3, idx % 3]
    
    for trial in range(5):
        y0 = np.random.uniform(-0.3, 0.3)
        py0 = np.random.uniform(-0.3, 0.3)
        V0 = potential(0, y0)
        px2 = 2*E - 2*V0 - py0**2
        if px2 < 0:
            continue
        px0 = np.sqrt(px2)
        state0 = [0, y0, px0, py0]
        
        sol = solve_ivp(henon_heiles, [0, 500], state0,
                       method='DOP853', rtol=1e-10, atol=1e-12,
                       max_step=0.1)
        
        if sol.success:
            ax.plot(sol.y[0], sol.y[1], linewidth=0.3, alpha=0.5)
    
    # Draw potential boundary at this energy
    theta = np.linspace(0, 2*np.pi, 1000)
    for r in np.linspace(0.01, 2, 500):
        x_c = r * np.cos(theta)
        y_c = r * np.sin(theta)
        V_c = potential(x_c, y_c)
        if np.any(np.abs(V_c - E) < 0.01):
            mask = np.abs(V_c - E) < 0.01
            ax.scatter(x_c[mask], y_c[mask], s=0.1, c='red', alpha=0.3)
    
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel('x', fontsize=10)
    ax.set_ylabel('y', fontsize=10)
    
    if E <= 1/12: regime = 'Regular'
    elif E <= 1/8: regime = 'Mostly regular'
    elif E < 1/6: regime = 'Mixed'
    elif E == 1/6: regime = 'Escape threshold'
    else: regime = 'Chaotic/Escape'
    ax.set_title(f'E = {E:.4f} ({regime})', fontsize=11, fontweight='bold')
    ax.set_aspect('equal')

fig3.suptitle('Hénon-Heiles: Real Space Trajectories at Different Energies',
              fontsize=16, fontweight='bold')
plt.savefig('henon_heiles_trajectories.png', dpi=150, bbox_inches='tight')
print('Saved henon_heiles_trajectories.png')

# ============================================================
# Phase 4: Chaos indicator - Lyapunov vs Energy
# ============================================================
print("\n=== Phase 4: Lyapunov vs Energy ===")

def compute_lyapunov_hh(E, n_steps=50, T=500):
    """Compute Lyapunov exponent using variational method."""
    lyaps = []
    for _ in range(n_steps):
        y0 = np.random.uniform(-0.3, 0.3)
        py0 = np.random.uniform(-0.3, 0.3)
        V0 = potential(0, y0)
        px2 = 2*E - 2*V0 - py0**2
        if px2 < 0:
            continue
        px0 = np.sqrt(px2)
        state0 = np.array([0, y0, px0, py0])
        
        # Perturbation
        delta = np.array([1e-8, 0, 0, 0])
        log_sum = 0.0
        
        state = state0.copy()
        dt = 0.01
        n = int(T / dt)
        
        for _ in range(n):
            # RK4 for main trajectory
            k1 = np.array(henon_heiles(0, state))
            k2 = np.array(henon_heiles(0, state + 0.5*dt*k1))
            k3 = np.array(henon_heiles(0, state + 0.5*dt*k2))
            k4 = np.array(henon_heiles(0, state + dt*k3))
            state = state + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
            
            # Tangent dynamics (Jacobian)
            x, y, px, py = state
            # Jacobian of HH: d(f)/d(state)
            # dx/dt=px, dy/dt=py
            # dpx/dt=-x-2xy, dpy/dt=-y-x^2+y^2
            J = np.array([
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [-1-2*y, -2*x, 0, 0],
                [-2*x, -1+2*y, 0, 0]
            ])
            # Evolve perturbation: delta' = J @ delta
            k1d = J @ delta
            k2d = J @ (delta + 0.5*dt*k1d)
            k3d = J @ (delta + 0.5*dt*k2d)
            k4d = J @ (delta + dt*k3d)
            delta = delta + dt/6 * (k1d + 2*k2d + 2*k3d + k4d)
            
            # Renormalize
            norm = np.linalg.norm(delta)
            if norm > 0:
                log_sum += np.log(norm)
                delta = delta / norm
        
        lyaps.append(log_sum / T)
    
    return np.mean(lyaps), np.std(lyaps)

E_scan = np.linspace(0.02, 0.20, 20)
lyap_mean = np.zeros(len(E_scan))
lyap_std = np.zeros(len(E_scan))

for i, E in enumerate(E_scan):
    lm, ls = compute_lyapunov_hh(E, n_steps=10, T=200)
    lyap_mean[i] = lm
    lyap_std[i] = ls
    print(f"  E={E:.4f}, λ={lm:.4f} ± {ls:.4f}")

fig4, ax = plt.subplots(figsize=(12, 7))
ax.errorbar(E_scan, lyap_mean, yerr=lyap_std, fmt='bo-', capsize=3, markersize=5)
ax.axhline(0, color='k', linewidth=0.5)
ax.axvline(1/12, color='g', linestyle='--', alpha=0.7, label='E=1/12 (onset of chaos)')
ax.axvline(1/6, color='r', linestyle='--', alpha=0.7, label='E=1/6 (escape threshold)')
ax.set_xlabel('Energy E', fontsize=13)
ax.set_ylabel('Lyapunov exponent λ', fontsize=13)
ax.set_title('Hénon-Heiles: Lyapunov Exponent vs Energy', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.savefig('henon_heiles_lyapunov.png', dpi=150, bbox_inches='tight')
print('Saved henon_heiles_lyapunov.png')

# ============================================================
# Save data
# ============================================================
data = {
    'system': 'Hénon-Heiles',
    'equations': {
        'hamiltonian': 'H = 1/2(px^2 + py^2) + 1/2(x^2 + y^2) + x^2*y - y^3/3',
        'dx/dt': 'px',
        'dy/dt': 'py',
        'dpx/dt': '-x - 2*x*y',
        'dpy/dt': '-y - x^2 + y^2',
    },
    'type': 'Hamiltonian (2 degrees of freedom, conservative)',
    'key_energies': {
        'E_1/12': 0.0833,
        'E_1/8': 0.125,
        'E_1/6': 0.1667,  # escape threshold
    },
    'findings': {
        'E < 1/12': 'Completely regular — all trajectories on KAM tori',
        '1/12 < E < 1/8': 'Onset of chaos — first resonances break',
        '1/8 < E < 1/6': 'Mixed phase space — islands + chaotic sea',
        'E > 1/6': 'Chaotic trajectories can escape through channels',
        'onset_of_chaos': 'E ≈ 1/12 ≈ 0.083',
        'escape_threshold': 'E = 1/6 ≈ 0.167',
    },
    'lyapunov': 'λ ≈ 0 for E < 1/12, increases for E > 1/12',
    'significance': [
        'Second Hamiltonian chaos system (after Standard Map)',
        'Continuous-time Hamiltonian (vs. Standard Map which is discrete)',
        'Historical: one of the first numerical discoveries of chaos (1964)',
        'Triangular symmetry creates rich island structure in phase space',
        'Poincaré sections show KAM tori breaking progressively',
    ],
}
with open('henon_heiles_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Saved henon_heiles_data.json')
