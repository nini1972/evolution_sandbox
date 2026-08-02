import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R14c: Generalized Synchronization ===')
print('Testing if a functional relationship emerges between coupled systems')

# Two different Lorenz parameter sets
# System A: standard Lorenz (sigma=10, rho=28, beta=8/3)
# System B: different rho (rho=35) - different attractor topology
dt = 0.005
steps = 20000

sigma_a, rho_a, beta_a = 10.0, 28.0, 8.0/3.0
sigma_b, rho_b, beta_b = 10.0, 35.0, 8.0/3.0  # different rho = different attractor

cs_values = [0.0, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0]
results = {}

for cs in cs_values:
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
    # Check direct synchronization
    direct_dist = np.mean(np.abs(ta[3000:,0] - tb[3000:,0]))
    # Check if there is a simple functional relationship
    # Try to fit xb = f(xa) using nearest-neighbor approach
    # If generalized sync exists, nearby xa values should map to nearby xb values
    xa_late = ta[3000:, 0]
    xb_late = tb[3000:, 0]
    # For each point, find nearest neighbor in xa and check if xb is also close
    n_check = min(500, len(xa_late))
    indices = np.random.choice(len(xa_late), n_check, replace=False)
    continuity_errors = []
    for i in indices:
        diffs = np.abs(xa_late - xa_late[i])
        diffs[i] = 1e10  # exclude self
        nn_idx = np.argmin(diffs)
        continuity_errors.append(np.abs(xb_late[i] - xb_late[nn_idx]))
    mean_ce = np.mean(continuity_errors)
    results[cs] = (ta, tb, direct_dist, mean_ce)
    print('  cs={}: direct_dist={:.4f}, continuity_error={:.4f}'.format(cs, direct_dist, mean_ce))
