import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

print("=== Chirikov Standard Map: KAM Tori Destruction ===")

def standard_map(p, theta, K):
    """Chirikov standard map: (theta, p) -> (theta', p')"""
    p_new = p + K * np.sin(theta)
    theta_new = theta + p_new
    # mod to [-pi, pi] for theta, [-pi, pi] for p display
    theta_new = (theta_new + np.pi) % (2*np.pi) - np.pi
    p_new = (p_new + np.pi) % (2*np.pi) - np.pi
    return p_new, theta_new

K_values = [0.1, 0.5, 0.9716354, 1.5, 5.0]
fig, axes = plt.subplots(1, 5, figsize=(25, 5.5))
fig.patch.set_facecolor('#0a0a1a')

for ax, K in zip(axes, K_values):
    ax.set_facecolor('#0a0a1a')
    n_iter = 2000
    n_ic = 60
    colors = plt.cm.Spectral(np.linspace(0, 1, n_ic))
    
    for j in range(n_ic):
        p0 = -np.pi + (j + 0.5) * (2*np.pi / n_ic)
        theta0 = 0.01 * (j % 7 - 3)
        p, theta = p0, theta0
        pts = []
        for _ in range(n_iter):
            p, theta = standard_map(p, theta, K)
            pts.append((theta, p))
        pts = np.array(pts)
        ax.scatter(pts[100:, 0], pts[100:, 1], s=0.15, color=colors[j], alpha=0.4, edgecolors='none')
    
    ax.set_xlim(-np.pi, np.pi)
    ax.set_ylim(-np.pi, np.pi)
    ax.set_xlabel('theta', color='gray', fontsize=9)
    ax.set_ylabel('p', color='gray', fontsize=9)
    label = f'K = {K}'
    if K == 0.9716354:
        label += ' (critical)'
    elif K == 0.1:
        label += ' (integrable)'
    elif K == 5.0:
        label += ' (fully chaotic)'
    ax.set_title(label, color='white', fontsize=11)
    ax.tick_params(colors='gray', labelsize=8)

plt.suptitle('Chirikov Standard Map: Destruction of KAM Tori as K Increases',
             fontsize=14, color='white', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('standard_map_kam.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("Saved standard_map_kam.png")

# Lyapunov exponent vs K
print("Computing Lyapunov exponents vs K...")
K_arr = np.linspace(0.01, 5.0, 100)
lyap = np.zeros(len(K_arr))
n_iter_ly = 2000

for idx, K in enumerate(K_arr):
    p, theta = 0.5, 0.1
    # Jacobian-based Lyapunov (tangent vector as 2x2 matrix)
    M = np.eye(2)  # tangent matrix
    lsum = 0.0
    for _ in range(n_iter_ly):
        # Jacobian of standard map at current theta
        ct = np.cos(theta)
        J = np.array([[1.0, K*ct], [1.0, 1.0 + K*ct]])
        M = J @ M
        # QR decomposition to prevent overflow
        Q, R = np.linalg.qr(M)
        lsum += np.log(abs(R[0, 0]))
        M = Q
        # Step the trajectory
        p_new = p + K * np.sin(theta)
        theta_new = theta + p_new
        p = (p_new + np.pi) % (2*np.pi) - np.pi
        theta = (theta_new + np.pi) % (2*np.pi) - np.pi
    lyap[idx] = lsum / n_iter_ly

fig2, ax2 = plt.subplots(figsize=(12, 5))
fig2.patch.set_facecolor('#0a0a1a')
ax2.set_facecolor('#0a0a1a')
ax2.plot(K_arr, lyap, color='cyan', linewidth=1.5)
ax2.axhline(y=0, color='red', linewidth=0.8, alpha=0.5, linestyle='--')
ax2.axvline(x=0.9716354, color='gold', linewidth=1, alpha=0.7, linestyle=':', label='K_c = 0.9716 (critical)')
ax2.fill_between(K_arr, lyap, 0, where=(lyap > 0), color='red', alpha=0.15, label='chaotic region')
ax2.set_xlabel('K (kick strength)', color='white', fontsize=12)
ax2.set_ylabel('Lyapunov exponent lambda', color='white', fontsize=12)
ax2.set_title('Standard Map: Lyapunov Exponent vs K', color='white', fontsize=14)
ax2.legend(facecolor='#1a1a3a', edgecolor='gray', labelcolor='white', fontsize=10)
ax2.tick_params(colors='gray')
plt.tight_layout()
plt.savefig('standard_map_lyapunov.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("Saved standard_map_lyapunov.png")

# Find where lambda crosses zero
cross_idx = np.where(np.diff(np.sign(lyap)) != 0)[0]
if len(cross_idx) > 0:
    K_critical = K_arr[cross_idx[0]]
    print(f"First Lyapunov zero-crossing at K = {K_critical:.4f}")
else:
    K_critical = None

data = {
    "system": "Chirikov Standard Map (Kicked Rotator)",
    "equations": "p_{n+1} = p_n + K*sin(theta_n), theta_{n+1} = theta_n + p_{n+1}",
    "K_values_visualized": K_values,
    "K_critical_KAM": 0.9716354,
    "K_first_positive_lyapunov": float(K_critical) if K_critical else None,
    "description": "As K increases past K_c~0.97, the last KAM torus breaks and global chaos sets in. Below K_c, invariant tori confine trajectories. Above, phase space becomes globally connected.",
    "lyapunov_at_K5": float(lyap[-1]),
    "lyapunov_at_K05": float(lyap[np.argmin(np.abs(K_arr-0.5))])
}
with open('standard_map_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Saved standard_map_data.json")
print("Done!")
