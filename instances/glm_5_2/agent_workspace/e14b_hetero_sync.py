import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R14b: Heterogeneous Sync (careful coupling) ===')

sigma, rho, beta = 10.0, 28.0, 8.0/3.0
a_r, b_r, c_r = 0.2, 0.2, 5.7
dt = 0.005
steps = 15000

# Unidirectional coupling: Lorenz drives Rossler (master-slave)
# This is Pecara-Carroll style - replace one variable entirely
# Master = Lorenz, Slave = Rossler with x replaced by Lorenz x

# Test 1: Drive Rossler with Lorenz x (replace x)
print('\nTest 1: Lorenz x drives Rossler (x replacement)')
xl, yl, zl = 0.1, 0.0, 0.0
xr, yr, zr = 0.1, 0.0, 0.0
traj_l = []
traj_r = []
for step in range(steps):
    dxl = sigma*(yl-xl)
    dyl = xl*(rho-zl) - yl
    dzl = xl*yl - beta*zl
    xl += dxl*dt; yl += dyl*dt; zl += dzl*dt
    
    # Rossler slave: x is driven by Lorenz
    dyr = xl + a_r*yr  # use xl instead of xr
    dzr = b_r + zr*(xl - c_r)  # use xl instead of xr
    yr += dyr*dt; zr += dzr*dt
    # xr follows from Rossler dynamics: xr = -yr - zr (approximately)
    xr = xl  # forced synchronization
    
    traj_l.append((xl,yl,zl))
    traj_r.append((xl,yr,zr))
    if step == steps-1:
        print('  Lorenz final: ({:.2f},{:.2f},{:.2f})'.format(xl,yl,zl))
        print('  Rossler final: ({:.2f},{:.2f},{:.2f})'.format(xr,yr,zr))

# Test 2: Bidirectional with bounded coupling
print('\nTest 2: Bidirectional bounded coupling')
for cs in [0.0, 0.1, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]:
    xl, yl, zl = 0.1, 0.0, 0.0
    xr, yr, zr = 0.1, 0.0, 0.0
    dists = []
    for step in range(steps):
        dxl = sigma*(yl-xl) + cs*(xr-xl)
        dyl = xl*(rho-zl) - yl
        dzl = xl*yl - beta*zl
        dxr = -yr - zr + cs*(xl-xr)
        dyr = xr + a_r*yr
        dzr = b_r + zr*(xr - c_r)
        xl += dxl*dt; yl += dyl*dt; zl += dzl*dt
        xr += dxr*dt; yr += dyr*dt; zr += dzr*dt
        # Check for blowup
        if abs(xr) > 100 or abs(xl) > 100:
            print('  cs={:.1f}: BLOWUP at step {}'.format(cs, step))
            dists.append(np.nan)
            break
        dists.append(abs(xl-xr))
    if len(dists) == steps:
        md = np.mean(dists[3000:])
        print('  cs={:.1f}: mean |xl-xr| = {:.4f}'.format(cs, md))
