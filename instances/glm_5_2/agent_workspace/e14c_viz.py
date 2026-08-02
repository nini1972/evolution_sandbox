import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Two Lorenz systems with different rho values, bidirectionally coupled
# Testing generalized synchronization

sigma_a, rho_a, beta_a = 10.0, 28.0, 8.0/3.0
sigma_b, rho_b, beta_b = 10.0, 35.0, 8.0/3.0
dt = 0.005
steps = 15000

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.patch.set_facecolor('#0a0a1a')

cs_list = [0.0, 2.0, 5.0, 8.0, 12.0, 20.0]
all_direct = []
all_continuity = []

for idx, cs in enumerate(cs_list):
    xa, ya, za = 0.1, 0.0, 0.0
    xb, yb, zb = 0.2, 0.1, 0.05
    traj_a = []
    traj_b = []
    for step in range(steps):
        dxa = sigma_a*(ya-xa) + cs*(xb-xa)
        dya = xa*(rho_a-za) - ya
        dza = xa*ya - beta_a*za
        dxb = sigma_b*(yb-xb) + cs*(xa-xb)
        dyb = xb*(rho_b-zb) - yb
        dzb = xb*yb - beta_b*zb
        xa += dxa*dt; ya += dya*dt; za += dza*dt
        xb += dxb*dt; yb += dyb*dt; zb += dzb*dt
        traj_a.append((xa,ya,za))
        traj_b.append((xb,yb,zb))
    ta = np.array(traj_a)
    tb = np.array(traj_b)
    
    ax = axes[idx//3, idx%3]
    ax.plot(ta[3000:,0], ta[3000:,2], lw=0.3, alpha=0.5, color='cyan', label='SysA (rho=28)')
    ax.plot(tb[3000:,0], tb[3000:,2], lw=0.3, alpha=0.5, color='magenta', label='SysB (rho=35)')
    dd = np.mean(np.abs(ta[3000:,0] - tb[3000:,0]))
    ax.set_title('cs={} (|xa-xb|={:.2f})'.format(cs, dd), fontsize=10, color='#e7e7f0')
    ax.set_facecolor('#0a0a1a')
    ax.tick_params(colors='#8a8aa3')
    if idx == 0:
        ax.legend(fontsize=7, facecolor='#1a1a2a', edgecolor='#3a3a5a')

plt.suptitle('R14: Generalized Sync - Coupled Lorenz Systems (different rho)', fontsize=14, y=0.98, color='#e7e7f0')
plt.tight_layout()
fig.savefig('../../shared_space/resonance_hetero_sync.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_hetero_sync.png')
