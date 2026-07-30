import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R11: Bidirectional Coupled Resonance ===')
print('Lorenz <-> Gray-Scott: true bidirectional coupling')
print()

W, Hh = 100, 100
Du, Dv = 0.16, 0.08

# Lorenz state
sigma, rho, beta = 10.0, 28.0, 8.0/3.0
x, y, z = 0.1, 0.0, 0.0
dt_l = 0.005

# Gray-Scott state
U = np.ones((Hh, W))
V = np.zeros((Hh, W))
cx, cy = W//2, Hh//2
V[cy-5:cy+5, cx-5:cx+5] = 0.5
U[cy-5:cy+5, cx-5:cx+5] = 0.5
V += np.random.rand(Hh, W) * 0.01

gs_steps_per_lorenz = 2
total_lorenz_steps = 4000

lorenz_hist = []
gs_snapshots = []
coupling_hist = []

print('Running bidirectional coupling for {} Lorenz steps...'.format(total_lorenz_steps))
for step in range(total_lorenz_steps):
    # === Lorenz -> Gray-Scott ===
    F_base = 0.020 + 0.010 * (x / 20.0 + 1)
    k_base = 0.055 + 0.010 * (z / 50.0)
    F_field = np.full((Hh, W), F_base)
    k_field = np.full((Hh, W), k_base)
    # Add spatial modulation from Lorenz y
    rows = np.arange(Hh)
    row_mod = 0.005 * np.sin(rows / 10.0 + y * 0.1)
    F_field += row_mod[:, np.newaxis]

    for gs_step in range(gs_steps_per_lorenz):
        lap_U = (np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U)
        lap_V = (np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V)
        uv2 = U*V*V
        U += Du*lap_U - uv2 + F_field*(1-U)
        V += Dv*lap_V + uv2 - k_field*V
        U = np.clip(U, 0, 1)
        V = np.clip(V, 0, 1)

    # === Gray-Scott -> Lorenz ===
    v_mean = V.mean()
    v_std = V.std()
    v_cx = V[:, cx].mean()
    # Forcing terms added to Lorenz equations
    force_x = (v_mean - 0.25) * 0.5
    force_y = (v_std - 0.08) * 2.0
    force_z = (v_cx - 0.1) * 1.0

    dx = sigma*(y-x) + force_x
    dy = x*(rho-z) - y + force_y
    dz = x*y - beta*z + force_z
    x += dx * dt_l
    y += dy * dt_l
    z += dz * dt_l

    lorenz_hist.append((x, y, z))
    coupling_hist.append((force_x, force_y, force_z))

    if step % 500 == 0:
        gs_snapshots.append(V.copy())
        print('  step {}: xyz=({:.2f},{:.2f},{:.2f}) v_mean={:.4f} v_std={:.4f}'.format(
            step, x, y, z, v_mean, v_std))
