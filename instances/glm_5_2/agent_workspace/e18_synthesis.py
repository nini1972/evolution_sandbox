import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R18: Master Synthesis - The Phase Transition Spectrum ===')

fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor('#0a0a1a')

# ---- Panel 1: R13 - Two identical Lorenz systems (sharp sync) ----
np.random.seed(42)
def lorenz_step(state, dt=0.01, sigma=10, rho=28, beta=8/3):
    x, y, z = state
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return np.array([x + dx*dt, y + dy*dt, z + dz*dt])

cs_vals = [0.45, 0.50, 0.51, 0.52, 0.55]
dist_data = []
for cs in cs_vals:
    s1 = np.array([1.0, 1.0, 1.0])
    s2 = np.array([1.001, 1.001, 1.001])
    dists = []
    for step in range(3000):
        f1 = lorenz_step(s1)
        f2 = lorenz_step(s2)
        s1 = f1 + cs*(f2 - f1)*0.01
        s2 = f2 + cs*(f1 - f2)*0.01
        d = np.linalg.norm(s1 - s2)
        dists.append(d)
    dist_data.append(np.mean(dists[-500:]))

ax1 = fig.add_subplot(2, 3, 1)
ax1.set_facecolor('#0a0a1a')
ax1.semilogy(cs_vals, dist_data, 'o-', color='#ff4444', lw=2, markersize=8)
ax1.set_title('R13: Identical Pair\n(Sharp Transition)', fontsize=11, color='#e7e7f0')
ax1.set_xlabel('Coupling cs', color='#e7e7f0')
ax1.set_ylabel('Mean Distance', color='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
ax1.grid(True, alpha=0.2, color='#3a3a5a')

# ---- Panel 2: R14 - Heterogeneous Lorenz (gradual sync) ----
cs_vals2 = [0, 1, 2, 5, 10, 20]
dist_data2 = []
for cs in cs_vals2:
    s1 = np.array([1.0, 1.0, 1.0])
    s2 = np.array([1.001, 1.001, 1.001])
    dists = []
    for step in range(2000):
        f1 = lorenz_step(s1, rho=28)
        f2 = lorenz_step(s2, rho=35)
        s1 = f1 + cs*(f2 - f1)*0.01
        s2 = f2 + cs*(f1 - f2)*0.01
        d = np.linalg.norm(s1 - s2)
        dists.append(d)
    dist_data2.append(np.mean(dists[-500:]))

ax2 = fig.add_subplot(2, 3, 2)
ax2.set_facecolor('#0a0a1a')
ax2.plot(cs_vals2, dist_data2, 's-', color='#44ff88', lw=2, markersize=8)
ax2.set_title('R14: Heterogeneous Pair\n(Gradual Transition)', fontsize=11, color='#e7e7f0')
ax2.set_xlabel('Coupling cs', color='#e7e7f0')
ax2.set_ylabel('Mean Distance', color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.2, color='#3a3a5a')

# ---- Panel 3: R15 - Kuramoto (smooth collective sync) ----
N = 50
omega = np.random.normal(0, 1, N)
K_vals = np.arange(0.0, 3.0, 0.15)
r_vals = []
for K in K_vals:
    theta = np.random.uniform(0, 2*np.pi, N)
    rs = []
    for step in range(1000):
        diff = theta[np.newaxis, :] - theta[:, np.newaxis]
        coupling = (K/N) * np.sin(diff).sum(axis=1)
        theta += (omega + coupling) * 0.05
        theta %= (2*np.pi)
        if step >= 500:
            rs.append(np.abs(np.mean(np.exp(1j*theta))))
    r_vals.append(np.mean(rs))

ax3 = fig.add_subplot(2, 3, 3)
ax3.set_facecolor('#0a0a1a')
ax3.plot(K_vals, r_vals, 'D-', color='#44ccff', lw=2, markersize=6)
ax3.set_title('R15: Kuramoto Network\n(Smooth Collective)', fontsize=11, color='#e7e7f0')
ax3.set_xlabel('Coupling K', color='#e7e7f0')
ax3.set_ylabel('Order Parameter r', color='#e7e7f0')
ax3.tick_params(colors='#8a8aa3')
ax3.grid(True, alpha=0.2, color='#3a3a5a')
ax3.set_ylim(-0.05, 1.05)

# ---- Panel 4: R16 - Chimera state (local order parameter) ----
# Simplified chimera reproduction
N_ch = 128
sigma_ch = 0.2
alpha_ch = np.pi/2 - 0.15
cm = np.zeros((N_ch, N_ch))
for i in range(N_ch):
    for j in range(N_ch):
        if i != j:
            dist = min(abs(i-j), N_ch-abs(i-j)) / N_ch
            cm[i,j] = np.exp(-dist/sigma_ch) * np.sin(alpha_ch)
cm = cm / (N_ch * cm.sum(axis=1, keepdims=True) + 1e-10)

theta = np.zeros(N_ch)
theta[:N_ch//2] = np.linspace(0, 2*np.pi, N_ch//2)
theta[N_ch//2:] = np.random.uniform(0, 2*np.pi, N_ch//2)

for step in range(2000):
    diff = theta[np.newaxis, :] - theta[:, np.newaxis]
    coupling = (cm * np.sin(diff)).sum(axis=1)
    theta += coupling * 0.02
    theta %= (2*np.pi)

# Local order parameter
window = 10
r_local = np.zeros(N_ch)
for i in range(N_ch):
    idx = [(i + k) % N_ch for k in range(-window//2, window//2)]
    r_local[i] = np.abs(np.mean(np.exp(1j*theta[idx])))

ax4 = fig.add_subplot(2, 3, 4)
ax4.set_facecolor('#0a0a1a')
ax4.plot(r_local, color='#ff8844', lw=2)
ax4.fill_between(range(N_ch), 0, r_local, alpha=0.3, color='#ff8844')
ax4.set_title('R16: Chimera State\n(Coherent + Incoherent)', fontsize=11, color='#e7e7f0')
ax4.set_xlabel('Oscillator Index', color='#e7e7f0')
ax4.set_ylabel('Local Order r', color='#e7e7f0')
ax4.tick_params(colors='#8a8aa3')
ax4.grid(True, alpha=0.2, color='#3a3a5a')
ax4.set_ylim(-0.05, 1.05)

# ---- Panel 5: R17 - Sandpile avalanche distribution ----
gs = 32
grid = np.random.randint(0, 4, (gs, gs))
av_sizes = []
for g in range(8000):
    i, j = np.random.randint(0, gs, 2)
    grid[i,j] += 1
    av = 0
    tt = [(i,j)]
    while tt:
        ci, cj = tt.pop()
        if grid[ci,cj] < 4:
            continue
        grid[ci,cj] -= 4
        av += 1
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = ci+di, cj+dj
            if 0 <= ni < gs and 0 <= nj < gs:
                grid[ni,nj] += 1
                if grid[ni,nj] >= 4:
                    tt.append((ni,nj))
    if av > 0:
        av_sizes.append(av)

av_sizes = np.array(av_sizes)
ax5 = fig.add_subplot(2, 3, 5)
ax5.set_facecolor('#0a0a1a')
bins = np.logspace(0, np.log10(av_sizes.max()+1), 15)
hist, edges = np.histogram(av_sizes, bins=bins)
centers = np.sqrt(edges[:-1] * edges[1:])
mask = hist > 0
ax5.scatter(centers[mask], hist[mask], c='#ff44ff', s=25)
ax5.set_xscale('log')
ax5.set_yscale('log')
ax5.set_title('R17: Sandpile Avalanches\n(Power Law - SOC)', fontsize=11, color='#e7e7f0')
ax5.set_xlabel('Avalanche Size', color='#e7e7f0')
ax5.set_ylabel('Frequency', color='#e7e7f0')
ax5.tick_params(colors='#8a8aa3')
ax5.grid(True, alpha=0.2, color='#3a3a5a')

# ---- Panel 6: Summary conceptual map ----
ax6 = fig.add_subplot(2, 3, 6)
ax6.set_facecolor('#0a0a1a')
ax6.set_xlim(0, 10)
ax6.set_ylim(0, 10)
ax6.axis('off')
ax6.set_title('Synthesis: The Criticality Spectrum', fontsize=13, color='#e7e7f0')

summary = [
    ("SHARP (1st order)", "R13: 2 identical Lorenz", "#ff4444", 8.5),
    ("GRADUAL", "R14: 2 different Lorenz", "#44ff88", 7.0),
    ("SMOOTH (2nd order)", "R15: N Kuramoto", "#44ccff", 5.5),
    ("BROKEN SYMMETRY", "R16: Chimera state", "#ff8844", 4.0),
    ("SELF-TUNING", "R17: Sandpile SOC", "#ff44ff", 2.5),
    ("MUTUAL CO-EVOLUTION", "R11: Lorenz <-> GS", "#ffff44", 1.0),
]
for label, desc, color, y in summary:
    ax6.text(0.5, y+0.5, label, fontsize=10, color=color, fontweight='bold')
    ax6.text(0.5, y-0.1, desc, fontsize=9, color='#8a8aa3')
    ax6.plot([0.3, 9.7], [y, y], color=color, alpha=0.3, lw=1)

plt.suptitle('R18: The Phase Transition Spectrum - From Sharp Synchronization to Self-Organized Criticality', 
             fontsize=16, color='#e7e7f0', y=1.02)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_synthesis.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_synthesis.png')
print('=== R18 COMPLETE ===')
