"""
M12 — Hybrid Kuramoto-Cellular-Automaton: a substrate-agnostic bridge
between the smooth-transition family and the bifurcation family.

Architecture:
- A 2D grid of N×N cells.
- Each cell carries a Kuramoto phase θ[i,j] ∈ [0, 2π) and a binary CA state s[i,j] ∈ {0,1}.
- Each step:
   1. Update phases: θ ← θ + dt · [ω + K · R_local · sin(neighbor_phase_mean - θ)]
      where R_local is the local Kuramoto order parameter (Treaty 001).
   2. Update CA state: s[i,j] ← XOR( s[i,j], (R_local > threshold) )
      so the CA dynamics is *gated* by the synchronization of the local neighborhood.
- The result is a hybrid substrate where the smooth Kuramoto dynamics controls
  the binary CA rule, and the CA state feeds back into the Kuramoto coupling.

We measure:
- Spatial LZ complexity (Treaty 003 axis 1)
- Temporal LZ complexity decay (Treaty 003 axis 2)
- Phase synchronization R_global
- Bimodality index (fraction of cells with R_local > threshold)

Prediction: the hybrid should sit BETWEEN the two families discovered in M11 —
neither pure smooth-transition nor pure bifurcation, but a continuous bridge.
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter

GRID = 64
STEPS = 200
K_BASE = 1.5      # base Kuramoto coupling (in Treaty 001 hysteresis range)
OMEGA_STD = 0.4   # natural frequency heterogeneity
THRESHOLD = 0.55  # local R threshold for CA gate
DT = 0.1

rng = np.random.default_rng(20260906)

# State: phases + binary
theta = rng.uniform(0, 2*np.pi, size=(GRID, GRID))
s = rng.integers(0, 2, size=(GRID, GRID)).astype(np.uint8)
omega = rng.normal(0.0, OMEGA_STD, size=(GRID, GRID))

# Approximate local order parameter via 3x3 convolution of e^{iθ}
def local_R(theta):
    z = np.exp(1j*theta)
    # 3x3 mean (treat boundary as wrap)
    smooth = np.zeros_like(z)
    for dy in [-1,0,1]:
        for dx in [-1,0,1]:
            smooth += np.roll(np.roll(z, dy, axis=0), dx, axis=1)
    smooth /= 9.0
    return np.abs(smooth), np.angle(smooth)

def lz_complexity_1d(bits):
    """Lempel-Ziv complexity of a 1D binary string (Kaspar & Schuster estimator)."""
    s = ''.join(map(str, bits))
    n = len(s)
    if n == 0: return 0
    i, k, l = 0, 1, 1
    c = 1
    INF = n + 1
    while True:
        if k + l > n:
            c += 1
            break
        substr = s[k:k+l]
        prefix = s[i:i+l]
        if substr in prefix:
            l += 1
            continue
        else:
            c += 1
            i = k
            k = k + l
            l = 1
            if k > n - 1:
                break
    return c

def lz_complexity_2d(grid):
    """Approximate 2D LZ by row+column scanning."""
    bits_row = grid.flatten()
    bits_col = grid.T.flatten()
    return (lz_complexity_1d(bits_row) + lz_complexity_1d(bits_col)) / 2.0

def shannon_entropy(grid):
    p1 = grid.mean()
    if p1 in (0,1): return 0.0
    return -(p1*np.log2(p1) + (1-p1)*np.log2(1-p1))

# Recording
history = {
    'step': [],
    'R_global': [],
    'bimodality': [],
    's_entropy': [],
    's_lz2d': [],
    't_lz_decay_window': [],
}

WINDOW = 8
t_lz_window = []

print("Running hybrid Kuramoto-CA...")
for step in range(STEPS):
    R_loc, phase_mean = local_R(theta)
    # Kuramoto update
    coupling = K_BASE * R_loc * np.sin(phase_mean - theta)
    theta = theta + DT * (omega + coupling)
    theta = theta % (2*np.pi)
    # CA update gated by local R
    gate = (R_loc > THRESHOLD).astype(np.uint8)
    # Moore neighborhood majority
    nb_sum = np.zeros_like(s, dtype=np.int32)
    for dy in [-1,0,1]:
        for dx in [-1,0,1]:
            if dy==0 and dx==0: continue
            nb_sum += np.roll(np.roll(s, dy, axis=0), dx, axis=1)
    new_s = ((nb_sum >= 4) ^ gate).astype(np.uint8)  # majority XOR with sync gate
    s = new_s

    R_global = np.abs(np.exp(1j*theta).mean())
    bimodality = gate.mean()
    ent = shannon_entropy(s)
    lz2d = lz_complexity_2d(s) / (GRID*GRID)

    t_lz_window.append(lz2d)
    if len(t_lz_window) > WINDOW: t_lz_window.pop(0)
    if len(t_lz_window) >= WINDOW:
        decay = (t_lz_window[0] - t_lz_window[-1]) / max(t_lz_window[0], 1e-9)
    else:
        decay = 0.0

    history['step'].append(step)
    history['R_global'].append(float(R_global))
    history['bimodality'].append(float(bimodality))
    history['s_entropy'].append(float(ent))
    history['s_lz2d'].append(float(lz2d))
    history['t_lz_decay_window'].append(float(decay))

    if step in (0, 10, 30, 60, 100, 150, 199):
        print(f"step={step:3d}  R_g={R_global:.3f}  bimodality={bimodality:.3f}  "
              f"S_ent={ent:.3f}  LZ2D={lz2d:.3f}  t_LZ_decay={decay:.3f}")

# Save artifacts
out_json = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/_artifacts/m12_hybrid_substrate.json'
with open(out_json, 'w') as f:
    json.dump({
        'params': {
            'GRID': GRID, 'STEPS': STEPS, 'K_BASE': K_BASE,
            'OMEGA_STD': OMEGA_STD, 'THRESHOLD': THRESHOLD,
        },
        'final_R_global': history['R_global'][-1],
        'final_bimodality': history['bimodality'][-1],
        'final_s_entropy': history['s_entropy'][-1],
        'final_s_lz2d': history['s_lz2d'][-1],
        'final_t_lz_decay': history['t_lz_decay_window'][-1],
        'mean_R_global': float(np.mean(history['R_global'])),
        'mean_bimodality': float(np.mean(history['bimodality'])),
        'std_R_global': float(np.std(history['R_global'])),
        'history_summary': {k: v[::10] for k, v in history.items()},
    }, f, indent=2)
print(f"Saved {out_json}")

# Plots
fig, axes = plt.subplots(3, 2, figsize=(14, 12))
axes[0,0].plot(history['step'], history['R_global'])
axes[0,0].set_title('Global Kuramoto order parameter R')
axes[0,0].set_xlabel('step'); axes[0,0].set_ylabel('R')

axes[0,1].plot(history['step'], history['bimodality'])
axes[0,1].set_title('Bimodality (fraction of cells R_local > threshold)')
axes[0,1].set_xlabel('step'); axes[0,1].set_ylabel('bimodality')

axes[1,0].plot(history['step'], history['s_entropy'])
axes[1,0].set_title('Shannon entropy of CA state')
axes[1,0].set_xlabel('step'); axes[1,0].set_ylabel('H')

axes[1,1].plot(history['step'], history['s_lz2d'])
axes[1,1].set_title('2D LZ complexity of CA state')
axes[1,1].set_xlabel('step'); axes[1,1].set_ylabel('LZ')

axes[2,0].plot(history['step'], history['t_lz_decay_window'])
axes[2,0].set_title('Temporal LZ complexity decay rate')
axes[2,0].set_xlabel('step'); axes[2,0].set_ylabel('decay')

# Phase diagram: spatial entropy vs temporal decay
axes[2,1].scatter(history['s_lz2d'][::5], history['t_lz_decay_window'][::5],
                  c=range(0, len(history['s_lz2d']), 5), cmap='viridis', s=8)
axes[2,1].set_xlabel('Spatial LZ complexity')
axes[2,1].set_ylabel('Temporal LZ decay')
axes[2,1].set_title('Spatiotemporal phase trajectory (Treaty 003)')

fig.tight_layout()
out_png = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/_artifacts/m12_hybrid_evolution.png'
fig.savefig(out_png, dpi=110)
print(f"Saved {out_png}")

# Final state image
fig2, ax = plt.subplots(1, 2, figsize=(10, 5))
ax[0].imshow(np.cos(theta), cmap='hsv')
ax[0].set_title('Final Kuramoto phase field (cos)')
ax[1].imshow(s, cmap='binary')
ax[1].set_title('Final CA state')
fig2.tight_layout()
out_png2 = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/_artifacts/m12_final_state.png'
fig2.savefig(out_png2, dpi=110)
print(f"Saved {out_png2}")
