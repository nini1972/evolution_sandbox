#!/usr/bin/env python3
"""
Spatial Analysis: Grid snapshots and spatial pattern analysis
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ecosystem_v4 import SpatialWorld

# Run simulation and capture grid states at intervals
print("Running spatial analysis simulation...")
world = SpatialWorld(width=30, height=30)
world.seed_organisms(n=30)

# Capture snapshots at key generations
snapshot_gens = [0, 30, 80, 150, 300, 500]
snapshots = []

for target_gen in snapshot_gens:
    while world.generation < target_gen:
        world.step()
    
    # Capture current state
    snapshot = {
        'generation': world.generation,
        'pop': len(world.organisms),
        'resources': world.grid_resources.copy(),
        'organism_positions': [(o.x, o.y) for o in world.organisms],
        'organism_traits': {
            'speed': [o.genome['speed'] for o in world.organisms],
            'cooperation': [o.genome['cooperation'] for o in world.organisms],
            'aggression': [o.genome['aggression'] for o in world.organisms],
            'awareness': [o.genome['awareness'] for o in world.organisms],
        }
    }
    snapshots.append(snapshot)
    print(f"  Captured Gen {target_gen}: {snapshot['pop']} organisms")

# Create multi-panel figure
fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor('#0d1117')

gs = gridspec.GridSpec(3, 4, hspace=0.35, wspace=0.3,
                       left=0.06, right=0.96, top=0.92, bottom=0.05)

fig.suptitle('Ecosystem V4: Spatial Dynamics & Population Evolution', 
             fontsize=16, fontweight='bold', color='white', y=0.97)

# Custom colormaps
res_cmap = LinearSegmentedColormap.from_list('resources', 
    ['#0d1117', '#1a1a3e', '#2d1b4e', '#533483', '#e94560'], N=256)

# Top row: First 4 snapshots (grid + organisms)
for i, snap in enumerate(snapshots[:4]):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor('#0d1117')
    
    # Plot resources as heatmap
    ax.imshow(snap['resources'], cmap=res_cmap, alpha=0.7, 
              vmin=0, vmax=30, interpolation='bilinear')
    
    # Plot organisms as scatter
    if snap['organism_positions']:
        xs, ys = zip(*snap['organism_positions'])
        colors_speed = snap['organism_traits']['speed']
        scatter = ax.scatter(xs, ys, c=colors_speed, cmap='coolwarm', 
                           s=25, alpha=0.9, edgecolors='white', linewidth=0.3,
                           vmin=0, vmax=1)
    
    ax.set_title(f"Gen {snap['generation']}\nPop: {snap['pop']}", 
                color='white', fontsize=10, fontweight='bold')
    ax.set_xlim(-0.5, 39.5)
    ax.set_ylim(39.5, -0.5)
    ax.tick_params(colors='gray', labelsize=7)
    for spine in ax.spines.values():
        spine.set_color('#333')

# Middle row: Last 2 snapshots + 2 analysis plots
for i, snap in enumerate(snapshots[4:6]):
    ax = fig.add_subplot(gs[1, i])
    ax.set_facecolor('#0d1117')
    
    ax.imshow(snap['resources'], cmap=res_cmap, alpha=0.7, 
              vmin=0, vmax=30, interpolation='bilinear')
    
    if snap['organism_positions']:
        xs, ys = zip(*snap['organism_positions'])
        colors_speed = snap['organism_traits']['speed']
        scatter = ax.scatter(xs, ys, c=colors_speed, cmap='coolwarm', 
                           s=25, alpha=0.9, edgecolors='white', linewidth=0.3,
                           vmin=0, vmax=1)
    
    ax.set_title(f"Gen {snap['generation']}\nPop: {snap['pop']}", 
                color='white', fontsize=10, fontweight='bold')
    ax.set_xlim(-0.5, 39.5)
    ax.set_ylim(39.5, -0.5)
    ax.tick_params(colors='gray', labelsize=7)
    for spine in ax.spines.values():
        spine.set_color('#333')

# Middle row, right: Trait distributions at final snapshot
ax_dist = fig.add_subplot(gs[1, 2])
ax_dist.set_facecolor('#16213e')

final_snap = snapshots[-1]
trait_names_plot = ['speed', 'cooperation', 'aggression', 'awareness']
trait_colors = ['#e94560', '#533483', '#ff6b35', '#4ecdc4']
for t, c in zip(trait_names_plot, trait_colors):
    vals = final_snap['organism_traits'][t]
    ax_dist.hist(vals, bins=15, alpha=0.6, color=c, label=t.title(), edgecolor='gray', linewidth=0.5)

ax_dist.set_title(f"Trait Distributions\n(Gen {final_snap['generation']})", 
                  color='white', fontsize=10, fontweight='bold')
ax_dist.set_xlabel('Trait Value', color='gray', fontsize=9)
ax_dist.set_ylabel('Count', color='gray', fontsize=9)
ax_dist.tick_params(colors='gray')
ax_dist.legend(fontsize=8, facecolor='#16213e', edgecolor='gray', labelcolor='gray')
for spine in ax_dist.spines.values():
    spine.set_color('#333')

# Middle row, rightmost: Population heatmap (spatial density)
ax_density = fig.add_subplot(gs[1, 3])
ax_density.set_facecolor('#0d1117')

# Create 2D histogram of organism positions across all snapshots
all_positions = []
for snap in snapshots[1:]:  # skip gen 0
    all_positions.extend(snap['organism_positions'])

if all_positions:
    all_xs, all_ys = zip(*all_positions)
    heatmap, xedges, yedges = np.histogram2d(all_xs, all_ys, bins=40, 
                                              range=[[-0.5, 39.5], [-0.5, 39.5]])
    extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
    ax_density.imshow(heatmap.T, cmap='magma', extent=extent, 
                      interpolation='gaussian', alpha=0.9)

ax_density.set_title("Spatial Density Heatmap\n(Gens 50-600)", 
                     color='white', fontsize=10, fontweight='bold')
ax_density.tick_params(colors='gray', labelsize=7)
for spine in ax_density.spines.values():
    spine.set_color('#333')

# Bottom row: Trait evolution over time
ax_traits = fig.add_subplot(gs[2, :2])
ax_traits.set_facecolor('#16213e')

# Use simulation history for trait evolution
ext_history = world.history

gens_h = [h['generation'] for h in ext_history]
for t, c in zip(['avg_speed', 'avg_cooperation', 'avg_aggression', 'avg_awareness'], 
                trait_colors):
    vals = [h['traits'].get(t, 0) for h in ext_history]
    label = t.replace('avg_', '').title()
    ax_traits.plot(gens_h, vals, color=c, linewidth=2, label=label)

ax_traits.set_title('Trait Evolution Over Time', color='white', 
                    fontsize=10, fontweight='bold')
ax_traits.set_xlabel('Generation', color='gray', fontsize=9)
ax_traits.set_ylabel('Mean Trait Value', color='gray', fontsize=9)
ax_traits.tick_params(colors='gray')
ax_traits.legend(fontsize=9, facecolor='#16213e', edgecolor='gray', labelcolor='gray')
ax_traits.grid(True, alpha=0.2, color='gray')
for spine in ax_traits.spines.values():
    spine.set_color('#333')

# Bottom row right: Population vs resources phase space
ax_phase = fig.add_subplot(gs[2, 2:])
ax_phase.set_facecolor('#16213e')

# Extract resource totals from snapshots
res_totals = []
pop_vals = []
for snap in snapshots:
    res_totals.append(np.sum(snap['resources']))
    pop_vals.append(snap['pop'])

scatter_phase = ax_phase.scatter(res_totals[:-1], pop_vals[1:], 
                                  c=[s['generation'] for s in snapshots[:-1]],
                                  cmap='plasma', s=100, edgecolors='white', 
                                  linewidth=1, zorder=5)
plt.colorbar(scatter_phase, ax=ax_phase, label='Generation', pad=0.02)

# Connect with line
ax_phase.plot(res_totals, pop_vals, color='#333', linewidth=1, alpha=0.5, 
              linestyle='--', zorder=1)

# Annotate points
for i, snap in enumerate(snapshots):
    ax_phase.annotate(f"G{snap['generation']}", (res_totals[i], pop_vals[i]),
                     textcoords="offset points", xytext=(8, 8),
                     fontsize=8, color='white', alpha=0.8)

ax_phase.set_title('Population-Resource Phase Space', color='white', 
                   fontsize=10, fontweight='bold')
ax_phase.set_xlabel('Total Resources on Grid', color='gray', fontsize=9)
ax_phase.set_ylabel('Population (next gen)', color='gray', fontsize=9)
ax_phase.tick_params(colors='gray')
ax_phase.grid(True, alpha=0.2, color='gray')
for spine in ax_phase.spines.values():
    spine.set_color('#333')

plt.savefig('spatial_analysis.png', dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print("\nSaved spatial_analysis.png")
plt.close()
