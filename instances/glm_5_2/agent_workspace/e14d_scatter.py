import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Check if xb = f(xa) functional relationship exists at high coupling
sigma_a, rho_a, beta_a = 10.0, 28.0, 8.0/3.0
sigma_b, rho_b, beta_b = 10.0, 35.0, 8.0/3.0
dt = 0.005
steps = 20000

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.patch.set_facecolor('#0a0a1a')

for idx, cs in enumerate([0.0, 5.0, 20.0]):
    xa, ya, za = 0.1, 0.0, 0.0
    xb, yb, zb = 0.2, 0.1, 0.05
    xa_list = []
    xb_list = []
    for step in range(steps):
        dxa = sigma_a*(ya-xa) + cs*(xb-xa)
        dya = xa*(rho_a-za) - ya
        dza = xa*ya - beta_a*za
        dxb = sigma_b*(yb-xb) + cs*(xa-xb)
        dyb = xb*(rho_b-zb) - yb
        dzb = xb*yb - beta_b*zb
        xa += dxa*dt; ya += dya*dt; za += dza*dt
        xb += dxb*dt; yb += dyb*dt; zb += dzb*dt
        xa_list.append(xa)
        xb_list.append(xb)
    xa_arr = np.array(xa_list[5000:])
    xb_arr = np.array(xb_list[5000:])
    
    ax = axes[idx]
    ax.scatter(xa_arr[::3], xb_arr[::3], s=0.3, alpha=0.3, c='#44ccff')
    ax.set_xlabel('xa', color='#e7e7f0')
    ax.set_ylabel('xb', color='#e7e7f0')
    ax.set_title('cs={} - {} sync'.format(cs, 'No' if cs==0 else 'Partial' if cs==5 else 'Strong'), color='#e7e7f0')
    ax.set_facecolor('#0a0a1a')
    ax.tick_params(colors='#8a8aa3')
    # Add y=x line
    lim = max(abs(xa_arr).max(), abs(xb_arr).max())
    ax.plot([-lim,lim], [-lim,lim], 'r--', alpha=0.5, lw=1)

plt.suptitle('R14: Functional Relationship xa -> xb (Generalized Sync Test)', fontsize=14, color='#e7e7f0')
plt.tight_layout()
fig.savefig('../../shared_space/resonance_generalized_sync_scatter.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_generalized_sync_scatter.png')
print('=== R14 COMPLETE ===')
