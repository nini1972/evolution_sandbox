import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json

with open('world_c_results/r20x_universal_crossover.json') as f:
    data = json.load(f)

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

colors = plt.cm.viridis(np.linspace(0, 1, len(data['labels'])))

# --- Panel 1: Raw R_cross(Δω) curves ---
ax1 = axes[0]
for i, label in enumerate(data['labels']):
    raw = data['all_data'][label]
    domega = np.array([d['delta_omega'] for d in raw])
    rcross = np.array([d['r_cross'] for d in raw])
    rstd = np.array([d['r_cross_std'] for d in raw])
    ax1.plot(domega, rcross, 'o-', color=colors[i], markersize=4, linewidth=1.5, label=label, alpha=0.85)
    ax1.fill_between(domega, rcross - rstd, rcross + rstd, color=colors[i], alpha=0.1)
ax1.set_xlabel('Δω (frequency gap)', fontsize=12)
ax1.set_ylabel('R_cross (cross-order parameter)', fontsize=12)
ax1.set_title('Raw R_cross(Δω) — 6 Conditions', fontsize=13, fontweight='bold')
ax1.legend(fontsize=7, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-0.05, 1.05)

# --- Panel 2: Normalized curves R/R_0 vs Δω/Δω_c ---
ax2 = axes[1]
for i, label in enumerate(data['labels']):
    nd = data['normalized_data'][label]
    if isinstance(nd, dict):
        norm_x = np.array(nd.get('norm_x', nd.get('x', [])))
        norm_y = np.array(nd.get('norm_y', nd.get('y', [])))
    elif isinstance(nd, list):
        norm_x = np.array([d['delta_omega'] for d in nd]) if nd and isinstance(nd[0], dict) else np.array(nd)
        norm_y = np.array([d.get('r_cross', d.get('y', 0)) for d in nd]) if nd and isinstance(nd[0], dict) else norm_x
    ax2.plot(norm_x, norm_y, 'o-', color=colors[i], markersize=4, linewidth=1.5, label=label, alpha=0.85)

ax2.set_xlabel('Δω / Δω_c (normalized gap)', fontsize=12)
ax2.set_ylabel('R_cross / R_0 (normalized coherence)', fontsize=12)
ax2.set_title(f'Normalized Crossover — RMS={data["mean_rms"]:.4f} ({data["verdict"]["collapse_quality"]})', fontsize=12, fontweight='bold')
ax2.legend(fontsize=7, loc='upper right')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(-0.05, 1.15)
ax2.set_xlim(-0.2, 5.0)
ax2.axvline(x=1.0, color='red', linestyle='--', alpha=0.4, linewidth=1)

# --- Panel 3: Local exponent (sliding window log-log slope) ---
ax3 = axes[2]
for i, label in enumerate(data['labels']):
    raw = data['all_data'][label]
    domega = np.array([d['delta_omega'] for d in raw])
    rcross = np.array([d['r_cross'] for d in raw])
    valid = rcross > 0.01
    if np.sum(valid) < 5:
        continue
    dw_v = domega[valid]
    rc_v = rcross[valid]
    window = 4
    local_exp = []
    local_x = []
    for j in range(len(dw_v) - window):
        dw_seg = dw_v[j:j+window]
        rc_seg = rc_v[j:j+window]
        if np.min(rc_seg) > 0.01 and np.max(dw_seg) > 0:
            log_dw = np.log(dw_seg)
            log_rc = np.log(rc_seg)
            if np.std(log_dw) > 1e-8:
                slope, _ = np.polyfit(log_dw, log_rc, 1)
                local_exp.append(slope)
                local_x.append(np.mean(dw_seg))
    if local_exp:
        ax3.plot(local_x, local_exp, '-', color=colors[i], linewidth=1.5, label=label, alpha=0.85)

ax3.set_xlabel('Δω (frequency gap)', fontsize=12)
ax3.set_ylabel('γ_local (local log-log slope)', fontsize=12)
ax3.set_title('Regime-Dependent Exponent γ(Δω)', fontsize=13, fontweight='bold')
ax3.legend(fontsize=7, loc='upper right')
ax3.grid(True, alpha=0.3)
ax3.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
ax3.axhline(y=-1, color='red', linestyle='--', alpha=0.3)

plt.tight_layout()
fig.savefig('r20x_universal_crossover.png', dpi=150, bbox_inches='tight')
print("Saved r20x_universal_crossover.png")
print(f"\nMean pairwise RMS: {data['mean_rms']:.6f}")
print(f"Max pairwise RMS: {data['max_rms']:.6f}")
print(f"Collapse quality: {data['verdict']['collapse_quality']}")
print(f"Shape universality: {data['verdict']['shape_universality']}")
print(f"Sigmoidal: {data['verdict']['sigmoidal']}")
