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
print()
print('=== Visualization ===')

lorenz_arr = np.array(lorenz_hist)
coupling_arr = np.array(coupling_hist)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))

# Lorenz XY
axes[0,0].plot(lorenz_arr[:,0], lorenz_arr[:,1], lw=0.2, alpha=0.6, color='cyan')
axes[0,0].set_title('Lorenz XY (with GS forcing)', fontsize=11)
axes[0,0].set_facecolor('#0a0a1a')

# Lorenz XZ
axes[0,1].plot(lorenz_arr[:,0], lorenz_arr[:,2], lw=0.2, alpha=0.6, color='magenta')
axes[0,1].set_title('Lorenz XZ (with GS forcing)', fontsize=11)
axes[0,1].set_facecolor('#0a0a1a')

# Coupling forces over time
axes[0,2].plot(coupling_arr[:,0], label='force_x', lw=0.3, alpha=0.7, color='red')
axes[0,2].plot(coupling_arr[:,1], label='force_y', lw=0.3, alpha=0.7, color='green')
axes[0,2].plot(coupling_arr[:,2], label='force_z', lw=0.3, alpha=0.7, color='blue')
axes[0,2].set_title('GS -> Lorenz forcing terms', fontsize=11)
axes[0,2].legend(fontsize=8)
axes[0,2].set_facecolor('#0a0a1a')

# GS snapshots
for i, snap_idx in enumerate([1, 2]):
    if i < 2 and snap_idx < len(gs_snapshots):
        axes[1,i].imshow(gs_snapshots[snap_idx], cmap='magma', origin='lower')
        axes[1,i].set_title('GS V-field snapshot {}'.format(snap_idx), fontsize=11)

# Final GS state
axes[1,2].imshow(V, cmap='magma', origin='lower')
axes[1,2].set_title('GS V-field final', fontsize=11)

plt.suptitle('R11: Bidirectional Coupled Resonance - Lorenz <-> Gray-Scott', fontsize=14, y=0.98)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_bidirectional_coupled.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_bidirectional_coupled.png')
print('=== R11 COMPLETE ===')
