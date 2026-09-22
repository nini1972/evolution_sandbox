#!/usr/bin/env python3
"""Comprehensive visualization of phi4 kink-antikink resonance windows."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Load ultrafine data
data = json.load(open('phi4_ultrafine_results.json'))

velocities = []
outcomes = []
final_seps = []
bounces_list = []

for k in sorted(data.keys(), key=float):
    v = data[k]
    velocities.append(float(k))
    outcomes.append(v['outcome'])
    final_seps.append(v['final_sep'])
    bounces_list.append(v['bounces'])

velocities = np.array(velocities)
final_seps = np.array(final_seps)

# Also load coarse data for full range
coarse_data = json.load(open('phi4_resonance_data.json'))
coarse_vels = np.array([d['v'] for d in coarse_data])
coarse_seps = np.array([d['final_sep'] for d in coarse_data])
coarse_status = [d['status'] for d in coarse_data]

# Color map: BION=red, ESC=green, 1b=blue, 2b=purple
color_map = {'BION': 'red', 'ESC': 'green', '1b': 'blue', '2b': 'purple', 'bion': 'red', 'escape': 'green'}
colors = [color_map.get(o, 'gray') for o in outcomes]

fig, axes = plt.subplots(3, 1, figsize=(14, 14), gridspec_kw={'height_ratios': [2, 2, 1]})

# --- Plot 1: Resonance window structure (ultrafine scan) ---
ax1 = axes[0]
# Plot BION as red at y=0, ESC as green at final_sep
bion_mask = np.array([o == 'BION' for o in outcomes])
esc_mask = np.array([o == 'ESC' for o in outcomes])
b1_mask = np.array([o == '1b' for o in outcomes])
b2_mask = np.array([o == '2b' for o in outcomes])

ax1.scatter(velocities[bion_mask], np.zeros(np.sum(bion_mask)), c='red', s=15, label='BION (bound)', zorder=3)
ax1.scatter(velocities[esc_mask], final_seps[esc_mask], c='green', s=15, label='ESC (escape)', zorder=3)
ax1.scatter(velocities[b1_mask], final_seps[b1_mask], c='blue', s=30, marker='D', label='1-bounce escape', zorder=3)
ax1.scatter(velocities[b2_mask], final_seps[b2_mask], c='purple', s=30, marker='s', label='2-bounce escape', zorder=3)

# Highlight resonance windows
ax1.axvspan(0.189, 0.189, alpha=0.15, color='green')
ax1.axvspan(0.194, 0.203, alpha=0.15, color='green')
ax1.axvspan(0.224, 0.229, alpha=0.15, color='green')
ax1.axvspan(0.236, 0.240, alpha=0.15, color='green')
ax1.axvspan(0.244, 0.249, alpha=0.15, color='green')
ax1.axvspan(0.253, 0.260, alpha=0.15, color='green')

ax1.set_xlabel('Initial velocity v', fontsize=12)
ax1.set_ylabel('Final separation', fontsize=12)
ax1.set_title('φ⁴ Kink-Antikink Resonance Windows (ultrafine scan, Δv=0.001)', fontsize=14)
ax1.legend(fontsize=10, loc='upper left')
ax1.set_xlim(0.175, 0.305)
ax1.set_ylim(-5, 130)
ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.3)

# --- Plot 2: Full velocity range (coarse scan) ---
ax2 = axes[1]
bion_mask_c = np.array([s == 'bion' for s in coarse_status])
esc_mask_c = np.array([s == 'escape' for s in coarse_status])

ax2.scatter(coarse_vels[bion_mask_c], np.zeros(np.sum(bion_mask_c)), c='red', s=20, label='BION (bound)', zorder=3)
ax2.scatter(coarse_vels[esc_mask_c], coarse_seps[esc_mask_c], c='green', s=20, label='ESC (escape)', zorder=3)
ax2.axvline(x=0.19, color='orange', linestyle='--', alpha=0.7, label='First resonance window ~v=0.19')
ax2.axvline(x=0.26, color='purple', linestyle='--', alpha=0.7, label='Critical velocity ~v≈0.26')
ax2.set_xlabel('Initial velocity v', fontsize=12)
ax2.set_ylabel('Final separation', fontsize=12)
ax2.set_title('φ⁴ Kink-Antikink: Full Velocity Range (coarse scan, Δv=0.005)', fontsize=14)
ax2.legend(fontsize=10)
ax2.set_xlim(0.08, 0.95)
ax2.set_ylim(-5, 150)

# --- Plot 3: Resonance window identification ---
ax3 = axes[2]
# Create binary: 0=BION, 1=ESC
binary = np.array([0 if o == 'BION' else 1 for o in outcomes])
ax3.fill_between(velocities, 0, binary, where=(binary==1), color='green', alpha=0.5, label='Escape window')
ax3.fill_between(velocities, 0, binary, where=(binary==0), color='red', alpha=0.3, label='BION')
ax3.set_xlabel('Initial velocity v', fontsize=12)
ax3.set_ylabel('Outcome (0=BION, 1=ESC)', fontsize=12)
ax3.set_title('Resonance Window Structure — Fractal-like Interspersing of BION/ESC', fontsize=14)
ax3.set_xlim(0.175, 0.305)
ax3.set_ylim(-0.1, 1.1)
ax3.legend(fontsize=10)

# Count windows
esc_regions = []
in_esc = False
start = None
for i, o in enumerate(outcomes):
    if o != 'BION' and not in_esc:
        in_esc = True
        start = velocities[i]
    elif o == 'BION' and in_esc:
        in_esc = False
        esc_regions.append((start, velocities[i-1]))
if in_esc:
    esc_regions.append((start, velocities[-1]))

print(f"Escape windows found: {len(esc_regions)}")
for i, (s, e) in enumerate(esc_regions):
    print(f"  Window {i+1}: v=[{s:.3f}, {e:.3f}], width={e-s:.4f}")
    # Add annotation
    mid = (s + e) / 2
    if mid < 0.305:
        ax3.annotate(f'W{i+1}', xy=(mid, 0.5), fontsize=8, ha='center', va='center', 
                     fontweight='bold', color='darkgreen')

plt.tight_layout()
fig.savefig('phi4_resonance_windows_comprehensive.png', dpi=150, bbox_inches='tight')
print("Saved phi4_resonance_windows_comprehensive.png")

# Also compute the critical velocity
# The critical velocity is where BION transitions to permanent ESC
# From the data, above v~0.26 everything is ESC
crit_v = 0.26
print(f"\nCritical velocity (BION→ESC transition): v_c ≈ {crit_v}")
print(f"BION regime: v < {crit_v} (with resonance windows)")
print(f"ESC regime: v > {crit_v} (always escape)")

# Bounce structure
print("\nBounce windows:")
for i, (v, o, b) in enumerate(zip(velocities, outcomes, bounces_list)):
    if b > 0:
        print(f"  v={v:.3f}, outcome={o}, bounces={b}")
