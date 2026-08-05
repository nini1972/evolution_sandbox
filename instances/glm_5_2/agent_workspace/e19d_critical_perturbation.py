import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19d: Critical Perturbations vs Established Synchronization ===')

# All-to-all Kuramoto (synchronizes well), then inject SOC-style perturbations
# Question: Can self-organized critical noise destroy established synchrony?

N = 200
dt = 0.02
K = 3.0  # well above the critical coupling for N=200
steps = 8000
perturb_start = 4000  # start sandpile perturbations halfway through

np.random.seed(42)
omega = np.random.normal(0, 1, N)
theta = np.random.uniform(0, 2*np.pi, N)

# Sandpile for perturbation generation
gs = 32
heights = np.random.randint(0, 4, (gs, gs))

r_history = []
perturbation_sizes = []

for step in range(steps):
    # Kuramoto all-to-all
    r_current = np.abs(np.mean(np.exp(1j * theta)))
    coupling = (K / N) * np.sin(theta - np.angle(np.mean(np.exp(1j * theta))))
    dtheta = omega + coupling
    
    # Inject sandpile perturbations after perturb_start
    if step >= perturb_start:
        gi, gj = np.random.randint(0, gs, 2)
        heights[gi, gj] += 1
        tt = [(gi, gj)]
        av_size = 0
        perturbed_oscillators = []
        while tt:
            ci, cj = tt.pop()
            if heights[ci, cj] < 4:
                continue
            heights[ci, cj] -= 4
            av_size += 1
            # Map (ci,cj) to oscillator index
            osc_idx = (ci * gs + cj) % N
            perturbed_oscillators.append(osc_idx)
            for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni, nj = ci+di, cj+dj
                if 0 <= ni < gs and 0 <= nj < gs:
                    heights[ni, nj] += 1
                    if heights[ni, nj] >= 4:
                        tt.append((ni, nj))
        
        if av_size > 0:
            perturbation_sizes.append((step, av_size))
            # Apply phase kicks to perturbed oscillators
            for idx in perturbed_oscillators:
                theta[idx] += np.random.normal(0, 1.0)
    
    theta += dtheta * dt
    theta %= (2*np.pi)
    r_history.append(np.abs(np.mean(np.exp(1j * theta))))

r_history = np.array(r_history)

# Analysis
r_before = r_history[:perturb_start].mean()
r_after = r_history[perturb_start:].mean()
print('Before perturbations: r={:.3f}'.format(r_before))
print('After perturbations: r={:.3f}'.format(r_after))
print('Total perturbation events: {}'.format(len(perturbation_sizes)))
if perturbation_sizes:
    sizes = [s for _, s in perturbation_sizes]
    print('Max perturbation size: {}'.format(max(sizes)))

# Plot
fig, axes = plt.subplots(2, 1, figsize=(18, 10))
fig.patch.set_facecolor('#0a0a1a')

ax1 = axes[0]
ax1.set_facecolor('#0a0a1a')
ax1.plot(r_history, color='#44ccff', lw=1)
ax1.axvline(x=perturb_start, color='#ff4444', ls='--', lw=2, label='Sandpile perturbations begin')
ax1.axhline(y=r_before, color='#44ff88', ls=':', lw=1, alpha=0.7, label='r before={:.3f}'.format(r_before))
ax1.axhline(y=r_after, color='#ff8844', ls=':', lw=1, alpha=0.7, label='r after={:.3f}'.format(r_after))
ax1.set_title('R19d: Can Self-Organized Critical Perturbations Destroy Synchronization?', fontsize=14, color='#e7e7f0')
ax1.set_xlabel('Time Step', color='#e7e7f0')
ax1.set_ylabel('Order Parameter r', color='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.2, color='#3a3a5a')
ax1.legend(fontsize=11, facecolor='#1a1a2a', edgecolor='#3a3a5a')
ax1.set_ylim(-0.05, 1.05)

# Avalanche sizes over time
ax2 = axes[1]
ax2.set_facecolor('#0a0a1a')
if perturbation_sizes:
    steps_p, sizes_p = zip(*perturbation_sizes)
    ax2.bar(steps_p, sizes_p, color='#ff44ff', alpha=0.7, width=20)
ax2.axvline(x=perturb_start, color='#ff4444', ls='--', lw=2)
ax2.set_title('R19d: Sandpile Avalanche Sizes (Critical Perturbations)', fontsize=14, color='#e7e7f0')
ax2.set_xlabel('Time Step', color='#e7e7f0')
ax2.set_ylabel('Avalanche Size', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.2, color='#3a3a5a')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_critical_perturbation.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_critical_perturbation.png')
print('=== R19d COMPLETE ===')
