import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R16: Chimera States - Broken Symmetry in Oscillator Networks ===')

# Chimera state: nonlocal coupling on a ring
# Each oscillator couples to neighbors within a range R
# dtheta_i/dt = omega_i + (K/(2R+1)) * sum_{j=i-R}^{i+R} sin(theta_j - theta_i)
# With identical frequencies (omega_i = 0), coupling strength K and range alpha

N = 256
dt = 0.01
steps = 5000
skip = 2000

# Nonlocal coupling kernel: exponential decay
# Coupling function: G(r) = exp(-r/sigma) 
# This is the standard chimera setup (Abrams & Strogatz 2004)

# Parameters: alpha = phase lag, sigma = coupling range
# Chimera emerges when coupling is nonlocal (not all-to-all, not nearest-neighbor)

alpha = np.pi/2 - 0.15  # phase lag parameter
sigma = 0.2  # coupling range (fraction of N)

# Precompute coupling matrix
coupling_matrix = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        if i != j:
            dist = min(abs(i-j), N-abs(i-j)) / N  # normalized distance on ring
            coupling_matrix[i, j] = np.exp(-dist/sigma) * np.sin(alpha)
# Normalize each row
row_sums = coupling_matrix.sum(axis=1, keepdims=True)
coupling_matrix = coupling_matrix / (N * row_sums + 1e-10)

# Initial condition: half coherent, half random
theta = np.zeros(N)
theta[:N//2] = np.linspace(0, 2*np.pi, N//2)  # ordered
theta[N//2:] = np.random.uniform(0, 2*np.pi, N//2)  # random

# Run simulation
r_local_history = []  # local order parameter
theta_history = []

for step in range(steps):
    diff = theta[np.newaxis, :] - theta[:, np.newaxis]
    coupling = K * (coupling_matrix * np.sin(diff)).sum(axis=1) if 'K' in dir() else (coupling_matrix * np.sin(diff)).sum(axis=1)
    dtheta = coupling
    theta += dtheta * dt
    theta %= (2*np.pi)
    
    if step >= skip and step % 10 == 0:
        # Compute local order parameter (window of 10 oscillators)
        r_local = np.zeros(N)
        window = 10
        for i in range(N):
            idx = range(i-window//2, i+window//2)
            idx = [k % N for k in idx]
            r_local[i] = np.abs(np.mean(np.exp(1j*theta[idx])))
        r_local_history.append(r_local.copy())
        theta_history.append(theta.copy())

r_local_history = np.array(r_local_history)
theta_history = np.array(theta_history)

print('Local order parameter range: [{:.3f}, {:.3f}]'.format(
    r_local_history[-1].min(), r_local_history[-1].max()))
print('Mean local order: coherent side={:.3f}, incoherent side={:.3f}'.format(
    r_local_history[-1, :N//2].mean(), r_local_history[-1, N//2:].mean()))

# Plot: space-time diagram of phases and local order parameter
fig, axes = plt.subplots(2, 1, figsize=(16, 10))
fig.patch.set_facecolor('#0a0a1a')

# Top: phase space-time
ax1 = axes[0]
# Normalize phases to [0,1] for colormap
phase_norm = (theta_history % (2*np.pi)) / (2*np.pi)
im = ax1.imshow(phase_norm, aspect='auto', cmap='twilight', 
                extent=[0, N, 0, len(theta_history)])
ax1.set_ylabel('Time', fontsize=12, color='#e7e7f0')
ax1.set_title('R16: Chimera State - Phase Space-Time Diagram', fontsize=14, color='#e7e7f0')
ax1.set_facecolor('#0a0a1a')
ax1.tick_params(colors='#8a8aa3')
plt.colorbar(im, ax=ax1, label='Phase', fraction=0.03)

# Bottom: local order parameter
ax2 = axes[1]
for t_idx in range(0, len(r_local_history), 5):
    ax2.plot(r_local_history[t_idx], alpha=0.1, color='#44ccff')
ax2.plot(r_local_history[-1], color='#ff4444', lw=2, label='Final state')
ax2.set_xlabel('Oscillator Index', fontsize=12, color='#e7e7f0')
ax2.set_ylabel('Local Order Parameter r', fontsize=12, color='#e7e7f0')
ax2.set_title('R16: Local Order Parameter (coherent vs incoherent regions)', fontsize=14, color='#e7e7f0')
ax2.set_facecolor('#0a0a1a')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.2, color='#3a3a5a')
ax2.set_ylim(-0.05, 1.05)
ax2.legend(fontsize=11, facecolor='#1a1a2a', edgecolor='#3a3a5a')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_chimera.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_chimera.png')
print('=== R16 COMPLETE ===')
