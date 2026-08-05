import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19c: Higher Coupling Contrast ===')

N = 64
dt = 0.05
steps = 3000

np.random.seed(42)
omega = np.random.normal(0, 1, (N, N))
theta_init = np.random.uniform(0, 2*np.pi, (N, N))

K_values = [5.0, 10.0, 20.0]
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
fig.patch.set_facecolor('#0a0a1a')

for idx, K in enumerate(K_values):
    # Pure
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
    
    # Sandpile
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
    
    print('K={:.1f}: Pure r={:.3f}, Sand r={:.3f}'.format(
        K, r_pure[-500:].mean(), r_sand[-500:].mean()))
    
    ax = axes[idx]
    ax.set_facecolor('#0a0a1a')
    ax.plot(r_pure, color='#44ff88', lw=2, label='Pure Kuramoto')
    ax.plot(r_sand, color='#ff4444', lw=2, label='Kuramoto + Sandpile')
    ax.set_title('K = {:.1f}'.format(K), fontsize=13, color='#e7e7f0')
    ax.set_xlabel('Time', color='#e7e7f0')
    ax.set_ylabel('r', color='#e7e7f0')
    ax.tick_params(colors='#8a8aa3')
    ax.grid(True, alpha=0.2, color='#3a3a5a')
    ax.legend(fontsize=10, facecolor='#1a1a2a', edgecolor='#3a3a5a')
    ax.set_ylim(-0.05, 1.05)

plt.suptitle('R19c: Synchronization Resistance Under Sandpile Perturbations (Various K)', 
             fontsize=14, color='#e7e7f0', y=1.02)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_kuramoto_sandpile_Kscan.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_kuramoto_sandpile_Kscan.png')
print('=== R19c COMPLETE ===')
