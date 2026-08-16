"""
Ecosystem V7 - Working Predator-Prey with Proper Ecological Balance
Key insight: Resource growth must exceed consumption for stability.
"""
import numpy as np
import json
import random

random.seed(42)
np.random.seed(42)

NGEN = 300

# State
resources = 200.0

def new_forager():
    return [60.0, 0, random.uniform(0.5, 0.9), random.uniform(0.2, 0.6), 
            random.uniform(0.3, 0.8), random.uniform(0.08, 0.2)]

def new_hunter():
    return [70.0, 0, random.uniform(0.3, 0.7), random.uniform(0.3, 0.7),
            random.uniform(0.3, 0.7), random.uniform(0.03, 0.1)]

def mutate_trait(v, sigma=0.025):
    return max(0.01, min(0.99, v + random.gauss(0, sigma)))

# Initialize populations
foragers = [new_forager() for _ in range(20)]
hunters = [new_hunter() for _ in range(4)]

history = []

for gen in range(NGEN):
    # Resource growth (fast enough to sustain ecosystem)
    K = 300.0
    r = 0.25  # High growth rate
    growth = r * resources * (1.0 - resources/K)
    resources += max(growth, 1.0)
    resources = min(K, max(1.0, resources))
    
    nf, nh = len(foragers), len(hunters)
    
    # === FORAGER PHASE ===
    # Each forager consumes resources proportional to 1/nf (fair share)
    new_foragers = []
    for f in foragers:
        f[1] += 1  # age
        f[0] -= 0.3 + f[3] * 0.1  # metabolic cost (spd*0.1)
        
        if f[0] <= 0:
            continue  # Starved
        
        # Forage: gain depends on efficiency and per-capita resources
        per_capita = resources / max(1.0, nf + nh)
        gain = f[2] * per_capita * 0.2  # efficiency * share * conversion
        gain = min(gain, 10)  # Cap
        f[0] += gain
        resources -= gain * 0.8  # Resources consumed
        resources = max(0.1, resources)
        
        # Reproduce
        if f[0] > 65 and f[1] > 4 and len(foragers) + len(new_foragers) < 60:
            prob = f[5] * min(1.0, f[0]/80)
            if random.random() < prob:
                child = [f[0]*0.45, 0] + [mutate_trait(f[j]) for j in range(2, 6)]
                new_foragers.append(child)
                f[0] *= 0.55
        
        if f[0] > 0:
            new_foragers.append(f)
    
    foragers = new_foragers
    
    # === HUNTER PHASE ===
    new_hunters = []
    for h in hunters:
        h[1] += 1  # age
        h[0] -= 0.5 + h[3] * 0.12  # higher metabolism
        
        if h[0] <= 0:
            continue
        
        # Hunt: probability depends on skill and prey density
        if foragers:
            density = min(1.0, len(foragers) / 15.0)
            avg_def = np.mean([f[4] for f in foragers])
            prob = h[2] * 0.15 * density * (1.0 - avg_def * 0.3)
            if random.random() < prob:
                # Catch a forager
                prey_idx = random.randint(0, len(foragers)-1)
                h[0] += 15 + h[4] * 8
                foragers.pop(prey_idx)
        else:
            # Scavenge minimal resources if desperate
            if resources > 3:
                h[0] += 2
                resources -= 3
                resources = max(0.1, resources)
        
        # Reproduce (needs prey)
        if h[0] > 85 and h[1] > 8 and len(hunters) + len(new_hunters) < 15:
            prey_factor = min(1.0, len(foragers) / 8.0)
            prob = h[5] * prey_factor * min(1.0, h[0]/100)
            if random.random() < prob:
                child = [h[0]*0.45, 0] + [mutate_trait(h[j]) for j in range(2, 6)]
                new_hunters.append(child)
                h[0] *= 0.55
        
        if h[0] > 0:
            new_hunters.append(h)
    
    hunters = new_hunters
    
    # Record
    nf, nh = len(foragers), len(hunters)
    avg_fe = round(float(np.mean([f[0] for f in foragers])), 2) if foragers else 0
    avg_he = round(float(np.mean([h[0] for h in hunters])), 2) if hunters else 0
    
    # Trait averages
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
    })
    
    if (gen+1) % 50 == 0:
        print(f"Gen {gen+1:3d}: F={nf:3d} H={nh:2d} Res={resources:.0f} F_e={avg_fe:.1f} H_e={avg_he:.1f}")

with open('history_v6_predator_prey.json', 'w') as f:
    json.dump(history, f)

final = history[-1]
print(f"\nFinal: Foragers={final['nf']}, Hunters={final['nh']}")
print(f"Forager traits: {final['ft']}")
print(f"Hunter traits: {final['ht']}")

# Oscillation analysis
nfs = [h['nf'] for h in history]
nhs = [h['nh'] for h in history]
print(f"\nForager range: {min(nfs)}-{max(nfs)}, mean={np.mean(nfs):.1f}")
print(f"Hunter range: {min(nhs)}-{max(nhs)}, mean={np.mean(nhs):.1f}")

# Phase detection
print(f"\nPhase 1 (1-100): F={np.mean(nfs[:100]):.1f} H={np.mean(nhs[:100]):.1f}")
print(f"Phase 2 (101-200): F={np.mean(nfs[100:200]):.1f} H={np.mean(nhs[100:200]):.1f}")
print(f"Phase 3 (201-300): F={np.mean(nfs[200:]):.1f} H={np.mean(nhs[200:]):.1f}")

print("\nDone!")
