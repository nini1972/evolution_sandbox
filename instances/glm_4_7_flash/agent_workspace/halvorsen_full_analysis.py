"""
Full Lyapunov spectrum + fractal dimension for the Halvorsen attractor.
Uses QR decomposition for the full spectrum (Benettin algorithm).
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def halvorsen_deriv(s, a=1.89):
    x, y, z = s
    return np.array([
        -a*x - 4*y - 4*z - y*y,
        -a*y - 4*z - 4*x - z*z,
        -a*z - 4*x - 4*y - x*x
    ])

def halvorsen_jacobian(s, a=1.89):
    """Jacobian matrix of the Halvorsen system."""
    x, y, z = s
    return np.array([
        [-a, -4 - 2*y, -4],
        [-4, -a, -4 - 2*z],
        [-4 - 2*x, -4, -a]
    ])

def rk4_step(s, dt, a=1.89):
    k1 = halvorsen_deriv(s, a)
    k2 = halvorsen_deriv(s + 0.5*dt*k1, a)
    k3 = halvorsen_deriv(s + 0.5*dt*k2, a)
    k4 = halvorsen_deriv(s + dt*k3, a)
    return s + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

def rk4_step_with_tangent(s, Q, dt, a=1.89):
    """RK4 step for state + tangent vectors (variational equation)."""
    # State derivatives
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

# Parameters
a = 1.89
dt = 0.005
n_transient = 5000
n_lyap = 20000
renorm_every = 5  # QR decomposition every 5 steps

# Initialize
s = np.array([-1.48, -1.51, 2.04], dtype=float)
Q = np.eye(3)

# Transient
for _ in range(n_transient):
    s = rk4_step(s, dt, a)

lyap_sums = np.zeros(3)
lyap_counts = 0
lyap_history = []

# Main loop with QR
for step in range(n_lyap):
    s, Q = rk4_step_with_tangent(s, Q, dt, a)
    
    if step % renorm_every == 0 and step > 0:
        Q, R = np.linalg.qr(Q)
        diag = np.abs(np.diag(R))
        lyap_sums += np.log(diag)
        lyap_counts += 1
        
        if step % 2000 == 0:
            current_lyap = lyap_sums / (lyap_counts * renorm_every * dt)
            lyap_history.append(current_lyap.copy())
            print(f'Step {step}: λ = {current_lyap}')

lyap_spectrum = lyap_sums / (lyap_counts * renorm_every * dt)
print(f'\nFinal Lyapunov spectrum: {lyap_spectrum}')
print(f'λ1 = {lyap_spectrum[0]:.6f}')
print(f'λ2 = {lyap_spectrum[1]:.6f}')
print(f'λ3 = {lyap_spectrum[2]:.6f}')

# Kaplan-Yorke dimension
lyap_sorted = np.sort(lyap_spectrum)[::-1]
ky_dim = 0
for k in range(len(lyap_sorted)):
    partial_sum = sum(lyap_sorted[:k+1])
    if partial_sum > 0:
        ky_dim = k + 1
if ky_dim < len(lyap_sorted) and ky_dim > 0:
    ky_dim += sum(lyap_sorted[:ky_dim+1]) / abs(lyap_sorted[ky_dim])
elif ky_dim == 0:
    ky_dim = 0.0

# Actually compute properly
ky_dim = 0.0
cumsum = np.cumsum(lyap_sorted)
for j in range(len(lyap_sorted)):
    if cumsum[j] < 0:
        if j > 0:
            ky_dim = j + lyap_sorted[j-1] / abs(lyap_sorted[j]) - 1
            # Actually: DKY = j + S_j / |λ_{j+1}|
            ky_dim = j  # 1-indexed: j is the last index with positive cumsum
            ky_dim = (j) + cumsum[j-1] / abs(lyap_sorted[j])  # j is 1-indexed count
        break
else:
    ky_dim = float(len(lyap_sorted))

# Let me just compute it directly
def kaplan_yorke(lyap_spec):
    """Compute Kaplan-Yorke dimension from Lyapunov spectrum."""
    ls = np.sort(lyap_spec)[::-1]
    cumsum = np.cumsum(ls)
    for k in range(len(ls) - 1):
        if cumsum[k] > 0 and cumsum[k+1] <= 0:
            return k + 1 + cumsum[k] / abs(ls[k+1])
    return float(len(ls))

ky_dim = kaplan_yorke(lyap_spectrum)
print(f'Kaplan-Yorke dimension: {ky_dim:.4f}')
print(f'Sum of Lyapunov exponents: {sum(lyap_spectrum):.6f} (should be negative for dissipative)')

# Now generate trajectory for visualization
n_vis = 50000
traj = np.zeros((n_vis, 3))
for i in range(n_vis):
    s = rk4_step(s, dt, a)
    traj[i] = s

# Box-counting fractal dimension
def box_counting_dim(traj, scales=None):
    if scales is None:
        ranges = np.ptp(traj, axis=0)
        min_range = ranges.min()
        scales = np.logspace(-3, -0.5, 30) * min_range
    
    counts = []
    for eps in scales:
        # Grid bins
        traj_min = traj.min(axis=0)
        bins = np.floor((traj - traj_min) / eps).astype(int)
        unique_bins = np.unique(bins, axis=0)
        counts.append(len(unique_bins))
    
    log_inv = np.log(1.0 / np.array(scales))
    log_counts = np.log(np.array(counts))
    
    # Linear fit
    coeffs = np.polyfit(log_inv, log_counts, 1)
    return coeffs[0], scales, counts, log_inv, log_counts

bc_dim, bc_scales, bc_counts, bc_log_inv, bc_log_counts = box_counting_dim(traj)

print(f'Box-counting dimension: {bc_dim:.4f}')

# Update data
with open('halvorsen_data.json') as f:
    data = json.load(f)
data['lyapunov_spectrum'] = lyap_spectrum.tolist()
data['lyapunov_exponent'] = float(lyap_spectrum[0])
data['kaplan_yorke_dim'] = float(ky_dim)
data['box_counting_dim'] = float(bc_dim)
data['sum_lyapunov'] = float(sum(lyap_spectrum))
with open('halvorsen_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# === VISUALIZATION ===
fig = plt.figure(figsize=(20, 16))

# 1. 3D Attractor
ax1 = fig.add_subplot(231, projection='3d')
ax1.scatter(traj[::3, 0], traj[::3, 1], traj[::3, 2], s=0.1, c=traj[::3, 2], 
            cmap='plasma', alpha=0.5)
ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z')
ax1.set_title(f'Halvorsen Attractor (a={a})\n3-Fold Rotational Symmetry', fontsize=10)

# 2. XY projection
ax2 = fig.add_subplot(232)
ax2.scatter(traj[::3, 0], traj[::3, 1], s=0.1, c='cyan', alpha=0.3)
ax2.set_xlabel('X'); ax2.set_ylabel('Y')
ax2.set_title('XY Projection', fontsize=10)

# 3. Lyapunov convergence
ax3 = fig.add_subplot(233)
lyap_hist = np.array(lyap_history)
for i, label in enumerate(['λ₁', 'λ₂', 'λ₃']):
    ax3.plot(lyap_hist[:, i], label=f'{label} = {lyap_spectrum[i]:.4f}', linewidth=1.5)
ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax3.set_xlabel('Step (×2000)')
ax3.set_ylabel('Lyapunov Exponent')
ax3.set_title('Lyapunov Spectrum Convergence', fontsize=10)
ax3.legend(fontsize=8)

# 4. Box-counting dimension
ax4 = fig.add_subplot(234)
ax4.scatter(bc_log_inv, bc_log_counts, s=20, c='red', alpha=0.6)
fit_line = np.polyval(np.polyfit(bc_log_inv, bc_log_counts, 1), bc_log_inv)
ax4.plot(bc_log_inv, fit_line, 'b--', linewidth=2, label=f'D₀ = {bc_dim:.3f}')
ax4.set_xlabel('log(1/ε)')
ax4.set_ylabel('log(N(ε))')
ax4.set_title('Box-Counting Dimension', fontsize=10)
ax4.legend(fontsize=9)

# 5. Time series
ax5 = fig.add_subplot(235)
t = np.arange(0, min(5000, n_vis)) * dt
ax5.plot(t, traj[:5000, 0], 'b-', linewidth=0.5, label='x(t)', alpha=0.8)
ax5.plot(t, traj[:5000, 1], 'r-', linewidth=0.5, label='y(t)', alpha=0.6)
ax5.plot(t, traj[:5000, 2], 'g-', linewidth=0.5, label='z(t)', alpha=0.6)
ax5.set_xlabel('Time')
ax5.set_ylabel('State')
ax5.set_title('Time Series', fontsize=10)
ax5.legend(fontsize=8)

# 6. Poincaré section (z=0 crossing)
crossings = []
for i in range(1, len(traj)):
    if traj[i, 2] * traj[i-1, 2] < 0:  # z crosses zero
        # Linear interpolation
        alpha_c = traj[i-1, 2] / (traj[i-1, 2] - traj[i, 2])
        x_c = traj[i-1, 0] + alpha_c * (traj[i, 0] - traj[i-1, 0])
        y_c = traj[i-1, 1] + alpha_c * (traj[i, 1] - traj[i-1, 1])
        crossings.append([x_c, y_c])
crossings = np.array(crossings)

ax6 = fig.add_subplot(236)
if len(crossings) > 0:
    ax6.scatter(crossings[:, 0], crossings[:, 1], s=2, c='purple', alpha=0.5)
ax6.set_xlabel('X (at Z=0)')
ax6.set_ylabel('Y (at Z=0)')
ax6.set_title(f'Poincaré Section (Z=0)\n{len(crossings)} crossings', fontsize=10)

plt.suptitle(f'Halvorsen Attractor — Full Analysis\n'
             f'λ = [{lyap_spectrum[0]:.4f}, {lyap_spectrum[1]:.4f}, {lyap_spectrum[2]:.4f}]  |  '
             f'D_KY = {ky_dim:.3f}  |  D₀ = {bc_dim:.3f}  |  Σλ = {sum(lyap_spectrum):.4f}',
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('halvorsen_full_analysis.png', dpi=150, bbox_inches='tight')
print('Saved halvorsen_full_analysis.png')

# Summary
print(f'\n=== HALVORSEN ATTRACTOR SUMMARY ===')
print(f'Parameter: a = {a}')
print(f'Lyapunov spectrum: [{lyap_spectrum[0]:.6f}, {lyap_spectrum[1]:.6f}, {lyap_spectrum[2]:.6f}]')
print(f'Kaplan-Yorke dimension: {ky_dim:.4f}')
print(f'Box-counting dimension: {bc_dim:.4f}')
print(f'Sum of Lyapunov (dissipation): {sum(lyap_spectrum):.6f}')
print(f'Poincaré crossings: {len(crossings)}')
