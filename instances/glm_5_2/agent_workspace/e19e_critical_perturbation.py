import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19e: Critical Perturbations vs Synchronization (Tuned) ===')

N = 100
dt = 0.05
K = 4.0
steps = 10000
perturb_start = 5000

np.random.seed(42)
omega = np.random.normal(0, 0.5, N)  # narrower distribution -> easier to sync
theta = np.random.uniform(0, 2*np.pi, N)

# Sandpile
gs = 32
heights = np.random.randint(0, 4, (gs, gs))

r_history = []
perturbation_events = []

for step in range(steps):
    Z = np.mean(np.exp(1j * theta))
    r_current = np.abs(Z)
    psi = np.angle(Z)
    coupling = (K / N) * np.sin(psi - theta)
    
    # Inject perturbations
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
            for idx in perturbed:
                theta[idx] += np.random.normal(0, 1.5)
    
    theta += (omega + coupling) * dt
    theta %= (2*np.pi)
    r_history.append(np.abs(np.mean(np.exp(1j * theta))))

r_history = np.array(r_history)

# Windowed analysis
window = 200
r_before = r_history[max(0,perturb_start-window):perturb_start].mean()
r_after = r_history[perturb_start:perturb_start+window].mean()
r_after_late = r_history[-window:].mean()

print('r just before perturbations: {:.3f}'.format(r_before))
print('r just after perturbations start: {:.3f}'.format(r_after))
print('r at end: {:.3f}'.format(r_after_late))
print('Perturbation events: {}'.format(len(perturbation_events)))
if perturbation_events:
    sizes = [s for _, s in perturbation_events]
    print('Max avalanche: {}'.format(max(sizes)))

# Plot
fig, axes = plt.subplots(2, 1, figsize=(18, 10))
fig.patch.set_facecolor('#0a0a1a')

ax1 = axes[0]
ax1.set_facecolor('#0a0a1a')
# Smoothed
smooth = np.convolve(r_history, np.ones(50)/50, mode='valid')
ax1.plot(r_history, color='#44ccff', lw=0.5, alpha=0.4)
ax1.plot(range(25, 25+len(smooth)), smooth, color='#44ccff', lw=2)
ax1.axvline(x=perturb_start, color='#ff4444', ls='--', lw=2, label='Sandpile ON')
ax1.set_title('R19e: Synchronization Under Critical Perturbations (K=4, sigma=0.5)', fontsize=14, color='#e7e7f0')
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
ax2.set_title('Sandpile Avalanche Sizes', fontsize=14, color='#e7e7f0')
ax2.set_xlabel('Time Step', color='#e7e7f0')
ax2.set_ylabel('Avalanche Size', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.2, color='#3a3a5a')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_critical_perturbation2.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_critical_perturbation2.png')
print('=== R19e COMPLETE ===')
