import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19i: Finding the Resilience Threshold ===')

N = 100
dt = 0.01
steps = 20000
perturb_start = 10000

K_values = [4, 8, 16, 32, 64, 128, 256]
results = []

for K in K_values:
    np.random.seed(42)
    omega = np.random.normal(0, 0.5, N)
    theta = np.random.uniform(0, 2*np.pi, N)
    
    gs = 32
    heights = np.random.randint(0, 4, (gs, gs))
    
    r_before_vals = []
    r_after_vals = []
    
    for step in range(steps):
        diff = theta[np.newaxis, :] - theta[:, np.newaxis]
        coupling = (K / N) * np.sin(diff).sum(axis=1)
        
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
        
        if perturb_start - 500 <= step < perturb_start:
            r_before_vals.append(r)
        if step >= steps - 500:
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
ax.set_title('R19i: Synchronization Resilience vs Self-Organized Critical Perturbations', fontsize=14, color='#e7e7f0')
ax.set_xlabel('Coupling Strength K', fontsize=12, color='#e7e7f0')
ax.set_ylabel('Order Parameter r', fontsize=12, color='#e7e7f0')
ax.tick_params(colors='#8a8aa3')
ax.grid(True, alpha=0.2, color='#3a3a5a')
ax.legend(fontsize=12, facecolor='#1a1a2a', edgecolor='#3a3a5a')
ax.set_xscale('log')
ax.set_ylim(-0.05, 1.05)

# Add annotation for the transition
for i in range(len(Ks)-1):
    if r_afters[i] < 0.5 and r_afters[i+1] >= 0.5:
        ax.annotate('Resilience\nthreshold', xy=(Ks[i+1], r_afters[i+1]),
                    xytext=(Ks[i+1]*0.3, 0.7), fontsize=11, color='#ffff44',
                    arrowprops=dict(arrowstyle='->', color='#ffff44'))

plt.tight_layout()
fig.savefig('../../shared_space/resonance_resilience_threshold.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_resilience_threshold.png')
print('=== R19i COMPLETE ===')
