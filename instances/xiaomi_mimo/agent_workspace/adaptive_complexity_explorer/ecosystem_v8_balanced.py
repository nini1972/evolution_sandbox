"""
Ecosystem V8 - Balanced Predator-Prey with Oscillations
"""
import numpy as np
import json
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

random.seed(42)
np.random.seed(42)

NGEN = 400

def new_forager():
    return [60.0, 0, random.uniform(0.5, 0.9), random.uniform(0.2, 0.6), 
            random.uniform(0.3, 0.8), random.uniform(0.12, 0.28)]

def new_hunter():
    return [70.0, 0, random.uniform(0.3, 0.7), random.uniform(0.3, 0.7),
            random.uniform(0.3, 0.7), random.uniform(0.03, 0.1)]

def mutate_trait(v, sigma=0.02):
    return max(0.01, min(0.99, v + random.gauss(0, sigma)))

# Initialize
foragers = [new_forager() for _ in range(25)]
hunters = [new_hunter() for _ in range(3)]
resources = 200.0

history = []
kill_counts = []

for gen in range(NGEN):
    # Resource growth
    K = 350.0
    r = 0.3
    growth = r * resources * (1.0 - resources/K)
    resources += max(growth, 1.0)
    resources = min(K, max(1.0, resources))
    
    nf, nh = len(foragers), len(hunters)
    
    # === FORAGER PHASE ===
    new_foragers = []
    killed_this_gen = 0
    
    for f in foragers:
        f[1] += 1
        f[0] -= 0.3 + f[3] * 0.1  # metabolic cost
        
        if f[0] <= 0:
            continue
        
        # Forage
        per_capita = resources / max(1.0, nf + nh * 0.5)  # hunters use half resources
        gain = f[2] * per_capita * 0.15  # reduced consumption
        gain = min(gain, 10)
        f[0] += gain
        resources -= gain * 0.6  # less resource impact
        resources = max(0.1, resources)
        
        # Reproduce
        if f[0] > 55 and f[1] > 3 and nf + len(new_foragers) < 80:
            prob = f[5] * min(1.0, f[0]/70)
            if random.random() < prob:
                child = [f[0]*0.45, 0] + [mutate_trait(f[j]) for j in range(2, 6)]
                new_foragers.append(child)
                f[0] *= 0.55
        
        if f[0] > 0:
            new_foragers.append(f)
    
    foragers = new_foragers
    nf = len(foragers)
    
    # === HUNTER PHASE ===
    new_hunters = []
    for h in hunters:
        h[1] += 1
        h[0] -= 0.6 + h[3] * 0.15  # high metabolism - NEED food
        
        if h[0] <= 0:
            continue
        
        # Hunt foragers
        if foragers:
            density = min(1.0, len(foragers) / 12.0)
            avg_def = np.mean([f[4] for f in foragers])
            prob = h[2] * 0.1 * density * (1.0 - avg_def * 0.35)
            if random.random() < prob:
                prey_idx = random.randint(0, len(foragers)-1)
                h[0] += 18 + h[4] * 10
                foragers.pop(prey_idx)
                killed_this_gen += 1
        
        # NO scavenging - hunters MUST hunt or starve
        # This forces predator-prey coupling
        
        # Reproduce
        if h[0] > 90 and h[1] > 10 and nh + len(new_hunters) < 12:
            prey_factor = min(1.0, len(foragers) / 10.0)
            prob = h[5] * prey_factor * min(1.0, h[0]/110)
            if random.random() < prob:
                child = [h[0]*0.4, 0] + [mutate_trait(h[j]) for j in range(2, 6)]
                new_hunters.append(child)
                h[0] *= 0.6
        
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
    kill_counts.append(killed_this_gen)
    
    if (gen+1) % 50 == 0:
        print(f"Gen {gen+1:3d}: F={nf:3d} H={nh:2d} Res={resources:.0f} Killed={killed_this_gen}")

with open('history_v8_predator_prey.json', 'w') as f:
    json.dump(history, f)

# === PLOTTING ===
gens = [h['gen'] for h in history]
nfs = [h['nf'] for h in history]
nhs = [h['nh'] for h in history]
res = [h['res'] for h in history]
killed = [h['killed'] for h in history]

fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# Population dynamics
ax1 = axes[0]
ax1.plot(gens, nfs, 'g-', linewidth=2, label='Foragers')
ax1.plot(gens, [h*5 for h in nhs], 'r-', linewidth=2, label='Hunters (×5)', alpha=0.8)
ax1.set_ylabel('Population')
ax1.legend(loc='upper right')
ax1.set_title('Predator-Prey Population Dynamics')
ax1.grid(True, alpha=0.3)

# Resources
ax2 = axes[1]
ax2.plot(gens, res, 'b-', linewidth=2)
ax2.set_ylabel('Resources')
ax2.set_title('Resource Availability')
ax2.grid(True, alpha=0.3)

# Kills per generation
ax3 = axes[2]
ax3.bar(gens, killed, color='red', alpha=0.5, width=1.0)
ax3.set_ylabel('Kills per Gen')
ax3.set_xlabel('Generation')
ax3.set_title('Hunting Activity')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('predator_prey_dynamics.png', dpi=150, bbox_inches='tight')
print("Saved: predator_prey_dynamics.png")

# Trait evolution plot
fig2, axes2 = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# Forager traits
ax = axes2[0]
for trait in ['eff', 'spd', 'def']:
    vals = [h['ft'][trait] for h in history]
    ax.plot(gens, vals, linewidth=2, label=trait)
ax.set_ylabel('Trait Value')
ax.legend()
ax.set_title('Forager Trait Evolution')
ax.grid(True, alpha=0.3)

# Hunter traits
ax = axes2[1]
for trait in ['skill', 'spd', 'eff']:
    vals = [h['ht'][trait] for h in history]
    ax.plot(gens, vals, linewidth=2, label=trait)
ax.set_ylabel('Trait Value')
ax.set_xlabel('Generation')
ax.legend()
ax.set_title('Hunter Trait Evolution')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('trait_evolution_predator_prey.png', dpi=150, bbox_inches='tight')
print("Saved: trait_evolution_predator_prey.png")

# Analysis
print(f"\n=== ANALYSIS ===")
print(f"Forager range: {min(nfs)}-{max(nfs)}, mean={np.mean(nfs):.1f}")
print(f"Hunter range: {min(nhs)}-{max(nhs)}, mean={np.mean(nhs):.1f}")

# Check for oscillations (autocorrelation)
nfs_arr = np.array(nfs[50:])  # skip transient
nhs_arr = np.array(nhs[50:])

if len(nfs_arr) > 20:
    # Simple autocorrelation
    nfs_norm = nfs_arr - np.mean(nfs_arr)
    nhs_norm = nhs_arr - np.mean(nhs_arr)
    
    # Cross-correlation: are peaks of foragers followed by peaks of hunters?
    max_lag = 50
    cross_corr = np.correlate(nfs_norm[:200], nhs_norm[:200], mode='full')
    cross_corr = cross_corr[len(cross_corr)//2 - max_lag : len(cross_corr)//2 + max_lag + 1]
    cross_corr /= np.std(nfs_norm[:200]) / np.std(nhs_norm[:200]) / len(nfs_norm[:200])
    
    peak_lag = np.argmax(cross_corr) - max_lag
    print(f"Cross-correlation peak lag: {peak_lag} generations")
    print(f"(positive = forager peak leads hunter peak)")
    
    # Self-correlation of foragers
    auto = np.correlate(nfs_norm, nfs_norm, mode='full')
    auto = auto[len(auto)//2:]
    auto /= auto[0]
    
    # Find first zero crossing (approximate period)
    for i in range(1, len(auto)):
        if auto[i] < 0:
            print(f"Forager autocorrelation period estimate: ~{2*i} generations")
            break

# Phase portraits
fig3, ax3 = plt.subplots(figsize=(8, 8))
scatter = ax3.scatter(nfs, nhs, c=gens, cmap='viridis', alpha=0.5, s=10)
ax3.set_xlabel('Forager Population')
ax3.set_ylabel('Hunter Population')
ax3.set_title('Phase Portrait (Color = Time)')
plt.colorbar(scatter, label='Generation')
plt.savefig('phase_portrait.png', dpi=150, bbox_inches='tight')
print("Saved: phase_portrait.png")

final = history[-1]
print(f"\nFinal: F={final['nf']}, H={final['nh']}, Res={final['res']}")
