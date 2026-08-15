"""
Ecosystem V6 - Predator-Prey (debug + balanced)
"""
import numpy as np
import json
import random

random.seed(42)
np.random.seed(42)

NGEN = 300

class Forager:
    def __init__(self, traits=None):
        self.traits = traits or {
            'efficiency': random.uniform(0.5, 0.9),
            'speed': random.uniform(0.2, 0.6),
            'defense': random.uniform(0.3, 0.8),
            'repro': random.uniform(0.1, 0.25),
        }
        self.energy = 60.0
        self.age = 0
    
    def mutate(self, sigma=0.03):
        return max(0.01, min(0.99, self.traits.get('efficiency', 0.5) + random.gauss(0, sigma)))

class Hunter:
    def __init__(self, traits=None):
        self.traits = traits or {
            'skill': random.uniform(0.3, 0.7),
            'speed': random.uniform(0.3, 0.7),
            'efficiency': random.uniform(0.3, 0.7),
            'repro': random.uniform(0.05, 0.15),
        }
        self.energy = 70.0
        self.age = 0
    
    def mutate(self, sigma=0.03):
        return max(0.01, min(0.99, self.traits.get('skill', 0.5) + random.gauss(0, sigma)))

# Initialize
foragers = [Forager() for _ in range(20)]
hunters = [Hunter() for _ in range(4)]
resource_pool = 250.0

history = []

for gen in range(NGEN):
    # Resource growth
    K = 400.0
    growth = 0.1 * resource_pool * (1 - resource_pool/K)
    resource_pool += max(growth, 0.5)  # Minimum growth
    resource_pool = min(K, max(1.0, resource_pool))
    
    # === FORAGER PHASE ===
    forager_food = 0
    for f in foragers:
        # Metabolism
        f.energy -= 0.4 + f.traits['speed'] * 0.1
        
        # Foraging
        share = resource_pool / (len(foragers) + 5)
        gain = f.traits['efficiency'] * share * 0.4
        gain = min(gain, 12)
        f.energy += gain
        forager_food += gain * 1.5
    
    resource_pool -= forager_food
    resource_pool = max(1.0, resource_pool)
    
    # Forager death
    foragers = [f for f in foragers if f.energy > 0]
    
    # Forager reproduction
    new_f = []
    for f in foragers:
        f.age += 1
        if f.energy > 70 and f.age > 4 and len(foragers) + len(new_f) < 70:
            prob = f.traits['repro'] * min(1.0, f.energy/90)
            if random.random() < prob:
                child_traits = {k: max(0.01, min(0.99, v + random.gauss(0, 0.03))) 
                               for k, v in f.traits.items()}
                new_f.append(Forager(child_traits))
                f.energy *= 0.5
    foragers.extend(new_f)
    
    # === HUNTER PHASE ===
    # Hunters hunt foragers
    killed_foragers = []
    for h in hunters:
        h.energy -= 0.6 + h.traits['speed'] * 0.15
        h.age += 1
        
        if h.energy > 0 and foragers:
            # Hunting success probability
            avg_defense = np.mean([f.traits['defense'] for f in foragers])
            density = min(1.0, len(foragers) / 15.0)
            prob = h.traits['skill'] * 0.12 * density * (1 - avg_defense * 0.4)
            
            if random.random() < prob:
                # Successful hunt
                prey_idx = random.randint(0, len(foragers)-1)
                h.energy += 20 + h.traits['efficiency'] * 8
                killed_foragers.append(prey_idx)
    
    # Remove killed foragers (remove from end to avoid index issues)
    killed_set = set(killed_foragers)
    foragers = [f for i, f in enumerate(foragers) if i not in killed_set]
    
    # Hunter death
    hunters = [h for h in hunters if h.energy > 0]
    
    # Hunter reproduction
    new_h = []
    for h in hunters:
        if h.energy > 80 and h.age > 8 and len(hunters) + len(new_h) < 12:
            prey_factor = min(1.0, len(foragers) / 10.0)
            prob = h.traits['repro'] * prey_factor * min(1.0, h.energy/100)
            if random.random() < prob:
                child_traits = {k: max(0.01, min(0.99, v + random.gauss(0, 0.03)))
                               for k, v in h.traits.items()}
                new_h.append(Hunter(child_traits))
                h.energy *= 0.5
    hunters.extend(new_h)
    
    # Record
    nf, nh = len(foragers), len(hunters)
    
    def stats(orgs, keys):
        out = {}
        for k in keys:
            vals = [o.traits[k] for o in orgs]
            out[k] = round(float(np.mean(vals)), 4) if vals else 0
        return out
    
    history.append({
        'gen': gen+1, 'nf': nf, 'nh': nh,
        'res': round(resource_pool, 1),
        'ft': stats(foragers, ['efficiency', 'speed', 'defense', 'repro']),
        'ht': stats(hunters, ['skill', 'speed', 'efficiency', 'repro']),
        'killed': len(killed_foragers),
    })
    
    if (gen+1) % 25 == 0:
        print(f"Gen {gen+1:3d}: F={nf:3d} H={nh:2d} Res={resource_pool:.0f} Killed={len(killed_foragers)}")

with open('history_v6_predator_prey.json', 'w') as f:
    json.dump(history, f)

final = history[-1]
print(f"\nFinal: Foragers={final['nf']}, Hunters={final['nh']}")
print(f"Forager traits: {final['ft']}")
print(f"Hunter traits: {final['ht']}")

# Print phase analysis
mid = 150
print(f"\nPhase comparison (Gen 1-100 vs 200-300):")
early = [h for h in history if h['gen'] <= 100]
late = [h for h in history if h['gen'] > 200]
print(f"Early: avg F={np.mean([h['nf'] for h in early]):.1f}, avg H={np.mean([h['nh'] for h in early]):.1f}")
if late:
    print(f"Late:  avg F={np.mean([h['nf'] for h in late]):.1f}, avg H={np.mean([h['nh'] for h in late]):.1f}")

print("\nDone!")
