"""
Ecosystem V6 - Predator-Prey Dynamics
Two species with different strategies: efficient foragers vs fast hunters
"""
import numpy as np
import json
import random
import uuid
from collections import defaultdict


class Organism:
    def __init__(self, x, y, species, genome=None):
        self.id = str(uuid.uuid4())[:8]
        self.x = x
        self.y = y
        self.species = species  # 'forager' or 'hunter'
        self.age = 0
        self.energy = 60.0 if species == 'forager' else 80.0
        self.is_alive = True
        if genome is None:
            if species == 'forager':
                self.genome = {
                    'speed': random.uniform(0.2, 0.8),
                    'efficiency': random.uniform(0.4, 1.0),
                    'reproduction': random.uniform(0.15, 0.45),
                    'cooperation': random.uniform(0.3, 0.9),
                    'frugality': random.uniform(0.4, 1.0),
                    'defense': random.uniform(0.2, 0.8),
                    'awareness': random.uniform(0.2, 0.8),
                }
            else:  # hunter
                self.genome = {
                    'speed': random.uniform(0.5, 1.0),
                    'hunting_skill': random.uniform(0.3, 1.0),
                    'reproduction': random.uniform(0.1, 0.4),
                    'cooperation': random.uniform(0.0, 0.6),
                    'stealth': random.uniform(0.3, 0.9),
                    'stamina': random.uniform(0.3, 0.9),
                    'awareness': random.uniform(0.3, 0.9),
                }
        else:
            self.genome = genome.copy()
        self.offspring_count = 0
        
    def metabolic_cost(self):
        if self.species == 'forager':
            return 0.4 + self.genome['speed'] * 0.3
        else:
            return 0.6 + self.genome['speed'] * 0.5 + self.genome['stamina'] * 0.2


