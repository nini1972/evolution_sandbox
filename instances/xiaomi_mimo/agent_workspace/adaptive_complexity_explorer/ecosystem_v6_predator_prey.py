"""
Ecosystem V6 - Predator-Prey with Lotka-Volterra Dynamics
"""
import numpy as np
import json
import random

random.seed(42)
np.random.seed(42)

NGEN = 300

class Organism:
    def __init__(self, traits, energy):
        self.traits = dict(traits)
        self.energy = energy
        self.age = 0
    
    def metabolize(self, cost):
        self.energy -= cost
        self.age += 1
    
    def alive(self):
        return self.energy > 0

class Forager(Organism):
    def __init__(self, traits=None):
        if traits is None:
            traits = {
                'efficiency': random.uniform(0.5, 0.9),
                'speed': random.uniform(0.2, 0.6),
                'defense': random.uniform(0.3, 0.8),
                'repro': random.uniform(0.1, 0.25),
            }
        super().__init__(traits, 60.0)
    
    def forage(self, resources, resource_pool):
        # Foraging: gain energy proportional to efficiency and available resources
        availability = resource_pool / max(1.0, len(foragers) + 5)
        gain = self.traits['efficiency'] * availability * 0.3
        self.energy += min(gain, 15)  # Cap gain
        return min(gain, 15) * 0.3  # Return amount consumed
    
    def try_reproduce(self):
        if self.energy > 60 and self.age > 3:
            prob = self.traits['repro'] * min(1.0, self.energy / 80)
            if random.random() < prob:
                child_traits = {}
                for k, v in self.traits.items():
                    child_traits[k] = max(0.01, min(0.99, v + random.gauss(0, 0.03)))
                self.energy *= 0.5
                return Forager(child_traits)
        return None

class Hunter(Organism):
    def __init__(self, traits=None):
        if traits is None:
            traits = {
                'skill': random.uniform(0.3, 0.8),
                'speed': random.uniform(0.3, 0.7),
                'efficiency': random.uniform(0.3, 0.7),
                'repro': random.uniform(0.05, 0.15),
            }
        super().__init__(traits, 70.0)
    
    def hunt(self, foragers_list):
        # Hunting success depends on skill and prey density
        if not foragers_list:
            return False
        density_bonus = min(1.0, len(foragers_list) / 15.0)
        prey_defense = np.mean([f.traits['defense'] for f in foragers_list])
        success_prob = self.traits['skill'] * 0.08 * density_bonus * (1 - prey_defense * 0.4)
        if random.random() < success_prob:
            prey_idx = random.randint(0, len(foragers_list)-1)
            energy_gain = 15 + self.traits['efficiency'] * 10
            self.energy += energy_gain
            return True  # Hunted successfully
        return False
    
    def try_reproduce(self, prey_count):
        if self.energy > 70 and self.age > 6:
            prey_factor = min(1.0, prey_count / 12.0)
            prob = self.traits['repro'] * prey_factor * min(1.0, self.energy / 90)
            if random.random() < prob:
                child_traits = {}
                for k, v in self.traits.items():
                    child_traits[k] = max(0.01, min(0.99, v + random.gauss(0, 0.03)))
                self.energy *= 0.5
                return Hunter(child_traits)
        return None

# Initialize
foragers = [Forager() for _ in range(15)]
hunters = [Hunter() for _ in range(4)]
resource_pool = 200.0

history = []

for gen in range(NGEN):
    # Resource regeneration (exponential growth capped at carrying capacity)
    K = 400.0
    growth_rate = 0.08
    resource_pool = min(K, resource_pool + growth_rate * resource_pool * (1 - resource_pool / K))
    resource_pool = max(1.0, resource_pool)
    
    # Foragers: forage and metabolize
    total_consumed = 0
    surviving_foragers = []
    for f in foragers:
        f.metabolize(0.3 + f.traits['speed'] * 0.15)
        if f.alive():
            consumed = f.forage(None, resource_pool)
            total_consumed += consumed
            surviving_foragers.append(f)
    
    resource_pool -= total_consumed * 2  # Convert energy gain back to resource cost
    resource_pool = max(1.0, resource_pool)
    
    # Forager reproduction
    new_foragers = []
    for f in surviving_foragers:
        child = f.try_reproduce()
        if child and len(surviving_foragers) + len(new_foragers) < 60:
            new_foragers.append(child)
    surviving_foragers.extend(new_foragers)
    
    # Hunters: hunt and metabolize
    surviving_hunters = []
    successful_hunts = 0
    for h in hunters:
        h.metabolize(0.5 + h.traits['speed'] * 0.2)
        if h.alive():
            if h.hunt(surviving_foragers):
                successful_hunts += 1
                # Remove a random forager
                if surviving_foragers:
                    surviving_foragers.pop(random.randint(0, len(surviving_foragers)-1))
            surviving_hunters.append(h)
    
    # Hunter reproduction
    new_hunters = []
    for h in surviving_hunters:
        child = h.try_reproduce(len(surviving_foragers))
        if child and len(surviving_hunters) + len(new_hunters) < 15:
            new_hunters.append(child)
    surviving_hunters.extend(new_hunters)
    
    foragers = surviving_foragers
    hunters = surviving_hunters
    
    # Record
    nf, nh = len(foragers), len(hunters)
    
    def stats(orgs, keys):
        out = {}
        for k in keys:
            vals = [o.traits[k] for o in orgs if k in o.traits]
            out[k] = round(float(np.mean(vals)), 4) if vals else 0
        return out
    
    history.append({
        'gen': gen+1, 'nf': nf, 'nh': nh,
        'res': round(resource_pool, 1),
        'ft': stats(foragers, ['efficiency', 'speed', 'defense', 'repro']),
        'ht': stats(hunters, ['skill', 'speed', 'efficiency', 'repro']),
        'hunts': successful_hunts,
    })
    
    if (gen+1) % 50 == 0:
        print(f"Gen {gen+1:3d}: Foragers={nf:3d} Hunters={nh:2d} Resources={resource_pool:.0f} Hunts={successful_hunts}")

with open('history_v6_predator_prey.json', 'w') as f:
    json.dump(history, f)

final = history[-1]
print(f"\nFinal: Foragers={final['nf']}, Hunters={final['nh']}")
print(f"Forager traits: {final['ft']}")
print(f"Hunter traits: {final['ht']}")
print("Done!")
