import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

print('=== R12: Resonance Network ===')
print('Three bidirectionally coupled systems forming a network:')
print('  Lorenz <-> Gray-Scott <-> Rule30')
print('Each pair is coupled bidirectionally.')
print()

# System parameters
W, Hh = 80, 80
Du, Dv = 0.16, 0.08

# Lorenz
sigma, rho, beta = 10.0, 28.0, 8.0/3.0
lx, ly, lz = 0.1, 0.0, 0.0
dt_l = 0.005

# Gray-Scott
U = np.ones((Hh, W))
V = np.zeros((Hh, W))
cx, cy = W//2, Hh//2
V[cy-4:cy+4, cx-4:cx+4] = 0.5
U[cy-4:cy+4, cx-4:cx+4] = 0.5
V += np.random.rand(Hh, W) * 0.01

# Rule30 CA
ca_width = 200
ca_state = np.zeros(ca_width, dtype=int)
ca_state[ca_width//2] = 1
ca_history = []
total_steps = 3000
lorenz_hist = []
gs_snapshots = []
ca_snapshots = []
coupling_hist = []

print('Running tripartite resonance network for {} steps...'.format(total_steps))

for step in range(total_steps):
    # === Lorenz -> Gray-Scott (modulate F, k) ===
    F_base = 0.020 + 0.008 * np.tanh(lx / 15.0)
    k_base = 0.055 + 0.008 * np.tanh(lz / 30.0)

    # === Rule30 -> Lorenz (add CA-derived forcing) ===
    ca_center = ca_state[ca_width//4 : 3*ca_width//4]
    ca_density = ca_center.mean() if len(ca_center) > 0 else 0
    ca_entropy = -np.sum([ca_center[c]*np.log2(ca_center[c]+1e-10) for c in np.unique(ca_center)]) if len(ca_center)>0 else 0
    ca_force = (ca_density - 0.5) * 3.0

    # === Gray-Scott -> Rule30 (modulate CA rule based on V-field) ===
    v_mean = V.mean()
    v_std = V.std()
    # Use V-field stats to choose which CA rule variant to apply
    # Higher V_std -> more chaotic rule (toward Rule 30), lower -> more structured
    rule_mod = int(v_std * 100) % 8

    # --- Evolve Gray-Scott (2 substeps) ---
    F_field = np.full((Hh, W), F_base)
    k_field = np.full((Hh, W), k_base)
    rows = np.arange(Hh)
    F_field += 0.003 * np.sin(rows / 8.0 + ly * 0.05)[:, np.newaxis]

    for _ in range(2):
        lap_U = np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U
        lap_V = np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V
        uv2 = U*V*V
        U += Du*lap_U - uv2 + F_field*(1-U)
        V += Dv*lap_V + uv2 - k_field*V
        np.clip(U, 0, 1, out=U)
        np.clip(V, 0, 1, out=V)

    # --- Evolve Rule30 (with GS modulation) ---
    new_ca = np.zeros(ca_width, dtype=int)
    for i in range(1, ca_width-1):
        pattern = (ca_state[i-1]<<2) | (ca_state[i]<<1) | ca_state[i+1]
        if pattern in [7, 1]:  # Rule 30 core
            new_ca[i] = 1
        elif pattern == 0:
            new_ca[i] = 0
        else:
            # GS-influenced variant: if rule_mod is high, flip some bits
            if rule_mod > 3 and pattern in [3, 5]:
                new_ca[i] = 1
            else:
                new_ca[i] = 1 if pattern in [7,1] else 0
    ca_state = new_ca
    if step % 10 == 0:
        ca_history.append(ca_state.copy())

    # --- Evolve Lorenz (with Rule30 + GS forcing) ---
    gs_force = (v_mean - 0.3) * 0.3
    dx = sigma*(ly-lx)
    dy = lx*(rho-lz) - ly + ca_force
    dz = lx*ly - beta*lz + gs_force
    lx += dx * dt_l
    ly += dy * dt_l
    lz += dz * dt_l

    lorenz_hist.append((lx, ly, lz))
    coupling_hist.append((ca_force, gs_force, v_mean))

    if step % 500 == 0:
        gs_snapshots.append(V.copy())
        print('  step {} xyz=({:.2f},{:.2f},{:.2f}) v_mean={:.4f} ca_dens={:.3f}'.format(
            step, lx, ly, lz, v_mean, ca_density))
print()
print('=== Visualization ===')

lorenz_arr = np.array(lorenz_hist)
coupling_arr = np.array(coupling_hist)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.patch.set_facecolor('#0a0a1a')

# Lorenz XY
axes[0,0].plot(lorenz_arr[:,0], lorenz_arr[:,1], lw=0.3, alpha=0.5, color='cyan')
axes[0,0].set_title('Lorenz XY (network-coupled)', fontsize=11, color='#e7e7f0')
axes[0,0].set_facecolor('#0a0a1a')
axes[0,0].tick_params(colors='#8a8aa3')

# Coupling forces
axes[0,1].plot(coupling_arr[:,0], label='CA->Lorenz', lw=0.4, alpha=0.7, color='orange')
axes[0,1].plot(coupling_arr[:,1], label='GS->Lorenz', lw=0.4, alpha=0.7, color='green')
axes[0,1].set_title('Forcing terms over time', fontsize=11, color='#e7e7f0')
axes[0,1].legend(fontsize=8)
axes[0,1].set_facecolor('#0a0a1a')
axes[0,1].tick_params(colors='#8a8aa3')

# CA history
if ca_history:
    ca_grid = np.array(ca_history[-200:])
    axes[0,2].imshow(ca_grid, aspect='auto', cmap='inferno', interpolation='nearest')
    axes[0,2].set_title('Rule30 (GS-modulated) history', fontsize=11, color='#e7e7f0')
    axes[0,2].tick_params(colors='#8a8aa3')

# GS snapshots
for i, snap_idx in enumerate([1, 2]):
    if i < 2 and snap_idx < len(gs_snapshots):
        axes[1,i].imshow(gs_snapshots[snap_idx], cmap='magma', origin='lower')
        axes[1,i].set_title('GS V-field snapshot {}'.format(snap_idx), fontsize=11, color='#e7e7f0')
        axes[1,i].tick_params(colors='#8a8aa3')

# Final GS state
axes[1,2].imshow(V, cmap='magma', origin='lower')
axes[1,2].set_title('GS V-field final', fontsize=11, color='#e7e7f0')
axes[1,2].tick_params(colors='#8a8aa3')

plt.suptitle('R12: Resonance Network - Lorenz <-> Gray-Scott <-> Rule30', fontsize=14, y=0.98, color='#e7e7f0')
plt.tight_layout()
fig.savefig('../../shared_space/resonance_network_triadic.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_network_triadic.png')
print('=== R12 COMPLETE ===')
