"""Hénon-Heiles Phase 2 only: Poincaré sections - very fast."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

def hh(t, s):
    x, y, px, py = s
    return [px, py, -x - 2*x*y, -y - x**2 + y**2]

def V(x, y):
    return 0.5*(x**2 + y**2) + x**2*y - y**3/3.0

Energies = [1/12, 1/8, 1/6, 0.15, 0.18]

fig = plt.figure(figsize=(20, 12))
for idx, E in enumerate(Energies):
    ax = fig.add_subplot(2, 3, idx+1)
    n_ic = 8
    colors = plt.cm.Spectral(np.linspace(0, 1, n_ic))
    
    for j in range(n_ic):
        y0 = np.random.uniform(-0.4, 0.4)
        py0 = np.random.uniform(-0.4, 0.4)
        px2 = 2*E - 2*V(0, y0) - py0**2
        if px2 < 0: continue
        px0 = np.sqrt(px2)
        
        sol = solve_ivp(hh, [0, 300], [0, y0, px0, py0], 
                       method='DOP853', rtol=1e-9, atol=1e-11, max_step=0.05)
        
        if sol.success:
            x_t = sol.y[0]
            px_t = sol.y[2]
            cy, cpy = [], []
            for k in range(len(x_t)-1):
                if x_t[k]*x_t[k+1] < 0 and px_t[k] > 0:
                    a = x_t[k]/(x_t[k]-x_t[k+1])
                    cy.append(sol.y[1,k]+a*(sol.y[1,k+1]-sol.y[1,k]))
                    cpy.append(sol.y[3,k]+a*(sol.y[3,k+1]-sol.y[3,k]))
            if len(cy) > 3:
                ax.scatter(cy, cpy, s=0.5, c=[colors[j]], alpha=0.5, rasterized=True)
    
    ax.set_xlim(-0.7, 0.7); ax.set_ylim(-0.7, 0.7)
    ax.set_xlabel('y'); ax.set_ylabel('p_y')
    regimes = {1/12:'Regular', 1/8:'Mostly regular', 1/6:'Escape threshold', 0.15:'Mixed', 0.18:'Chaotic/Escape'}
    ax.set_title(f'E={E:.4f} ({regimes.get(E, "")})', fontsize=11, fontweight='bold')
    ax.set_aspect('equal')

fig.suptitle('Hénon-Heiles: Poincaré Sections (x=0, px>0)', fontsize=16, fontweight='bold')
plt.savefig('henon_heiles_poincare.png', dpi=150, bbox_inches='tight')
print('Saved poincare')
