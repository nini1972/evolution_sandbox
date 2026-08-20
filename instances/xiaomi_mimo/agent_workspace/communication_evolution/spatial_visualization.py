"""Spatial visualization: run simulation and capture world state snapshots"""
import sys
sys.path.insert(0, 'communication_evolution')
from sim_core import *
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from sim_core import N_SIGNAL_CHANNELS

def run_and_capture():
    world = World()
    agents = [Agent() for _ in range(POP_SIZE)]
    predators = [Predator() for _ in range(PRED_POP)]
    snapshots = []
    
    snapshot_gens = {1, 50, 100, 150, 200, 250, 300}
    
    for gen in range(NGEN):
        world.time = gen
        world.regenerate()
        signals_this_gen = []
        
        for a in agents:
            if not a.alive:
                continue
            a.perceive(world, predators)
            sig = a.gen_signal()
            signals_this_gen.append({
                'id': id(a), 'sig': sig.tolist(),
                'danger': a.danger_level, 'food': a.food_nearby,
                'x': a.x, 'y': a.y, 'energy': a.energy,
                'alive': True
            })
        
        for a in agents:
            if not a.alive:
                continue
            nearby = []
            for s in signals_this_gen:
                if s['id'] == id(a):
                    continue
                d = np.sqrt((a.x-s['x'])**2+(a.y-s['y'])**2)
                if d < a.perception:
                    nearby.append((np.array(s['sig']), d))
            bmod = a.respond(nearby)
            a.move(bmod, world, predators)
        
        for a in agents:
            if a.alive:
                a.try_forage(world)
        
        for a in agents:
            if a.alive:
                a.metabolize()
        
        new_agents = []
        for a in agents:
            if a.can_reproduce() and len(agents)+len(new_agents) < MAX_AGENTS:
                if random.random() < 0.3:
                    new_agents.append(a.reproduce())
        agents.extend(new_agents)
        agents = [a for a in agents if a.alive]
        
        killed_list = []
        for p in predators:
            if p.alive:
                p.move_toward(agents)
                k = p.hunt(agents)
                if k:
                    killed_list.append(k)
                    world.total_kills += 1
        
        new_preds = []
        for p in predators:
            if p.alive and p.energy > 90 and len(predators)+len(new_preds) < 5:
                if random.random() < 0.1:
                    c = Predator(p.x+random.gauss(0,3), p.y+random.gauss(0,3))
                    c.energy = p.energy*0.4
                    p.energy *= 0.5
                    new_preds.append(c)
        predators.extend(new_preds)
        predators = [p for p in predators if p.alive]
        
        if (gen+1) in snapshot_gens:
            agents_data = []
            for a in agents:
                if a.alive:
                    agents_data.append({
                        'x': a.x, 'y': a.y,
                        'energy': a.energy,
                        'danger_level': a.danger_level,
                        'food_nearby': a.food_nearby,
                        'perception': a.perception,
                        'signal': a.cur_signal.tolist() if a.cur_signal is not None else [0]*N_SIGNAL_CHANNELS
                    })
            pred_data = [{'x': p.x, 'y': p.y, 'energy': p.energy} for p in predators if p.alive]
            food_data = [{'x': r['x'], 'y': r['y'], 'amount': r['cur']} for r in world.resources]
            
            snapshots.append({
                'gen': gen+1,
                'agents': agents_data,
                'predators': pred_data,
                'food': food_data
            })
            print(f"  Snapshot at gen {gen+1}: {len(agents_data)} agents, {len(pred_data)} predators, {len(food_data)} food")
    
    return snapshots

print("Running simulation with spatial snapshots...")
snapshots = run_and_capture()

# Create spatial visualization
n_snaps = len(snapshots)
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes_flat = axes.flatten()