class PredatorPreyWorld:
    def __init__(self, width=30, height=30):
        self.width = width
        self.height = height
        self.grid_resources = np.full((height, width), 100.0)
        self.organisms = []
        self.generation = 0
        self.history = []
        self.spatial_index = defaultdict(list)
        self.migration_events = []
        
    def seed_organisms(self, n_foragers=40, n_hunters=15):
        for _ in range(n_foragers):
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            self.organisms.append(Organism(x, y, 'forager'))
        for _ in range(n_hunters):
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            self.organisms.append(Organism(x, y, 'hunter'))
        self.rebuild_index()
        
    def rebuild_index(self):
        self.spatial_index = defaultdict(list)
        for o in self.organisms:
            if o.is_alive:
                self.spatial_index[(o.x, o.y)].append(o)
                
    def step(self):
        self.generation += 1
        
        # Resource regrowth
        growth = self.grid_resources * 0.015 + 0.3
        self.grid_resources = np.minimum(100.0, self.grid_resources + growth)
        
        # Phase 1: Hunters hunt
        for org in self.organisms:
            if org.species == 'hunter' and org.is_alive:
                self.hunt(org)
                
        # Phase 2: All organisms act
        new_borns = []
        
        for org in self.organisms:
            if not org.is_alive:
                continue
                
            org.age += 1
            
            # Metabolic cost
            org.energy -= org.metabolic_cost()
            
            if org.energy <= 0:
                org.is_alive = False
                continue
                
            # Foragers gather resources
            if org.species == 'forager':
                self.forage(org)
                
            # Cooperation
            if org.genome.get('cooperation', 0) > 0.5 and org.energy > 35:
                self.cooperate(org)
                
            # Movement
            self.move(org)
            
            # Reproduction
            child = self.reproduce(org)
            if child:
                new_borns.append(child)
                
        # Remove dead
        self.organisms = [o for o in self.organisms if o.is_alive]
        
        # Add newborns
        self.organisms.extend(new_borns)
        self.rebuild_index()
        
        # Record
        self.record_state()
        
    def hunt(self, hunter):
        """Hunter attempts to catch a nearby forager"""
        if hunter.energy < 20:
            return
            
        hunting_range = int(hunter.genome['stealth'] * 3) + 1
        
        for dx in range(-hunting_range, hunting_range + 1):
            for dy in range(-hunting_range, hunting_range + 1):
                if dx == 0 and dy == 0:
                    continue
                nx = (hunter.x + dx) % self.width
                ny = (hunter.y + dy) % self.height
                
                for prey in self.spatial_index.get((nx, ny), []):
                    if prey.species == 'forager' and prey.is_alive:
                        # Hunt success probability
                        success_prob = (hunter.genome['hunting_skill'] * 0.4 +
                                       hunter.genome['speed'] * 0.3 +
                                       hunter.genome['stealth'] * 0.3)
                        defense = prey.genome.get('defense', 0.5)
                        
                        if random.random() < success_prob * (1 - defense * 0.5):
                            # Successful hunt!
                            prey.is_alive = False
                            hunter.energy += 30 * hunter.genome['hunting_skill']
                            return
                            
    def forage(self, forager):
        """Forager gathers resources from current location"""
        available = self.grid_resources[forager.y, forager.x]
        if available > 1.0:
            consumed = min(available, 4.0 * forager.genome['efficiency'])
            forager.energy += consumed * forager.genome['efficiency'] * 0.7
            self.grid_resources[forager.y, forager.x] -= consumed
            
    def cooperate(self, org):
        """Share energy with nearby ally - simplified"""
        if org.energy < 25:
            return
        # Just check 4 neighbors
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx = (org.x + dx) % self.width
            ny = (org.y + dy) % self.height
            for neighbor in self.spatial_index.get((nx, ny), []):
                if (neighbor.species == org.species and 
                    neighbor.is_alive and 
                    neighbor.energy < 30):
                    share = min(3.0, org.energy * 0.1)
                    org.energy -= share
                    neighbor.energy += share
                    return  # Only share once per turn
                        
    def move(self, org):
        """Move toward better resources or avoid predators"""
        if org.genome['speed'] < 0.3 or org.energy < 10:
            return
            
        awareness = min(int(org.genome['awareness'] * 2) + 1, 3)  # Cap at 3
        best_dir = (0, 0)
        best_val = -1000
        
        # Sample directions instead of checking all
        dirs_to_check = [(0, 0)]
        for _ in range(5):
            dx = random.randint(-awareness, awareness)
            dy = random.randint(-awareness, awareness)
            dirs_to_check.append((dx, dy))
        
        for dx, dy in dirs_to_check:
            nx = (org.x + dx) % self.width
            ny = (org.y + dy) % self.height
            
            if org.species == 'forager':
                val = self.grid_resources[ny, nx] * 0.5
                # Quick check nearby for hunters
                for o in self.spatial_index.get((nx, ny), []):
                    if o.species == 'hunter' and o.is_alive:
                        val -= 50
            else:
                val = 0
                for o in self.spatial_index.get((nx, ny), []):
                    if o.species == 'forager' and o.is_alive:
                        val += 10
                        
            if val > best_val:
                best_val = val
                best_dir = (dx, dy)
                
        if random.random() < org.genome['speed'] * 0.6:
            move_x = max(-1, min(1, best_dir[0]))
            move_y = max(-1, min(1, best_dir[1]))
            org.x = (org.x + move_x) % self.width
            org.y = (org.y + move_y) % self.height
            org.energy -= 0.3
            
    def reproduce(self, org):
        """Attempt to reproduce"""
        repro_threshold = org.genome['reproduction'] * 120
        
        if org.energy > repro_threshold and org.age > 8:
            child_genome = {}
            for key, val in org.genome.items():
                child_genome[key] = val + random.gauss(0, 0.04)
                child_genome[key] = max(0.01, min(1.0, child_genome[key]))
                
            # Occasional larger mutation
            if random.random() < 0.25:
                key = random.choice(list(child_genome.keys()))
                child_genome[key] = max(0.01, min(1.0,
                    child_genome[key] + random.gauss(0, 0.1)))
                    
            child = Organism(org.x, org.y, org.species, child_genome)
            org.energy *= 0.45
            org.offspring_count += 1
            return child
            
        return None
        
    def record_state(self):
        foragers = [o for o in self.organisms if o.species == 'forager']
        hunters = [o for o in self.organisms if o.species == 'hunter']
        
        def trait_stats(orgs, traits):
            stats = {}
            for t in traits:
                vals = [o.genome[t] for o in orgs if t in o.genome]
                stats[f'avg_{t}'] = float(np.mean(vals)) if vals else 0
                stats[f'std_{t}'] = float(np.std(vals)) if len(vals) > 1 else 0
            return stats
            
        forager_traits = ['speed', 'efficiency', 'cooperation', 'frugality', 'defense', 'awareness']
        hunter_traits = ['speed', 'hunting_skill', 'cooperation', 'stealth', 'stamina', 'awareness']
        
        self.history.append({
            'generation': self.generation,
            'forager_count': len(foragers),
            'hunter_count': len(hunters),
            'total_population': len(self.organisms),
            'forager_avg_energy': float(np.mean([o.energy for o in foragers])) if foragers else 0,
            'hunter_avg_energy': float(np.mean([o.energy for o in hunters])) if hunters else 0,
            'forager_traits': trait_stats(foragers, forager_traits),
            'hunter_traits': trait_stats(hunters, hunter_traits),
            'resources_avg': float(np.mean(self.grid_resources)),
        })
        
    def run(self, generations=500):
        for i in range(generations):
            self.step()
            if (i + 1) % 100 == 0:
                f = self.history[-1]['forager_count']
                h = self.history[-1]['hunter_count']
                print(f"Gen {i+1}: Foragers={f}, Hunters={h}, "
                      f"Resources={self.history[-1]['resources_avg']:.1f}")


if __name__ == '__main__':
    print("="*60)
    print("ECOSYSTEM V6 - PREDATOR-PREY DYNAMICS")
    print("="*60)
    print("Species: Foragers (efficient, cooperative) vs Hunters (fast, stealthy)")
    print("="*60)
    
    world = PredatorPreyWorld(width=30, height=30)
    world.seed_organisms(n_foragers=40, n_hunters=15)
    print("Starting simulation...")
    world.run(generations=300)  # Reduced from 500
    
    with open('history_v6_predator_prey.json', 'w') as f:
        json.dump(world.history, f)
    print("\nSaved history_v6_predator_prey.json")
    
    # Final stats
    final = world.history[-1]
    print(f"\nFinal Stats:")
    print(f"  Foragers: {final['forager_count']}")
    print(f"  Hunters: {final['hunter_count']}")
    print(f"  Forager Energy: {final['forager_avg_energy']:.2f}")
    print(f"  Hunter Energy: {final['hunter_avg_energy']:.2f}")
    print(f"\nForager Traits:")
    for k, v in final['forager_traits'].items():
        if k.startswith('avg_'):
            print(f"  {k[4:]}: {v:.3f}")
    print(f"\nHunter Traits:")
    for k, v in final['hunter_traits'].items():
        if k.startswith('avg_'):
            print(f"  {k[4:]}: {v:.3f}")
