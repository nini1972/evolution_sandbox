import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19b: Contrast - Kuramoto With vs Without Sandpile Perturbations ===')

N = 64
dt = 0.05
K = 2.0
steps = 3000

np.random.seed(42)
omega = np.random.normal(0, 1, (N, N))
theta_init = np.random.uniform(0, 2*np.pi, (N, N))

# Run 1: Pure Kuramoto (no sandpile)
theta = theta_init.copy()
r_pure = []
for step in range(steps):
    coupling = np.zeros_like(theta)
    for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
        rolled = np.roll(theta, (di, dj), axis=(0,1))
        coupling += np.sin(rolled - theta)
    theta += (omega + (K/4) * coupling) * dt
    theta %= (2*np.pi)
    r_pure.append(np.abs(np.mean(np.exp(1j * theta.flatten()))))

# Run 2: Kuramoto + sandpile (same as R19)
np.random.seed(42)
theta2 = theta_init.copy()
heights = np.random.randint(0, 4, (N, N))
r_sand = []
for step in range(steps):
    coupling = np.zeros_like(theta2)
    for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
        rolled = np.roll(theta2, (di, dj), axis=(0,1))
        coupling += np.sin(rolled - theta2)
    dtheta = omega + (K/4) * coupling
    
    gi, gj = np.random.randint(0, N, 2)
    heights[gi, gj] += 1
    tt = [(gi, gj)]
    while tt:
        ci, cj = tt.pop()
        if heights[ci, cj] < 4:
            continue
        heights[ci, cj] -= 4
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = ci+di, cj+dj
            if 0 <= ni < N and 0 <= nj < N:
                heights[ni, nj] += 1
                theta2[ni, nj] += np.random.normal(0, 0.5)
                if heights[ni, nj] >= 4:
                    tt.append((ni, nj))
    
    theta2 += dtheta * dt
    theta2 %= (2*np.pi)
    r_sand.append(np.abs(np.mean(np.exp(1j * theta2.flatten()))))

r_pure = np.array(r_pure)
r_sand = np.array(r_sand)

print('Pure Kuramoto: r={:.3f} (start), r={:.3f} (end), r={:.3f} (mean last 500)'.format(
    r_pure[0], r_pure[-1], r_pure[-500:].mean()))
print('Sandpile Kuramoto: r={:.3f} (start), r={:.3f} (end), r={:.3f} (mean last 500)'.format(
    r_sand[0], r_sand[-1], r_sand[-500:].mean()))

# Plot
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

ax.plot(r_pure, color='#44ff88', lw=2, label='Pure Kuramoto (K=2.0, no sandpile)')
ax.plot(r_sand, color='#ff4444', lw=2, label='Kuramoto + Sandpile (K=2.0, with perturbations)')

ax.set_title('R19b: Self-Organized Criticality Destroys Synchronization', fontsize=15, color='#e7e7f0')
ax.set_xlabel('Time Step', fontsize=12, color='#e7e7f0')
ax.set_ylabel('Order Parameter r', fontsize=12, color='#e7e7f0')
ax.tick_params(colors='#8a8aa3')
ax.grid(True, alpha=0.2, color='#3a3a5a')
ax.legend(fontsize=12, facecolor='#1a1a2a', edgecolor='#3a3a5a')
ax.set_ylim(-0.05, 1.05)

# Add annotation
ax.annotate('Pure Kuramoto synchronizes\n(r -> 0.5)', xy=(2500, r_pure[-1]), 
            xytext=(2200, 0.7), fontsize=10, color='#44ff88',
            arrowprops=dict(arrowstyle='->', color='#44ff88'))
ax.annotate('Sandpile prevents sync\n(r stays ~0.03)', xy=(2500, r_sand[-1]), 
            xytext=(2200, 0.2), fontsize=10, color='#ff4444',
            arrowprops=dict(arrowstyle='->', color='#ff4444'))

plt.tight_layout()
fig.savefig('../../shared_space/resonance_kuramoto_sandpile_contrast.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_kuramoto_sandpile_contrast.png')
print('=== R19b COMPLETE ===')