for i, snap in enumerate(snapshots):
    ax = axes_flat[i]
    
    # Plot food
    food_x = [f['x'] for f in snap['food']]
    food_y = [f['y'] for f in snap['food']]
    food_a = [f['amount']/100 for f in snap['food']]
    if food_x:
        ax.scatter(food_x, food_y, c='#8BC34A', alpha=0.4, s=[a*20 for a in food_a], marker='s', label='Food')
    
    # Plot agents - color by danger level (red = near predator)
    if snap['agents']:
        ag_x = [a['x'] for a in snap['agents']]
        ag_y = [a['y'] for a in snap['agents']]
        ag_danger = [a['danger_level'] for a in snap['agents']]
        ag_energy = [min(a['energy']/100, 1) for a in snap['agents']]
        
        scatter = ax.scatter(ag_x, ag_y, c=ag_danger, cmap='RdYlGn_r', vmin=0, vmax=1,
                           s=40, edgecolors='black', linewidth=0.3, zorder=5)
        
        # Draw perception circles for a few agents
        for j in range(min(3, len(snap['agents']))):
            a = snap['agents'][j]
            circle = Circle((a['x'], a['y']), a['perception'], 
                           fill=False, linestyle='--', alpha=0.3, color='blue')
            ax.add_patch(circle)
    
    # Plot predators
    if snap['predators']:
        pr_x = [p['x'] for p in snap['predators']]
        pr_y = [p['y'] for p in snap['predators']]
        ax.scatter(pr_x, pr_y, c='#F44336', s=120, marker='X', edgecolors='darkred', 
                  linewidth=1, zorder=6, label='Predator')
    
    ax.set_xlim(0, WORLD_SIZE)
    ax.set_ylim(0, WORLD_SIZE)
    ax.set_aspect('equal')
    ax.set_title(f"Gen {snap['gen']} ({len(snap['agents'])} agents)", fontsize=11, fontweight='bold')
    ax.set_xticks([0, 50, 100])
    ax.set_yticks([0, 50, 100])

# Remove last empty subplot
axes_flat[-1].axis('off')

# Add colorbar for danger
cbar_ax = fig.add_axes([0.92, 0.3, 0.015, 0.4])
sm = plt.cm.ScalarMappable(cmap='RdYlGn_r', norm=plt.Normalize(0, 1))
sm.set_array([])
plt.colorbar(sm, cax=cbar_ax, label='Danger Level')

fig.suptitle('Spatial Distribution of Agents Over Generations\n(Color = Danger Level, X = Predators, Green = Food)',
             fontsize=14, fontweight='bold')
plt.savefig('communication_evolution/spatial_snapshots.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved spatial_snapshots.png")

# ===== Figure 2: Signal vector visualization =====
fig2, axes2 = plt.subplots(2, 4, figsize=(20, 10))
axes2_flat = axes2.flatten()

for i, snap in enumerate(snapshots):
    ax = axes2_flat[i]
    if not snap['agents']:
        continue
    
    sigs = np.array([a['signal'] for a in snap['agents']])
    dangers = np.array([a['danger_level'] for a in snap['agents']])
    
    # Plot first 2 principal signal dimensions
    from numpy.linalg import svd
    if sigs.shape[0] > 5:
        # Center the signals
        sigs_centered = sigs - sigs.mean(axis=0)
        U, S, Vt = svd(sigs_centered, full_matrices=False)
        proj = sigs_centered @ Vt.T
        
        scatter = ax.scatter(proj[:, 0], proj[:, 1], c=dangers, cmap='RdYlGn_r',
                           vmin=0, vmax=1, s=30, alpha=0.7, edgecolors='gray', linewidth=0.3)
        
        # Draw eigenvector directions
        scale = 5
        for j in range(min(2, Vt.shape[0])):
            ax.annotate('', xy=(Vt[j, 0]*scale, Vt[j, 1]*scale), xytext=(0, 0),
                       arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.text(Vt[j, 0]*scale*1.2, Vt[j, 1]*scale*1.2, 
                   f'PC{j+1}\n({S[j]/S.sum()*100:.0f}%)', fontsize=8, color='red')
    
    ax.set_title(f"Gen {snap['gen']}", fontsize=11, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')

axes2_flat[-1].axis('off')
cbar_ax2 = fig2.add_axes([0.92, 0.3, 0.015, 0.4])
plt.colorbar(sm, cax=cbar_ax2, label='Danger Level')

fig2.suptitle('Signal Space Projections (PCA)\nRed arrows = principal signal axes, color = agent danger level',
              fontsize=14, fontweight='bold')
plt.savefig('communication_evolution/signal_pca.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved signal_pca.png")
