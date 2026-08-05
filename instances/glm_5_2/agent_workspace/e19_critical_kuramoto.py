import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19: Kuramoto on Sandpile - Synchronization Meets Criticality ===')

# IDEA: Run Kuramoto oscillators on top of a sandpile grid.
# Each grid cell has a phase oscillator. When a cell topples, it injects a phase kick to neighbors.
# The oscillators' phases also couple through standard Kuramoto coupling.
# Question: Does the sandpile's self-organized criticality affect the synchronization transition?

N = 64  # grid size NxN
threshold = 4
dt = 0.05
K = 2.0  # Kuramoto coupling
steps = 3000

np.random.seed(42)
omega = np.random.normal(0, 1, (N, N))
theta = np.random.uniform(0, 2*np.pi, (N, N))
heights = np.random.randint(0, threshold, (N, N))

r_history = []
total_avalanches = []
phase_kicks = 0

for step in range(steps):
    # Kuramoto coupling on grid (4 neighbors)
    coupling = np.zeros_like(theta)
    for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
        rolled = np.roll(theta, (di, dj), axis=(0,1))
        coupling += np.sin(rolled - theta)
    dtheta = omega + (K/4) * coupling
    
    # Drop grain at random location
    gi, gj = np.random.randint(0, N, 2)
    heights[gi, gj] += 1
    
    # Sandpile toppling with phase kicks
    avalanche_size = 0
    to_topple = [(gi, gj)]
    toppled_cells = set()
    while to_topple:
        ci, cj = to_topple.pop()
        if (ci, cj) in toppled_cells:
            continue
        if heights[ci, cj] < threshold:
            continue
        toppled_cells.add((ci, cj))
        heights[ci, cj] -= threshold
        avalanche_size += 1
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = ci+di, cj+dj
            if 0 <= ni < N and 0 <= nj < N:
                heights[ni, nj] += 1
                # Phase kick: toppling nudges neighbor's phase
                theta[ni, nj] += np.random.normal(0, 0.5)
                if heights[ni, nj] >= threshold:
                    to_topple.append((ni, nj))
    
    if avalanche_size > 0:
        total_avalanches.append(avalanche_size)
        phase_kicks += avalanche_size
    
    # Update phases
    theta += dtheta * dt
    theta %= (2*np.pi)
    
    # Global order parameter
    r = np.abs(np.mean(np.exp(1j * theta.flatten())))
    r_history.append(r)

r_history = np.array(r_history)
total_avalanches = np.array(total_avalanches)

print('Total steps: {}'.format(steps))
print('Avalanches: {}, Max avalanche: {}'.format(len(total_avalanches), total_avalanches.max() if len(total_avalanches) > 0 else 0))
print('Phase kicks delivered: {}'.format(phase_kicks))
print('Order parameter: start={:.3f}, end={:.3f}, mean(last 500)={:.3f}'.format(
    r_history[0], r_history[-1], r_history[-500:].mean()))
print('r std (last 500): {:.4f}'.format(r_history[-500:].std()))

# Plot
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.patch.set_facecolor('#0a0a1a')

# 1. Order parameter over time
ax1 = axes[0, 0]
ax1.set_facecolor('#0a0a1a')
ax1.plot(r_history, color='#44ccff', lw=1)
ax1.axhline(y=r_history[-500:].mean(), color='#ff4444', ls='--', lw=2, label='Mean r={:.3f}'.format(r_history[-500:].mean()))
ax1.set_title('R19: Global Synchronization with Sandpile Perturbations', fontsize=13, color='#e7e7f0')
ax1.set_xlabel('Time Step', color='#e7e7f0')
ax1.set_ylabel('Order Parameter r', color='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.2, color='#3a3a5a')
ax1.legend(fontsize=10, facecolor='#1a1a2a', edgecolor='#3a3a5a')
ax1.set_ylim(-0.05, 1.05)

# 2. Avalanche size over time (overlay)
ax2 = axes[0, 1]
ax2.set_facecolor('#0a0a1a')
if len(total_avalanches) > 0:
    ax2.bar(range(len(total_avalanches)), total_avalanches, color='#ff8844', alpha=0.7)
ax2.set_title('R19: Avalanche Sizes Over Time', fontsize=13, color='#e7e7f0')
ax2.set_xlabel('Avalanche Event', color='#e7e7f0')
ax2.set_ylabel('Avalanche Size', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.2, color='#3a3a5a')

# 3. Phase heatmap (final state)
ax3 = axes[1, 0]
ax3.set_facecolor('#0a0a1a')
im = ax3.imshow(theta / (2*np.pi), cmap='twilight', interpolation='nearest')
ax3.set_title('R19: Final Phase Distribution', fontsize=13, color='#e7e7f0')
ax3.tick_params(colors='#8a8aa3')
plt.colorbar(im, ax=ax3, fraction=0.046, label='Phase / 2pi')

# 4. Sandpile heights (final state)
ax4 = axes[1, 1]
ax4.set_facecolor('#0a0a1a')
im2 = ax4.imshow(heights, cmap='hot', interpolation='nearest')
ax4.set_title('R19: Final Sandpile Heights', fontsize=13, color='#e7e7f0')
ax4.tick_params(colors='#8a8aa3')
plt.colorbar(im2, ax=ax4, fraction=0.046, label='Height')

plt.suptitle('R19: Kuramoto on Sandpile - When Synchronization Meets Self-Organized Criticality', 
             fontsize=15, color='#e7e7f0', y=1.02)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_kuramoto_sandpile.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_kuramoto_sandpile.png')
print('=== R19 COMPLETE ===')
