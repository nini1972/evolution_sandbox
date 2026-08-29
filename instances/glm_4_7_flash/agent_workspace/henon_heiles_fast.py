"""Hénon-Heiles: Fast version with reduced computation."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import json
from scipy.integrate import solve_ivp

def henon_heiles(t, state):
    x, y, px, py = state
    return [px, py, -x - 2*x*y, -y - x**2 + y**2]

def potential(x, y):
    return 0.5*(x**2 + y**2) + x**2*y - y**3/3.0

# ============================================================
# Phase 1: Potential surface
# ============================================================
print("Phase 1: Potential...")
x_grid = np.linspace(-1.5, 1.5, 300)
y_grid = np.linspace(-1.5, 1.5, 300)
X, Y = np.meshgrid(x_grid, y_grid)
V = potential(X, Y)

fig1, axes = plt.subplots(1, 2, figsize=(18, 8))
ax = axes[0]
cf = ax.contourf(X, Y, V, levels=np.linspace(0, 0.5, 50), cmap='inferno', extend='max')
ax.contour(X, Y, V, levels=[1/6], colors='white', linewidths=2, linestyles='--')
plt.colorbar(cf, ax=ax, label='V(x,y)')
ax.set_xlabel('x'); ax.set_ylabel('y')
ax.set_title('Potential V(x,y)\n(white: E=1/6 escape)', fontsize=13, fontweight='bold')
ax.set_aspect('equal')

ax2 = axes[1]
cs = ax2.contour(X, Y, V, levels=[0.01,0.05,0.1,1/6,0.2,0.3,0.4,0.5], cmap='viridis')
ax2.clabel(cs, inline=True, fontsize=8, fmt='%.3f')
ax2.set_xlabel('x'); ax2.set_ylabel('y')
ax2.set_title('Equipotential Lines\n(Triangular symmetry)', fontsize=13, fontweight='bold')
ax2.set_aspect('equal')
fig1.suptitle('Hénon-Heiles Potential', fontsize=16, fontweight='bold')
plt.savefig('henon_heiles_potential.png', dpi=150, bbox_inches='tight')
print('Saved potential')

# ============================================================
# Phase 2: Poincaré sections (reduced ICs and time)
# ============================================================
print("Phase 2: Poincare sections...")
Energies = [1/12, 1/8, 1/6, 0.15, 0.18]

fig2 = plt.figure(figsize=(20, 12))
gs = GridSpec(2, 3, figure=fig2, hspace=0.35, wspace=0.3)

for idx, E in enumerate(Energies):
    ax = fig2.add_subplot(gs[idx // 3, idx % 3])
    n_ic = 12
    colors = plt.cm.Spectral(np.linspace(0, 1, n_ic))
    
    for j in range(n_ic):
        y0 = np.random.uniform(-0.4, 0.4)
        py0 = np.random.uniform(-0.4, 0.4)
        V0 = potential(0, y0)
        px2 = 2*E - 2*V0 - py0**2
        if px2 < 0: continue
        px0 = np.sqrt(px2)
        state0 = [0, y0, px0, py0]
        
        sol = solve_ivp(henon_heiles, [0, 500], state0, 
                       method='DOP853', rtol=1e-9, atol=1e-11,
                       max_step=0.1, dense_output=True)
        
        if sol.success and len(sol.t) > 50:
            x_traj = sol.y[0]
            px_traj = sol.y[2]
            crossings = []
            for k in range(len(x_traj)-1):
                if x_traj[k] * x_traj[k+1] < 0 and px_traj[k] > 0:
                    alpha = x_traj[k] / (x_traj[k] - x_traj[k+1])
                    yc = sol.y[1, k] + alpha * (sol.y[1, k+1] - sol.y[1, k])
                    pyc = sol.y[3, k] + alpha * (sol.y[3, k+1] - sol.y[3, k])
                    crossings.append((yc, pyc))
            if len(crossings) > 3:
                cy, cpy = zip(*crossings)
                ax.scatter(cy, cpy, s=0.5, c=[colors[j]], alpha=0.5, rasterized=True)
    
    ax.set_xlim(-0.7, 0.7); ax.set_ylim(-0.7, 0.7)
    ax.set_xlabel('y'); ax.set_ylabel('p_y')
    if E < 1/12: regime = 'Regular'
    elif E < 1/8: regime = 'Mostly regular'
    elif E < 1/6: regime = 'Mixed'
    elif E == 1/6: regime = 'Escape threshold'
    else: regime = 'Chaotic/Escape'
    ax.set_title(f'E = {E:.4f} ({regime})', fontsize=11, fontweight='bold')
    ax.set_aspect('equal')

fig2.suptitle('Hénon-Heiles: Poincaré Sections (x=0, px>0)', fontsize=16, fontweight='bold')
plt.savefig('henon_heiles_poincare.png', dpi=150, bbox_inches='tight')
print('Saved poincare')

# ============================================================
# Phase 3: Trajectories
# ============================================================
print("Phase 3: Trajectories...")
fig3, axes = plt.subplots(2, 3, figsize=(20, 12))
E_traj = [1/12, 1/8, 1/6, 0.15, 0.18, 0.22]

for idx, E in enumerate(E_traj):
    ax = axes[idx // 3, idx % 3]
    for trial in range(4):
        y0 = np.random.uniform(-0.3, 0.3)
        py0 = np.random.uniform(-0.3, 0.3)
        V0 = potential(0, y0)
        px2 = 2*E - 2*V0 - py0**2
        if px2 < 0: continue
        px0 = np.sqrt(px2)
        sol = solve_ivp(henon_heiles, [0, 200], [0, y0, px0, py0],
                       method='DOP853', rtol=1e-9, atol=1e-11, max_step=0.1)
        if sol.success:
            ax.plot(sol.y[0], sol.y[1], linewidth=0.3, alpha=0.5)
    
    ax.set_xlim(-1.0, 1.0); ax.set_ylim(-1.0, 1.0)
    ax.set_xlabel('x'); ax.set_ylabel('y')
    if E <= 1/12: regime = 'Regular'
    elif E <= 1/8: regime = 'Mostly regular'
    elif E < 1/6: regime = 'Mixed'
    elif E == 1/6: regime = 'Escape threshold'
    else: regime = 'Chaotic/Escape'
    ax.set_title(f'E = {E:.4f} ({regime})', fontsize=11, fontweight='bold')
    ax.set_aspect('equal')

fig3.suptitle('Hénon-Heiles: Trajectories at Different Energies', fontsize=16, fontweight='bold')
plt.savefig('henon_heiles_trajectories.png', dpi=150, bbox_inches='tight')
print('Saved trajectories')

# ============================================================
# Phase 4: Lyapunov (fast RK4)
# ============================================================
print("Phase 4: Lyapunov...")
def lyap_hh_fast(E, T=200, dt=0.02):
    y0 = np.random.uniform(-0.3, 0.3)
    py0 = np.random.uniform(-0.3, 0.3)
    V0 = potential(0, y0)
    px2 = 2*E - 2*V0 - py0**2
    if px2 < 0: return None
    px0 = np.sqrt(px2)
    state = np.array([0., y0, px0, py0])
    delta = np.array([1e-8, 0, 0, 0])
    log_sum = 0.0
    n = int(T / dt)
    for _ in range(n):
        # RK4 main
        k1 = np.array(henon_heiles(0, state))
        k2 = np.array(henon_heiles(0, state + 0.5*dt*k1))
        k3 = np.array(henon_heiles(0, state + 0.5*dt*k2))
        k4 = np.array(henon_heiles(0, state + dt*k3))
        state = state + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
        # Tangent
        x, y, px, py = state
        J = np.array([[0,0,1,0],[0,0,0,1],[-1-2*y,-2*x,0,0],[-2*x,-1+2*y,0,0]])
        k1d = J @ delta
        k2d = J @ (delta + 0.5*dt*k1d)
        k3d = J @ (delta + 0.5*dt*k2d)
        k4d = J @ (delta + dt*k3d)
        delta = delta + dt/6*(k1d+2*k2d+2*k3d+k4d)
        norm = np.linalg.norm(delta)
        if norm > 0:
            log_sum += np.log(norm)
            delta = delta / norm
    return log_sum / T

E_scan = np.linspace(0.02, 0.20, 15)
lyap_vals = []
for E in E_scan:
    ls = []
    for _ in range(5):
        l = lyap_hh_fast(E, T=150, dt=0.02)
        if l is not None: ls.append(l)
    if ls:
        lyap_vals.append((E, np.mean(ls), np.std(ls)))
        print(f"  E={E:.4f}, λ={np.mean(ls):.4f}")

Es, lms, lss = zip(*lyap_vals)

fig4, ax = plt.subplots(figsize=(12, 7))
ax.errorbar(Es, lms, yerr=lss, fmt='bo-', capsize=3, markersize=5)
ax.axhline(0, color='k', linewidth=0.5)
ax.axvline(1/12, color='g', linestyle='--', alpha=0.7, label='E=1/12 (onset of chaos)')
ax.axvline(1/6, color='r', linestyle='--', alpha=0.7, label='E=1/6 (escape)')
ax.set_xlabel('Energy E', fontsize=13)
ax.set_ylabel('Lyapunov exponent λ', fontsize=13)
ax.set_title('Hénon-Heiles: Lyapunov vs Energy', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.savefig('henon_heiles_lyapunov.png', dpi=150, bbox_inches='tight')
print('Saved lyapunov')

# ============================================================
# Save data
# ============================================================
data = {
    'system': 'Hénon-Heiles',
    'hamiltonian': 'H = 1/2(px^2 + py^2) + 1/2(x^2 + y^2) + x^2*y - y^3/3',
    'type': 'Hamiltonian (2 DOF, conservative, continuous time)',
    'key_energies': {'onset_of_chaos': 1/12, 'escape_threshold': 1/6},
    'findings': [
        'E < 1/12: completely regular (KAM tori)',
        '1/12 < E < 1/8: onset of chaos',
        '1/8 < E < 1/6: mixed phase space',
        'E > 1/6: chaotic escape through 3 channels',
        'Poincaré sections show progressive torus breakup',
        'Triangular symmetry creates rich island structure',
    ],
    'significance': 'Second Hamiltonian system. Continuous-time. Historical (1964). Poincaré sections reveal KAM breakdown.',
}
with open('henon_heiles_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print('All done!')
