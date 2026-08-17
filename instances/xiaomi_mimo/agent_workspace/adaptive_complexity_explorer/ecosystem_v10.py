"""
Ecosystem V10 - Carefully Calibrated Predator-Prey
Goal: Stable Lotka-Volterra oscillations
Key insight: Prey reproduction must be much faster than predation
"""
import numpy as np
import json
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

random.seed(42)
np.random.seed(42)

NGEN = 500

def new_forager():
    return [60.0, 0, random.uniform(0.5, 0.9), random.uniform(0.2, 0.5), 
            random.uniform(0.2, 0.6), random.uniform(0.15, 0.35)]

def new_hunter():
    return [70.0, 0, random.uniform(0.3, 0.6), random.uniform(0.2, 0.5),
            random.uniform(0.3, 0.7), random.uniform(0.05, 0.12)]

def mutate_trait(v, sigma=0.015):
    return max(0.01, min(0.99, v + random.gauss(0, sigma)))

# Initialize
foragers = [new_forager() for _ in range(30)]
hunters = [new_hunter() for _ in range(2)]
resources = 200.0

history = []

for gen in range(NGEN):
    # Resource growth
    K = 300.0
    r = 0.35
    growth = r * resources * (1.0 - resources/K)
    resources += max(growth, 1.0)
    resources = min(K, max(1.0, resources))
    
    nf_start = len(foragers)
    nh_start = len(hunters)
    
    # === FORAGER PHASE ===
    new_foragers = []
    
    for f in foragers:
        f[1] += 1
        f[0] -= 0.25 + f[3] * 0.08  # LOW metabolic cost
        
        if f[0] <= 0:
            continue
        
        # Forage
        per_capita = resources / max(1.0, nf_start + nh_start * 0.2)
        gain = f[2] * per_capita * 0.18
        gain = min(gain, 10)
        f[0] += gain
        resources -= gain * 0.4
        resources = max(0.1, resources)
        
        # Reproduce FREQUENTLY (key for prey recovery)
        if f[0] > 50 and f[1] > 2 and nf_start + len(new_foragers) < 100:
            prob = f[5] * min(1.5, f[0]/60)  # Higher base repro
            if random.random() < prob:
                child = [f[0]*0.45, 0] + [mutate_trait(f[j]) for j in range(2, 6)]
                new_foragers.append(child)
                f[0] *= 0.55
        
        if f[0] > 0:
            new_foragers.append(f)
    
    foragers = new_foragers
    
    # === HUNTER PHASE ===
    new_hunters = []
    killed_this_gen = 0
    
    for h in hunters:
        h[1] += 1
        h[0] -= 0.5 + h[3] * 0.12  # Moderate metabolism
        
        if h[0] <= 0:
            continue
        
        # Hunt: LOW probability (crucial for balance)
        if foragers:
            density = min(1.0, len(foragers) / 15.0)
            avg_def = np.mean([f[4] for f in foragers])
            prob = h[2] * 0.18 * density * (1.0 - avg_def * 0.2)
            
            if random.random() < prob:
                prey_idx = random.randint(0, len(foragers)-1)
                h[0] += 12 + h[4] * 6  # Modest gain
                foragers.pop(prey_idx)
                killed_this_gen += 1
        
        # Reproduce slowly
        if h[0] > 85 and h[1] > 12 and len(hunters) + len(new_hunters) < 12:
            prey_factor = min(1.0, len(foragers) / 12.0)
            prob = h[5] * prey_factor * min(1.0, h[0]/100)
            if random.random() < prob:
                child = [h[0]*0.35, 0] + [mutate_trait(h[j]) for j in range(2, 6)]
                new_hunters.append(child)
                h[0] *= 0.65
        
        if h[0] > 0:
            new_hunters.append(h)
    
    hunters = new_hunters
    
    # Record
    nf, nh = len(foragers), len(hunters)
    avg_fe = round(float(np.mean([f[0] for f in foragers])), 2) if foragers else 0
    avg_he = round(float(np.mean([h[0] for h in hunters])), 2) if hunters else 0
    
    ft = {}
    for idx, name in enumerate(['eff', 'spd', 'def', 'repro']):
        vals = [f[idx+2] for f in foragers]
        ft[name] = round(float(np.mean(vals)), 4) if vals else 0
    
    ht = {}
    for idx, name in enumerate(['skill', 'spd', 'eff', 'repro']):
        vals = [h[idx+2] for h in hunters]
        ht[name] = round(float(np.mean(vals)), 4) if vals else 0
    
    history.append({
        'gen': gen+1, 'nf': nf, 'nh': nh,
        'fe': avg_fe, 'he': avg_he,
        'res': round(resources, 1),
        'ft': ft, 'ht': ht,
        'killed': killed_this_gen,
    })
    
    if (gen+1) % 100 == 0:
        print(f"Gen {gen+1:3d}: F={nf:3d} H={nh:2d} Res={resources:.0f} K={killed_this_gen}")

