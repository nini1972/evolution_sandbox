import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R15: Kuramoto Model (FIXED) ===')

N = 100
dt = 0.02
steps = 2000
skip = 500

np.random.seed(42)
omega = np.random.normal(0, 1, N)

# Kuramoto: dtheta_i/dt = omega_i + (K/N) * sum_j sin(theta_j - theta_i)
# The coupling term should PULL theta_i toward theta_j

K_values = np.arange(0.0, 3.0, 0.1)
r_values = []

for K in K_values:
    theta = np.random.uniform(0, 2*np.pi, N)
    r_history = []
    for step in range(steps):
        # sin(theta_j - theta_i): when theta_j > theta_i, this is positive, pulling theta_i up
        diff = theta[np.newaxis, :] - theta[:, np.newaxis]  # diff[i,j] = theta_j - theta_i
        coupling = (K/N) * np.sin(diff).sum(axis=1)
        dtheta = omega + coupling
        theta += dtheta * dt
        theta %= (2*np.pi)
        if step >= skip:
            r = np.abs(np.mean(np.exp(1j*theta)))
            r_history.append(r)
    r_mean = np.mean(r_history)
    r_values.append(r_mean)
    print('  K={:.1f}: r={:.4f}'.format(K, r_mean))

r_values = np.array(r_values)

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')
ax.plot(K_values, r_values, 'o-', color='#44ccff', lw=2, markersize=5)
ax.set_xlabel('Coupling Strength K', fontsize=13, color='#e7e7f0')
ax.set_ylabel('Order Parameter r', fontsize=13, color='#e7e7f0')
ax.set_title('R15: Kuramoto Phase Transition - Collective Synchronization', fontsize=14, color='#e7e7f0')
ax.tick_params(colors='#8a8aa3')
ax.grid(True, alpha=0.2, color='#3a3a5a')
ax.set_ylim(-0.05, 1.05)
fig.savefig('../../shared_space/resonance_kuramoto.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_kuramoto.png')

# Phase distribution plots
fig2, axes = plt.subplots(1, 4, figsize=(20, 5), subplot_kw=dict(projection='polar'))
fig2.patch.set_facecolor('#0a0a1a')
K_demo = [0.0, 1.0, 2.0, 3.0]
for idx, K in enumerate(K_demo):
    theta = np.random.uniform(0, 2*np.pi, N)
    for step in range(2000):
        diff = theta[np.newaxis, :] - theta[:, np.newaxis]
        coupling = (K/N) * np.sin(diff).sum(axis=1)
        dtheta = omega + coupling
        theta += dtheta * dt
        theta %= (2*np.pi)
    r = np.abs(np.mean(np.exp(1j*theta)))
    ax = axes[idx]
    ax.scatter(theta, np.ones(N), s=15, c='#44ccff', alpha=0.7)
    ax.set_title('K={:.1f}, r={:.3f}'.format(K, r), fontsize=11, color='#e7e7f0')
    ax.set_facecolor('#0a0a1a')
    ax.tick_params(colors='#8a8aa3')
plt.suptitle('R15: Oscillator Phase Distribution at Different Coupling Strengths', fontsize=14, y=1.08, color='#e7e7f0')
plt.tight_layout()
fig2.savefig('../../shared_space/resonance_kuramoto_phases.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_kuramoto_phases.png')
print('=== R15 COMPLETE ===')
