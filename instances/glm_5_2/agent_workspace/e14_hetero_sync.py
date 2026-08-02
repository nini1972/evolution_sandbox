import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R14: Heterogeneous Synchronization ===')
print('Can a Lorenz system synchronize with a Rossler system?')

# Lorenz: sigma=10, rho=28, beta=8/3
# Rossler: a=0.2, b=0.2, c=5.7
dt = 0.01
steps = 10000

# Different dimensionalities: Lorenz is 3D, Rossler is 3D but different dynamics
# We couple through x-coordinate only (Pecora-Carroll style)

sigma, rho, beta = 10.0, 28.0, 8.0/3.0
a_r, b_r, c_r = 0.2, 0.2, 5.7

results = {}
for cs in [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]:
    # Lorenz
    xl, yl, zl = 0.1, 0.0, 0.0
    # Rossler
    xr, yr, zr = 0.1, 0.0, 0.0
    
    traj_l = []
    traj_r = []
    dists = []
    
    for step in range(steps):
        # Lorenz with coupling from Rossler x
        dxl = sigma*(yl-xl) + cs*(xr-xl)
        dyl = xl*(rho-zl) - yl
        dzl = xl*yl - beta*zl
        
        # Rossler with coupling from Lorenz x
        dxr = -yr - zr + cs*(xl-xr)
        dyr = xr + a_r*yr
        dzr = b_r + zr*(xr - c_r)
        
        xl += dxl*dt; yl += dyl*dt; zl += dzl*dt
        xr += dxr*dt; yr += dyr*dt; zr += dzr*dt
        traj_l.append((xl,yl,zl))
        traj_r.append((xr,yr,zr))
        dists.append(abs(xl-xr))
    
    md = np.mean(dists[3000:])
    results[cs] = (np.array(traj_l), np.array(traj_r), np.array(dists), md)
    print('  cs={:.1f}: mean |xl-xr| = {:.4f}'.format(cs, md))
