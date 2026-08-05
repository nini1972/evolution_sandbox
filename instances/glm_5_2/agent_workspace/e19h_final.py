import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19h: Final - Critical Perturbations vs Established Synchronization ===')

N = 100
dt = 0.01
K = 4.0
steps = 20000
perturb_start = 10000

np.random.seed(42)
omega = np.random.normal(0, 0.5, N)
theta = np.random.uniform(0, 2*np.pi, N)

# Sandpile for perturbation generation
gs = 32
heights = np.random.randint(0, 4, (gs, gs))

r_history = []
perturbation_events = []

for step in range(steps):
    # Full pairwise Kuramoto
    diff = theta[np.newaxis, :] - theta[:, np.newaxis]
    coupling = (K / N) * np.sin(diff).sum(axis=1)
    
    # Inject sandpile perturbations after perturb_start
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
            perturbation_events.append((step, av_size))
            for idx in set(perturbed):
                theta[idx] += np.random.normal(0, 2.0)
    
    theta += (omega + coupling) * dt
    theta %= (2*np.pi)
    r_history.append(np.abs(np.mean(np.exp(1j * theta))))

r_history = np.array(r_history)

# Analysis
r_before = r_history[max(0,perturb_start-500):perturb_start].mean()
r_after_early = r_history[perturb_start:perturb_start+500].mean()
r_after_late = r_history[-500:].mean()

print('r before perturbations: {:.4f}'.format(r_before))
print('r just after perturbations start: {:.4f}'.format(r_after_early))
print('r at end: {:.4f}'.format(r_after_late))
print('Perturbation events: {}'.format(len(perturbation_events)))
if perturbation_events:
    sizes = [s for _, s in perturbation_events]
    print('Max avalanche: {}'.format(max(sizes)))
    print('Mean avalanche: {:.1f}'.format(np.mean(sizes)))

# Plot
fig, axes = plt.subplots(2, 1, figsize=(18, 10))
fig.patch.set_facecolor('#0a0a1a')

ax1 = axes[0]
ax1.set_facecolor('#0a0a1a')
ax1.plot(r_history, color='#44ccff', lw=1)
# Smoothed
smooth = np.convolve(r_history, np.ones(100)/100, mode='valid')
ax1.plot(range(50, 50+len(smooth)), smooth, color='#ffffff', lw=2.5, label='Smoothed')
ax1.axvline(x=perturb_start, color='#ff4444', ls='--', lw=2, label='Sandpile ON (t={})'.format(perturb_start))
ax1.axhline(y=r_before, color='#44ff88', ls=':', lw=1.5, alpha=0.7, label='r before={:.3f}'.format(r_before))
ax1.axhline(y=r_after_late, color='#ff8844', ls=':', lw=1.5, alpha=0.7, label='r after={:.3f}'.format(r_after_late))
ax1.set_title('R19h: Self-Organized Critical Perturbations vs Established Synchronization', fontsize=14, color='#e7e7f0')
ax1.set_xlabel('Time Step', color='#e7e7f0')
ax1.set_ylabel('Order Parameter r', color='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.2, color='#3a3a5a')
ax1.legend(fontsize=11, facecolor='#1a1a2a', edgecolor='#3a3a5a')
ax1.set_ylim(-0.05, 1.05)

ax2 = axes[1]
ax2.set_facecolor('#0a0a1a')
if perturbation_events:
    steps_p, sizes_p = zip(*perturbation_events)
    ax2.bar(steps_p, sizes_p, color='#ff44ff', alpha=0.7, width=30)
ax2.axvline(x=perturb_start, color='#ff4444', ls='--', lw=2)
ax2.set_title('Sandpile Avalanche Sizes (Power-Law Perturbations)', fontsize=14, color='#e7e7f0')
ax2.set_xlabel('Time Step', color='#e7e7f0')
ax2.set_ylabel('Avalanche Size', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.2, color='#3a3a5a')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_critical_vs_sync.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_critical_vs_sync.png')
print('=== R19h COMPLETE ===')
