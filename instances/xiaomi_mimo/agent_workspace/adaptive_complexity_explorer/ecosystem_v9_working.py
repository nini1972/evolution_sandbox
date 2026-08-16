"""
Ecosystem V9 - REAL Predator-Prey with Lotka-Volterra Oscillations
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
    return [60.0, 0, random.uniform(0.5, 0.9), random.uniform(0.2, 0.6), 
            random.uniform(0.3, 0.8), random.uniform(0.15, 0.3)]

def new_hunter():
    return [70.0, 0, random.uniform(0.3, 0.7), random.uniform(0.3, 0.7),
            random.uniform(0.3, 0.7), random.uniform(0.05, 0.15)]

def mutate_trait(v, sigma=0.02):
    return max(0.01, min(0.99, v + random.gauss(0, sigma)))

# Initialize
foragers = [new_forager() for _ in range(25)]
hunters = [new_hunter() for _ in range(3)]
resources = 200.0

history = []

for gen in range(NGEN):
    # Resource growth
    K = 350.0
    r = 0.3
    growth = r * resources * (1.0 - resources/K)
    resources += max(growth, 1.0)
    resources = min(K, max(1.0, resources))
    
    nf_start, nh_start = len(foragers), len(hunters)
    
    # === FORAGER PHASE ===
    new_foragers = []
    for f in foragers:
        f[1] += 1
        f[0] -= 0.3 + f[3] * 0.1
        
        if f[0] <= 0:
            continue
        
        per_capita = resources / max(1.0, nf_start + nh_start * 0.3)
        gain = f[2] * per_capita * 0.15
        gain = min(gain, 10)
        f[0] += gain
        resources -= gain * 0.5
        resources = max(0.1, resources)
        
        if f[0] > 55 and f[1] > 3 and nf_start + len(new_foragers) < 80:
            prob = f[5] * min(1.0, f[0]/70)
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
        h[0] -= 0.8 + h[3] * 0.2  # HIGH metabolism - MUST hunt
        
        if h[0] <= 0:
            continue
        
        # HIGH hunting probability - key to making dynamics work
        if foragers:
            density = min(1.0, len(foragers) / 10.0)
            avg_def = np.mean([f[4] for f in foragers])
            # Much higher base hunting probability
            prob = h[2] * 0.35 * density * (1.0 - avg_def * 0.25)
            
            if random.random() < prob:
                prey_idx = random.randint(0, len(foragers)-1)
                h[0] += 20 + h[4] * 12
                foragers.pop(prey_idx)
                killed_this_gen += 1
        
        # Reproduce
        if h[0] > 85 and h[1] > 8 and len(hunters) + len(new_hunters) < 15:
            prey_factor = min(1.0, len(foragers) / 10.0)
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
        print(f"Gen {gen+1:3d}: F={nf:3d} H={nh:2d} Res={resources:.0f} Killed={killed_this_gen}")

with open('history_v9_predator_prey.json', 'w') as f:
    json.dump(history, f)

# === PLOTTING ===
gens = np.array([h['gen'] for h in history])
nfs = np.array([h['nf'] for h in history])
nhs = np.array([h['nh'] for h in history])
res = np.array([h['res'] for h in history])
killed = np.array([h['killed'] for h in history])

# Main dynamics plot
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

ax1 = axes[0]
ax1.plot(gens, nfs, 'g-', linewidth=2, label='Foragers')
ax1.plot(gens, nhs * 10, 'r-', linewidth=2, label='Hunters (×10)', alpha=0.8)
ax1.set_ylabel('Population')
ax1.legend(loc='upper right')
ax1.set_title('Predator-Prey Population Dynamics')
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
ax2.plot(gens, res, 'b-', linewidth=2)
ax2.set_ylabel('Resources')
ax2.set_title('Resource Availability')
ax2.grid(True, alpha=0.3)

ax3 = axes[2]
# Smoothed kills
window = 10
killed_smooth = np.convolve(killed, np.ones(window)/window, mode='valid')
ax3.plot(gens[window-1:], killed_smooth, 'r-', linewidth=2, label=f'{window}-gen avg')
ax3.set_ylabel('Kills per Gen (smoothed)')
ax3.set_xlabel('Generation')
ax3.set_title('Hunting Activity')
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('predator_prey_dynamics.png', dpi=150, bbox_inches='tight')
print("Saved: predator_prey_dynamics.png")

# Trait evolution
fig2, axes2 = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

ax = axes2[0]
for trait, color in [('eff', 'green'), ('spd', 'blue'), ('def', 'red')]:
    vals = np.array([h['ft'][trait] for h in history])
    ax.plot(gens, vals, linewidth=2, label=trait, color=color)
ax.set_ylabel('Trait Value')
ax.legend()
ax.set_title('Forager Trait Evolution')
ax.grid(True, alpha=0.3)

ax = axes2[1]
for trait, color in [('skill', 'red'), ('spd', 'blue'), ('eff', 'green')]:
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

# Phase portrait
fig3, ax3 = plt.subplots(figsize=(8, 8))
# Only plot after transient
skip = 50
scatter = ax3.scatter(nfs[skip:], nhs[skip:], c=gens[skip:], cmap='viridis', alpha=0.6, s=15)
ax3.set_xlabel('Forager Population')
ax3.set_ylabel('Hunter Population')
ax3.set_title('Phase Portrait (Color = Time)')
plt.colorbar(scatter, label='Generation')
plt.savefig('phase_portrait.png', dpi=150, bbox_inches='tight')
print("Saved: phase_portrait.png")

# Analysis
print(f"\n=== ANALYSIS ===")
print(f"Forager range: {min(nfs)}-{max(nfs)}, mean={np.mean(nfs):.1f}")
print(f"Hunter range: {min(nhs)}-{max(nhs)}, mean={np.mean(nhs):.1f}")
print(f"Total kills: {sum(killed)}")
print(f"Avg kills/gen: {np.mean(killed):.2f}")

# Cross-correlation
nfs_n = nfs[50:] - np.mean(nfs[50:])
nhs_n = nhs[50:] - np.mean(nhs[50:])
if np.std(nfs_n) > 0 and np.std(nhs_n) > 0:
    cc = np.correlate(nfs_n, nhs_n, mode='full')
    cc = cc[len(cc)//2 - 50 : len(cc)//2 + 51]
    cc /= (np.std(nfs_n) * np.std(nhs_n) * len(nfs_n))
    peak_lag = np.argmax(cc) - 50
    print(f"Cross-correlation peak lag: {peak_lag} gen (positive = F leads H)")

# Period detection via autocorrelation
ac = np.correlate(nfs_n, nfs_n, mode='full')
ac = ac[len(ac)//2:]
ac /= ac[0]
# Find first minimum
minima = np.where(np.diff(np.sign(np.diff(ac))))[0]
if len(minima) > 0:
    print(f"Forager oscillation period estimate: ~{2*minima[0]} gen")

final = history[-1]
print(f"\nFinal: F={final['nf']}, H={final['nh']}, Res={final['res']}")
