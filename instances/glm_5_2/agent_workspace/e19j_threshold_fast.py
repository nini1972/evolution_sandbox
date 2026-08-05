import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19j: Resilience Threshold (Optimized) ===')

N = 50
dt = 0.02
steps = 6000
perturb_start = 3000

K_values = [4, 8, 16, 32, 64, 128, 256]
results = []

for K in K_values:
    np.random.seed(42)
    omega = np.random.normal(0, 0.5, N)
    theta = np.random.uniform(0, 2*np.pi, N)
    
    gs = 16
    heights = np.random.randint(0, 4, (gs, gs))
    
    r_before_vals = []
    r_after_vals = []
    
    for step in range(steps):
        # Optimized: use mean field approximation (valid for all-to-all)
        Z = np.mean(np.exp(1j * theta))
        psi = np.angle(Z)
        r_curr = np.abs(Z)
        # Correct mean-field coupling: (K/N)*sum_j sin(theta_j - theta_i) = K * r * sin(psi - theta_i)
        coupling = K * r_curr * np.sin(psi - theta)
        
        if step >= perturb_start:
            gi, gj = np.random.randint(0, gs, 2)
            heights[gi, gj] += 1
            tt = [(gi, gj)]
            av_size = 0
            perturbed = []
            while tt:
                ci, cj = tt.pop()
                if heights[ci, cj] < 4:
                    continue
                heights[ci, cj] -= 4
                av_size += 1
                osc_idx = (ci * gs + cj) % N
                perturbed.append(osc_idx)
                for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ni, nj = ci+di, cj+dj
                    if 0 <= ni < gs and 0 <= nj < gs:
                        heights[ni, nj] += 1
                        if heights[ni, nj] >= 4:
                            tt.append((ni, nj))
            if av_size > 0:
                for idx in set(perturbed):
                    theta[idx] += np.random.normal(0, 2.0)
        
        theta += (omega + coupling) * dt
        theta %= (2*np.pi)
        r = np.abs(np.mean(np.exp(1j * theta)))
        
        if perturb_start - 300 <= step < perturb_start:
            r_before_vals.append(r)
        if step >= steps - 300:
            r_after_vals.append(r)
    
    r_before = np.mean(r_before_vals)
    r_after = np.mean(r_after_vals)
    results.append((K, r_before, r_after))
    print('K={:4d}: r_before={:.4f}, r_after={:.4f}'.format(K, r_before, r_after))

# Plot
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

Ks = [r[0] for r in results]
r_befores = [r[1] for r in results]
r_afters = [r[2] for r in results]

ax.plot(Ks, r_befores, 'o-', color='#44ff88', lw=2, markersize=10, label='Before sandpile (synchronized)')
ax.plot(Ks, r_afters, 's-', color='#ff4444', lw=2, markersize=10, label='After sandpile (perturbed)')
ax.fill_between(Ks, r_befores, r_afters, alpha=0.15, color='#ff4444', label='Sync gap (desynchronization)')
ax.set_title('R19j: Resilience of Synchronization vs Self-Organized Critical Perturbations', fontsize=14, color='#e7e7f0')
ax.set_xlabel('Coupling Strength K (log scale)', fontsize=12, color='#e7e7f0')
ax.set_ylabel('Order Parameter r', fontsize=12, color='#e7e7f0')
ax.tick_params(colors='#8a8aa3')
ax.grid(True, alpha=0.2, color='#3a3a5a')
ax.legend(fontsize=11, facecolor='#1a1a2a', edgecolor='#3a3a5a')
ax.set_xscale('log')
ax.set_ylim(-0.05, 1.05)

plt.tight_layout()
fig.savefig('../../shared_space/resonance_resilience_threshold.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_resilience_threshold.png')
print('=== R19j COMPLETE ===')
