import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R13: Phase-Locking Visualization ===')

sigma, rho, beta = 10.0, 28.0, 8.0/3.0
dt = 0.005
steps = 8000

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.patch.set_facecolor('#0a0a1a')

coupling_list = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
colors_list = ['#ff4444', '#ff8844', '#ffcc44', '#44ff44', '#44ccff', '#8844ff']
all_dists = {}
for idx, cs in enumerate(coupling_list):
    x1, y1, z1 = 0.1, 0.0, 0.0
    x2, y2, z2 = 0.15, 0.01, 0.1
    traj1 = []
    traj2 = []
    dists = []
    for step in range(steps):
        dx1 = sigma*(y1-x1) + cs*(x2-x1)
        dy1 = x1*(rho-z1) - y1 + cs*(y2-y1)
        dz1 = x1*y1 - beta*z1 + cs*(z2-z1)
        dx2 = sigma*(y2-x2) + cs*(x1-x2)
        dy2 = x2*(rho-z2) - y2 + cs*(y1-y2)
        dz2 = x2*y2 - beta*z2 + cs*(z1-z2)
        x1 += dx1*dt; y1 += dy1*dt; z1 += dz1*dt
        x2 += dx2*dt; y2 += dy2*dt; z2 += dz2*dt
        traj1.append((x1,y1,z1))
        traj2.append((x2,y2,z2))
        dists.append(np.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2))
    t1 = np.array(traj1)
    t2 = np.array(traj2)
    all_dists[cs] = np.array(dists)
    ax = axes[idx//3, idx%3]
    ax.plot(t1[:,0], t1[:,2], lw=0.3, alpha=0.5, color='cyan', label='Sys1')
    ax.plot(t2[:,0], t2[:,2], lw=0.3, alpha=0.5, color='magenta', label='Sys2')
    mean_d = np.mean(dists[2000:])
    ax.set_title('cs={} (mean_dist={:.2f})'.format(cs, mean_d), fontsize=10, color='#e7e7f0')
    ax.set_facecolor('#0a0a1a')
    ax.tick_params(colors='#8a8aa3')
    if idx == 0:
        ax.legend(fontsize=7, facecolor='#1a1a2a', edgecolor='#3a3a5a')
plt.suptitle('R13: Phase-Locking Resonance - Two Coupled Lorenz Systems', fontsize=14, y=0.98, color='#e7e7f0')
plt.tight_layout()
fig.savefig('../../shared_space/resonance_phase_locking.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_phase_locking.png')

fig2, ax2 = plt.subplots(figsize=(14, 6))
fig2.patch.set_facecolor('#0a0a1a')
ax2.set_facecolor('#0a0a1a')
for idx, cs in enumerate(coupling_list):
    d = all_dists[cs]
    ax2.plot(d[::5], lw=0.5, alpha=0.7, color=colors_list[idx], label='cs={}'.format(cs))
ax2.set_xlabel('Step', color='#8a8aa3')
ax2.set_ylabel('Distance between systems', color='#e7e7f0')
ax2.set_title('Synchronization convergence vs coupling strength', fontsize=12, color='#e7e7f0')
ax2.legend(fontsize=9)
ax2.tick_params(colors='#8a8aa3')
fig2.savefig('../../shared_space/resonance_phase_locking_dist.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_phase_locking_dist.png')
print('=== R13 COMPLETE ===')
