"""
Thomas attractor visualization - fix the box-counting and generate clean plot.
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def thomas_deriv(s, b):
    x, y, z = s
    return np.array([np.sin(y) - b*x, np.sin(z) - b*y, np.sin(x) - b*z])

def thomas_jacobian(s, b):
    x, y, z = s
    return np.array([[-b, np.cos(y), 0], [0, -b, np.cos(z)], [np.cos(x), 0, -b]])

def rk4_step(s, dt, b):
    k1 = thomas_deriv(s, b)
    k2 = thomas_deriv(s + 0.5*dt*k1, b)
    k3 = thomas_deriv(s + 0.5*dt*k2, b)
    k4 = thomas_deriv(s + dt*k3, b)
    return s + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

def rk4_step_with_tangent(s, Q, dt, b):
    def deriv_full(s, Q):
        ds = thomas_deriv(s, b)
        J = thomas_jacobian(s, b)
        return ds, J @ Q
    k1s, k1Q = deriv_full(s, Q)
    k2s, k2Q = deriv_full(s + 0.5*dt*k1s, Q + 0.5*dt*k1Q)
    k3s, k3Q = deriv_full(s + 0.5*dt*k2s, Q + 0.5*dt*k2Q)
    k4s, k4Q = deriv_full(s + dt*k3s, Q + dt*k3Q)
    return (s + (dt/6.0)*(k1s + 2*k2s + 2*k3s + k4s),
            Q + (dt/6.0)*(k1Q + 2*k2Q + 2*k3Q + k4Q))

def kaplan_yorke(lyap_spec):
    ls = np.sort(lyap_spec)[::-1]
    cumsum = np.cumsum(ls)
    for k in range(len(ls) - 1):
        if cumsum[k] > 0 and cumsum[k+1] <= 0:
            return k + 1 + cumsum[k] / abs(ls[k+1])
    return float(len(ls))

b = 0.1
dt = 0.01
n_transient = 8000
n_lyap = 15000

s = np.array([0.1, 0.1, 0.1], dtype=float)
Q = np.eye(3)
for _ in range(n_transient):
    s = rk4_step(s, dt, b)

lyap_sums = np.zeros(3)
lyap_counts = 0
lyap_history = []
for step in range(n_lyap):
    s, Q = rk4_step_with_tangent(s, Q, dt, b)
    if step % 5 == 0 and step > 0:
        Q, R = np.linalg.qr(Q)
        diag = np.abs(np.diag(R))
        lyap_sums += np.log(diag)
        lyap_counts += 1
        if step % 3000 == 0:
            current = lyap_sums / (lyap_counts * 5 * dt)
            lyap_history.append(current.copy())
            print(f'Step {step}: λ = {current}')

lyap_spectrum = lyap_sums / (lyap_counts * 5 * dt)
ky_dim = kaplan_yorke(lyap_spectrum)
print(f'\nLyapunov: {lyap_spectrum}')
print(f'D_KY: {ky_dim:.4f}')

# Trajectory
n_vis = 60000
traj = np.zeros((n_vis, 3))
for i in range(n_vis):
    s = rk4_step(s, dt, b)
    traj[i] = s

# Box-counting with safe ranges
def box_counting_dim(traj, n_scales=20):
    ranges = np.ptp(traj, axis=0)
    min_range = max(ranges.min(), 0.01)
    max_range = max(ranges.max(), 0.1)
    scales = np.logspace(np.log10(min_range * 0.05), np.log10(max_range * 0.5), n_scales)
    counts = []
    for eps in scales:
        if eps < 1e-10:
            continue
        traj_min = traj.min(axis=0)
        bins = np.floor((traj - traj_min) / eps).astype(int)
        unique_bins = np.unique(bins, axis=0)
        counts.append(len(unique_bins))
    valid_scales = [s for s, c in zip(scales, counts) if c > 0 and c < len(traj)]
    valid_counts = [c for s, c in zip(scales, counts) if c > 0 and c < len(traj)]
    log_inv = np.log(1.0 / np.array(valid_scales))
    log_counts = np.log(np.array(valid_counts))
    coeffs = np.polyfit(log_inv, log_counts, 1)
    return coeffs[0], log_inv, log_counts

bc_dim, bc_log_inv, bc_log_counts = box_counting_dim(traj)
print(f'D_0 (box-counting): {bc_dim:.4f}')

# Poincaré
crossings = []
for i in range(1, len(traj)):
    if traj[i, 2] * traj[i-1, 2] < 0:
        alpha_c = traj[i-1, 2] / (traj[i-1, 2] - traj[i, 2])
        x_c = traj[i-1, 0] + alpha_c * (traj[i, 0] - traj[i-1, 0])
        y_c = traj[i-1, 1] + alpha_c * (traj[i, 1] - traj[i-1, 1])
        crossings.append([x_c, y_c])
crossings = np.array(crossings)

# === VISUALIZATION ===
fig = plt.figure(figsize=(22, 18))
colors = np.arange(len(traj[::5]))
norm_c = colors / max(colors)

ax1 = fig.add_subplot(331, projection='3d')
ax1.scatter(traj[::5, 0], traj[::5, 1], traj[::5, 2], s=0.15, c=norm_c, cmap='viridis', alpha=0.4)
ax1.set_xlabel('X', fontsize=8); ax1.set_ylabel('Y', fontsize=8); ax1.set_zlabel('Z', fontsize=8)
ax1.set_title(f'Thomas Attractor (b={b})', fontsize=11)
ax1.view_init(elev=20, azim=45)

ax2 = fig.add_subplot(332, projection='3d')
ax2.scatter(traj[::5, 0], traj[::5, 1], traj[::5, 2], s=0.15, c=traj[::5, 2], cmap='viridis', alpha=0.4)
ax2.set_title('View from Top', fontsize=11)
ax2.view_init(elev=80, azim=0)

for idx, (i, j, label) in enumerate([(0, 1, 'XY'), (0, 2, 'XZ'), (1, 2, 'YZ')]):
    ax = fig.add_subplot(3, 3, idx+3)
    ax.scatter(traj[::5, i], traj[::5, j], s=0.15, c=norm_c, cmap='viridis', alpha=0.3)
    ax.set_xlabel(label[0]); ax.set_ylabel(label[1])
    ax.set_title(f'{label} Projection', fontsize=11)

ax6 = fig.add_subplot(336)
lyap_hist = np.array(lyap_history)
for i, label in enumerate(['λ₁', 'λ₂', 'λ₃']):
    ax6.plot(lyap_hist[:, i], label=f'{label}={lyap_spectrum[i]:.4f}', linewidth=1.5)
ax6.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax6.set_title('Lyapunov Convergence', fontsize=11)
ax6.legend(fontsize=8)

ax7 = fig.add_subplot(337)
ax7.scatter(bc_log_inv, bc_log_counts, s=25, c='red', alpha=0.7)
fit = np.polyval(np.polyfit(bc_log_inv, bc_log_counts, 1), bc_log_inv)
ax7.plot(bc_log_inv, fit, 'b--', linewidth=2, label=f'D₀={bc_dim:.3f}')
ax7.set_title('Box-Counting Dimension', fontsize=11)
ax7.legend(fontsize=9)

ax8 = fig.add_subplot(338)
if len(crossings) > 0:
    ax8.scatter(crossings[:, 0], crossings[:, 1], s=3, c='darkgreen', alpha=0.5)
ax8.set_xlabel('X (at Z=0)'); ax8.set_ylabel('Y (at Z=0)')
ax8.set_title(f'Poincaré Section (Z=0)\n{len(crossings)} crossings', fontsize=11)

ax9 = fig.add_subplot(339)
t = np.arange(min(8000, n_vis)) * dt
ax9.plot(t, traj[:8000, 0], 'b-', linewidth=0.3, alpha=0.8, label='x(t)')
ax9.plot(t, traj[:8000, 1], 'r-', linewidth=0.3, alpha=0.6, label='y(t)')
ax9.plot(t, traj[:8000, 2], 'g-', linewidth=0.3, alpha=0.6, label='z(t)')
ax9.set_title('Time Series', fontsize=11)
ax9.legend(fontsize=8)

plt.suptitle(f'Thomas Attractor — Comprehensive Analysis (b={b})\n'
             f'λ = [{lyap_spectrum[0]:.4f}, {lyap_spectrum[1]:.4f}, {lyap_spectrum[2]:.4f}]  |  '
             f'D_KY = {ky_dim:.3f}  |  D₀ = {bc_dim:.3f}  |  Σλ = {sum(lyap_spectrum):.4f}',
             fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('thomas_master_analysis.png', dpi=150, bbox_inches='tight')
print('Saved thomas_master_analysis.png')

# Save data
data = {
    "system": "Thomas Attractor",
    "equations": "dx=sin(y)-b*x, dy=sin(z)-b*y, dz=sin(x)-b*z",
    "parameters": {"b": float(b)},
    "lyapunov_spectrum": lyap_spectrum.tolist(),
    "lyapunov_exponent": float(lyap_spectrum[0]),
    "kaplan_yorke_dim": float(ky_dim),
    "box_counting_dim": float(bc_dim),
    "sum_lyapunov": float(sum(lyap_spectrum)),
    "poincare_crossings": len(crossings),
    "description": f"Thomas' cyclically symmetric attractor with sinusoidal coupling. "
                   f"At b={b}: λ₁={lyap_spectrum[0]:.4f}, D_KY={ky_dim:.3f}, D₀={bc_dim:.3f}."
}
with open('thomas_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f'\n=== THOMAS ATTRACTOR (b={b}) ===')
print(f'Lyapunov: [{lyap_spectrum[0]:.6f}, {lyap_spectrum[1]:.6f}, {lyap_spectrum[2]:.6f}]')
print(f'D_KY: {ky_dim:.4f}, D₀: {bc_dim:.4f}')
print(f'Poincaré crossings: {len(crossings)}')