with open('history_v10_predator_prey.json', 'w') as f:
    json.dump(history, f)

# === ANALYSIS & PLOTTING ===
gens = np.array([h['gen'] for h in history])
nfs = np.array([h['nf'] for h in history])
nhs = np.array([h['nh'] for h in history])
res = np.array([h['res'] for h in history])
killed = np.array([h['killed'] for h in history])

print(f"\n=== ANALYSIS ===")
print(f"Forager range: {min(nfs)}-{max(nfs)}, mean={np.mean(nfs):.1f}")
print(f"Hunter range: {min(nhs)}-{max(nhs)}, mean={np.mean(nhs):.1f}")
print(f"Total kills: {sum(killed)}")

# Cross-correlation analysis
if np.std(nfs[50:]) > 0 and np.std(nhs[50:]) > 0:
    nfs_n = nfs[50:] - np.mean(nfs[50:])
    nhs_n = nhs[50:] - np.mean(nhs[50:])
    cc = np.correlate(nfs_n, nhs_n, mode='full')
    mid = len(cc) // 2
    cc_segment = cc[mid-50:mid+51]
    norm = np.std(nfs_n) * np.std(nhs_n) * len(nfs_n)
    if norm > 0:
        cc_segment /= norm
    peak_lag = np.argmax(cc_segment) - 50
    print(f"Cross-correlation peak lag: {peak_lag} gen")

# Main plot
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

ax1 = axes[0]
ax1.plot(gens, nfs, 'g-', linewidth=2, label='Foragers')
ax1.plot(gens, nhs * 8, 'r-', linewidth=2, label='Hunters (×8)', alpha=0.8)
ax1.set_ylabel('Population')
ax1.legend(loc='upper right')
ax1.set_title('Predator-Prey Population Dynamics')
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
ax2.plot(gens, res, 'b-', linewidth=2)
ax2.set_ylabel('Resources')
ax2.grid(True, alpha=0.3)

ax3 = axes[2]
window = 15
killed_smooth = np.convolve(killed, np.ones(window)/window, mode='valid')
ax3.plot(gens[window-1:], killed_smooth, 'r-', linewidth=2)
ax3.set_ylabel('Kills/gen (smoothed)')
ax3.set_xlabel('Generation')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('predator_prey_dynamics.png', dpi=150, bbox_inches='tight')
print("Saved: predator_prey_dynamics.png")

# Phase portrait
fig2, ax2 = plt.subplots(figsize=(8, 8))
skip = 50
sc = ax2.scatter(nfs[skip:], nhs[skip:], c=gens[skip:], cmap='viridis', alpha=0.6, s=15)
ax2.set_xlabel('Forager Population')
ax2.set_ylabel('Hunter Population')
ax2.set_title('Phase Portrait')
plt.colorbar(sc, label='Generation')
plt.savefig('phase_portrait.png', dpi=150, bbox_inches='tight')
print("Saved: phase_portrait.png")

# Trait evolution
fig3, axes3 = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

ax = axes3[0]
for trait, color in [('eff', '#2ecc71'), ('spd', '#3498db'), ('def', '#e74c3c')]:
    vals = np.array([h['ft'][trait] for h in history])
    ax.plot(gens, vals, linewidth=2, label=trait, color=color)
ax.set_ylabel('Trait Value')
ax.legend()
ax.set_title('Forager Trait Evolution')
ax.grid(True, alpha=0.3)

ax = axes3[1]
for trait, color in [('skill', '#e74c3c'), ('spd', '#3498db'), ('eff', '#2ecc71')]:
    vals = np.array([h['ht'][trait] for h in history])
    ax.plot(gens, vals, linewidth=2, label=trait, color=color)
ax.set_ylabel('Trait Value')
ax.set_xlabel('Generation')
ax.legend()
ax.set_title('Hunter Trait Evolution')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('trait_evolution_predator_prey.png', dpi=150, bbox_inches='tight')
print("Saved: trait_evolution_predator_prey.png")

final = history[-1]
print(f"\nFinal: F={final['nf']}, H={final['nh']}, Res={final['res']}")
