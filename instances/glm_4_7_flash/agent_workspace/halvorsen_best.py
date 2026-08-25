"""
High-quality visualization of Halvorsen attractor at its most chaotic parameter (a≈1.4).
Full Lyapunov spectrum, fractal dimension, Poincaré section, and multi-view renderings.
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def halvorsen_deriv(s, a):
    x, y, z = s
    return np.array([
        -a*x - 4*y - 4*z - y*y,
        -a*y - 4*z - 4*x - z*z,
        -a*z - 4*x - 4*y - x*x
    ])

def halvorsen_jacobian(s, a):
    x, y, z = s
    return np.array([
        [-a, -4 - 2*y, -4],
        [-4, -a, -4 - 2*z],
        [-4 - 2*x, -4, -a]
    ])

def rk4_step(s, dt, a):
    k1 = halvorsen_deriv(s, a)
    k2 = halvorsen_deriv(s + 0.5*dt*k1, a)
    k3 = halvorsen_deriv(s + 0.5*dt*k2, a)
    k4 = halvorsen_deriv(s + dt*k3, a)
    return s + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

def rk4_step_with_tangent(s, Q, dt, a):
    def deriv_full(s, Q):
        ds = halvorsen_deriv(s, a)
        J = halvorsen_jacobian(s, a)
        dQ = J @ Q
        return ds, dQ
    k1s, k1Q = deriv_full(s, Q)
    k2s, k2Q = deriv_full(s + 0.5*dt*k1s, Q + 0.5*dt*k1Q)
    k3s, k3Q = deriv_full(s + 0.5*dt*k2s, Q + 0.5*dt*k2Q)
    k4s, k4Q = deriv_full(s + dt*k3s, Q + dt*k3Q)
    s_new = s + (dt/6.0)*(k1s + 2*k2s + 2*k3s + k4s)
    Q_new = Q + (dt/6.0)*(k1Q + 2*k2Q + 2*k3Q + k4Q)
    return s_new, Q_new

# Use a=1.4 - strong chaos, stable
a = 1.4
dt = 0.005
n_transient = 8000
n_lyap = 15000
renorm_every = 5

s = np.array([-1.48, -1.51, 2.04], dtype=float)
Q = np.eye(3)

# Transient
for _ in range(n_transient):
    s = rk4_step(s, dt, a)

# Lyapunov spectrum
lyap_sums = np.zeros(3)
lyap_counts = 0
lyap_history = []

for step in range(n_lyap):
    s, Q = rk4_step_with_tangent(s, Q, dt, a)
    if step % renorm_every == 0 and step > 0:
        Q, R = np.linalg.qr(Q)
        diag = np.abs(np.diag(R))
        lyap_sums += np.log(diag)
        lyap_counts += 1
        if step % 3000 == 0:
            current = lyap_sums / (lyap_counts * renorm_every * dt)
            lyap_history.append(current.copy())
            print(f'Step {step}: λ = {current}')

lyap_spectrum = lyap_sums / (lyap_counts * renorm_every * dt)
print(f'\nFinal Lyapunov spectrum: {lyap_spectrum}')

def kaplan_yorke(lyap_spec):
    ls = np.sort(lyap_spec)[::-1]
    cumsum = np.cumsum(ls)
    for k in range(len(ls) - 1):
        if cumsum[k] > 0 and cumsum[k+1] <= 0:
            return k + 1 + cumsum[k] / abs(ls[k+1])
    return float(len(ls))

ky_dim = kaplan_yorke(lyap_spectrum)
print(f'Kaplan-Yorke dimension: {ky_dim:.4f}')

# Generate trajectory
n_vis = 60000
traj = np.zeros((n_vis, 3))
for i in range(n_vis):
    s = rk4_step(s, dt, a)
    traj[i] = s

# Box-counting dimension
def box_counting_dim(traj, n_scales=25):
    ranges = np.ptp(traj, axis=0)
    min_range = ranges.min()
    max_range = ranges.max()
    scales = np.logspace(np.log10(min_range * 0.01), np.log10(max_range * 0.5), n_scales)
    
    counts = []
    for eps in scales:
        traj_min = traj.min(axis=0)
        bins = np.floor((traj - traj_min) / eps).astype(int)
        unique_bins = np.unique(bins, axis=0)
        counts.append(len(unique_bins))
    
    log_inv = np.log(1.0 / np.array(scales))
    log_counts = np.log(np.array(counts))
    coeffs = np.polyfit(log_inv, log_counts, 1)
    return coeffs[0], scales, counts, log_inv, log_counts

bc_dim, bc_scales, bc_counts, bc_log_inv, bc_log_counts = box_counting_dim(traj)
print(f'Box-counting dimension: {bc_dim:.4f}')

# Poincaré sections
crossings_z = []
crossings_y = []
crossings_x = []
for i in range(1, len(traj)):
    if traj[i, 2] * traj[i-1, 2] < 0:
        alpha_c = traj[i-1, 2] / (traj[i-1, 2] - traj[i, 2])
        x_c = traj[i-1, 0] + alpha_c * (traj[i, 0] - traj[i-1, 0])
        y_c = traj[i-1, 1] + alpha_c * (traj[i, 1] - traj[i-1, 1])
        crossings_z.append([x_c, y_c])
    if traj[i, 1] * traj[i-1, 1] < 0:
        alpha_c = traj[i-1, 1] / (traj[i-1, 1] - traj[i, 1])
        x_c = traj[i-1, 0] + alpha_c * (traj[i, 0] - traj[i-1, 0])
        z_c = traj[i-1, 2] + alpha_c * (traj[i, 2] - traj[i-1, 2])
        crossings_y.append([x_c, z_c])
    if traj[i, 0] * traj[i-1, 0] < 0:
        alpha_c = traj[i-1, 0] / (traj[i-1, 0] - traj[i, 0])
        y_c = traj[i-1, 1] + alpha_c * (traj[i, 1] - traj[i-1, 1])
        z_c = traj[i-1, 2] + alpha_c * (traj[i, 2] - traj[i-1, 2])
        crossings_x.append([y_c, z_c])

crossings_z = np.array(crossings_z)
crossings_y = np.array(crossings_y)
crossings_x = np.array(crossings_x)

# === MASTER VISUALIZATION ===
fig = plt.figure(figsize=(22, 18))

# Color map based on time along trajectory
colors = np.arange(len(traj[::5]))
norm_c = colors / max(colors)

# 1. 3D Attractor - main view
ax1 = fig.add_subplot(331, projection='3d')
ax1.scatter(traj[::5, 0], traj[::5, 1], traj[::5, 2], s=0.15, c=norm_c, 
            cmap='inferno', alpha=0.4)
ax1.set_xlabel('X', fontsize=8); ax1.set_ylabel('Y', fontsize=8); ax1.set_zlabel('Z', fontsize=8)
ax1.set_title(f'Halvorsen Attractor (a={a})\n3-Fold Cyclic Symmetry', fontsize=11)
ax1.view_init(elev=20, azim=45)

# 2. 3D from different angle
ax2 = fig.add_subplot(332, projection='3d')
ax2.scatter(traj[::5, 0], traj[::5, 1], traj[::5, 2], s=0.15, c=traj[::5, 2], 
            cmap='plasma', alpha=0.4)
ax2.set_xlabel('X', fontsize=8); ax2.set_ylabel('Y', fontsize=8); ax2.set_zlabel('Z', fontsize=8)
ax2.set_title('View from Top', fontsize=11)
ax2.view_init(elev=80, azim=0)

# 3. XY projection
ax3 = fig.add_subplot(333)
ax3.scatter(traj[::5, 0], traj[::5, 1], s=0.15, c=norm_c, cmap='inferno', alpha=0.3)
ax3.set_xlabel('X'); ax3.set_ylabel('Y')
ax3.set_title('XY Plane Projection', fontsize=11)

# 4. XZ projection
ax4 = fig.add_subplot(334)
ax4.scatter(traj[::5, 0], traj[::5, 2], s=0.15, c=norm_c, cmap='inferno', alpha=0.3)
ax4.set_xlabel('X'); ax4.set_ylabel('Z')
ax4.set_title('XZ Plane Projection', fontsize=11)

# 5. YZ projection
ax5 = fig.add_subplot(335)
ax5.scatter(traj[::5, 1], traj[::5, 2], s=0.15, c=norm_c, cmap='inferno', alpha=0.3)
ax5.set_xlabel('Y'); ax5.set_ylabel('Z')
ax5.set_title('YZ Plane Projection', fontsize=11)

# 6. Lyapunov convergence
ax6 = fig.add_subplot(336)
lyap_hist = np.array(lyap_history)
for i, label in enumerate(['λ₁', 'λ₂', 'λ₃']):
    ax6.plot(lyap_hist[:, i], label=f'{label} = {lyap_spectrum[i]:.4f}', linewidth=1.5)
ax6.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax6.set_xlabel('Step (×3000)')
ax6.set_ylabel('Lyapunov Exponent')
ax6.set_title('Lyapunov Spectrum Convergence', fontsize=11)
ax6.legend(fontsize=8)

# 7. Box-counting dimension
ax7 = fig.add_subplot(337)
ax7.scatter(bc_log_inv, bc_log_counts, s=25, c='red', alpha=0.7)
fit_line = np.polyval(np.polyfit(bc_log_inv, bc_log_counts, 1), bc_log_inv)
ax7.plot(bc_log_inv, fit_line, 'b--', linewidth=2, label=f'D₀ = {bc_dim:.3f}')
ax7.set_xlabel('log(1/ε)')
ax7.set_ylabel('log N(ε)')
ax7.set_title('Box-Counting Dimension', fontsize=11)
ax7.legend(fontsize=9)

# 8. Poincaré section (z=0)
ax8 = fig.add_subplot(338)
if len(crossings_z) > 0:
    ax8.scatter(crossings_z[:, 0], crossings_z[:, 1], s=3, c='purple', alpha=0.5)
ax8.set_xlabel('X (at Z=0)')
ax8.set_ylabel('Y (at Z=0)')
ax8.set_title(f'Poincaré Section (Z=0)\n{len(crossings_z)} crossings', fontsize=11)

# 9. Time series
ax9 = fig.add_subplot(339)
t = np.arange(min(8000, n_vis)) * dt
ax9.plot(t, traj[:8000, 0], 'b-', linewidth=0.3, label='x(t)', alpha=0.8)
ax9.plot(t, traj[:8000, 1], 'r-', linewidth=0.3, label='y(t)', alpha=0.6)
ax9.plot(t, traj[:8000, 2], 'g-', linewidth=0.3, label='z(t)', alpha=0.6)
ax9.set_xlabel('Time')
ax9.set_ylabel('State')
ax9.set_title('Time Series (first 40 time units)', fontsize=11)
ax9.legend(fontsize=8)

plt.suptitle(f'Halvorsen Attractor — Comprehensive Analysis (a={a})\n'
             f'λ = [{lyap_spectrum[0]:.4f}, {lyap_spectrum[1]:.4f}, {lyap_spectrum[2]:.4f}]  |  '
             f'D_KY = {ky_dim:.3f}  |  D₀ = {bc_dim:.3f}  |  Σλ = {sum(lyap_spectrum):.4f}',
             fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('halvorsen_master_analysis.png', dpi=150, bbox_inches='tight')
print('Saved halvorsen_master_analysis.png')

# Update data
data = {
    "system": "Halvorsen Attractor",
    "equations": "dx=-a*x-4*y-4*z-y^2, dy=-a*y-4*z-4*x-z^2, dz=-a*z-4*x-4*y-x^2",
    "parameters": {"a": a},
    "lyapunov_spectrum": lyap_spectrum.tolist(),
    "lyapunov_exponent": float(lyap_spectrum[0]),
    "kaplan_yorke_dim": float(ky_dim),
    "box_counting_dim": float(bc_dim),
    "sum_lyapunov": float(sum(lyap_spectrum)),
    "poincare_crossings_z": len(crossings_z),
    "poincare_crossings_y": len(crossings_y),
    "poincare_crossings_x": len(crossings_x),
    "description": f"Cyclic polynomial strange attractor with 3-fold rotational symmetry. "
                   f"At a={a}: λ₁={lyap_spectrum[0]:.4f} (chaotic), "
                   f"D_KY={ky_dim:.3f}, D₀={bc_dim:.3f}. "
                   f"The system shows strong chaos at this parameter value."
}
with open('halvorsen_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f'\n=== HALVORSEN ATTRACTOR (a={a}) SUMMARY ===')
print(f'Lyapunov spectrum: [{lyap_spectrum[0]:.6f}, {lyap_spectrum[1]:.6f}, {lyap_spectrum[2]:.6f}]')
print(f'Kaplan-Yorke dimension: {ky_dim:.4f}')
print(f'Box-counting dimension: {bc_dim:.4f}')
print(f'Sum of Lyapunov (dissipation): {sum(lyap_spectrum):.6f}')
print(f'Poincaré crossings: Z={len(crossings_z)}, Y={len(crossings_y)}, X={len(crossings_x)}')
