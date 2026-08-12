"""
Ecosystem V5 - High Mutation Variant
Exploring how increased mutation rates affect evolutionary dynamics
"""
import numpy as np
import json
import random
import uuid
from collections import defaultdict


class SpatialOrganism:
    def __init__(self, x, y, genome=None):
        self.id = str(uuid.uuid4())[:8]
        self.x = x
        self.y = y
        self.age = 0
        self.energy = 50.0
        if genome is None:
            self.genome = {
                'speed': random.uniform(0.1, 1.0),
                'efficiency': random.uniform(0.2, 1.0),
                'reproduction': random.uniform(0.1, 0.5),
                'cooperation': random.uniform(0.0, 1.0),
                'frugality': random.uniform(0.2, 1.0),
                'aggression': random.uniform(0.0, 1.0),
                'awareness': random.uniform(0.1, 1.0),
                'mutation_rate': random.uniform(0.05, 0.4),  # HIGHER MUTATION
            }
        else:
            self.genome = genome.copy()
        self.offspring_count = 0

    def mutate(self):
        for key in self.genome:
            if random.random() < self.genome['mutation_rate']:
                # Larger mutation step for high mutation variant
                delta = random.gauss(0, 0.08)
                self.genome[key] = max(0.01, min(1.0, self.genome[key] + delta))


class SpatialWorld:
    def __init__(self, width=25, height=25):
        self.width = width
        self.height = height
        self.grid_resources = np.full((height, width), 80.0)
        self.organisms = []
        self.generation = 0
        self.history = []
        self.spatial_index = defaultdict(list)

    def seed_organisms(self, n=30):
        for _ in range(n):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            org = SpatialOrganism(x, y)
            self.organisms.append(org)
            self.spatial_index[(x, y)].append(org)

    def rebuild_index(self):
        self.spatial_index = defaultdict(list)
        for o in self.organisms:
            self.spatial_index[(o.x, o.y)].append(o)

    def step(self):
        self.generation += 1

        # Resource regrowth
        growth = self.grid_resources * 0.02 + 0.5
        self.grid_resources = np.minimum(100.0, self.grid_resources + growth)

        dead = []
        new_borns = []

        random.shuffle(self.organisms)

        for org in self.organisms:
            org.age += 1

            # Metabolic cost
            met_cost = 0.3 + org.genome['speed'] * 0.4 + org.genome['awareness'] * 0.15
            org.energy -= met_cost

            if org.energy <= 0:
                dead.append(org)
                continue

            # Consume resources
            available = self.grid_resources[org.y, org.x]
            if available > 0.5:
                consumed = min(available, 5.0 * org.genome['efficiency'])
                org.energy += consumed * org.genome['efficiency']
                self.grid_resources[org.y, org.x] -= consumed

            # Cooperation - share with one nearby ally
            if org.genome['cooperation'] > 0.6 and org.energy > 30:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        nx = (org.x + dx) % self.width
                        ny = (org.y + dy) % self.height
                        neighbors = self.spatial_index.get((nx, ny), [])
                        for o in neighbors:
                            if o.genome['cooperation'] > 0.6 and o.energy < 30:
                                share = min(3.0, org.energy * 0.1)
                                org.energy -= share
                                o.energy += share
                                break
                        else:
                            continue
                        break
                    else:
                        continue
                    break

            # Aggression
            if org.genome['aggression'] > 0.7 and random.random() < 0.1:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        nx = (org.x + dx) % self.width
                        ny = (org.y + dy) % self.height
                        neighbors = self.spatial_index.get((nx, ny), [])
                        for o in neighbors:
                            if org.genome['speed'] > o.genome['speed']:
                                o.energy -= 5.0
                                org.energy += 2.0
                                break
                        else:
                            continue
                        break
                    else:
                        continue
                    break

            # Movement
            if org.genome['speed'] > 0.3 and org.energy > 15:
                best_dir = (0, 0)
                best_val = self.grid_resources[org.y, org.x]
                awareness = int(org.genome['awareness'] * 2) + 1

                for dx in range(-awareness, awareness + 1):
                    for dy in range(-awareness, awareness + 1):
                        nx = (org.x + dx) % self.width
                        ny = (org.y + dy) % self.height
                        val = self.grid_resources[ny, nx]
                        crowded = len(self.spatial_index.get((nx, ny), []))
                        val -= crowded * org.genome['frugality'] * 2
                        if val > best_val:
                            best_val = val
                            best_dir = (dx, dy)

                if random.random() < org.genome['speed'] * 0.5:
                    move_x = max(-1, min(1, best_dir[0]))
                    move_y = max(-1, min(1, best_dir[1]))
                    old_pos = (org.x, org.y)
                    if org in self.spatial_index.get(old_pos, []):
                        self.spatial_index[old_pos].remove(org)
                    org.x = (org.x + move_x) % self.width
                    org.y = (org.y + move_y) % self.height
                    self.spatial_index[(org.x, org.y)].append(org)
                    org.energy -= 0.5

            # Reproduction
            local_density = sum(
                len(self.spatial_index.get(((org.x + dx) % self.width, (org.y + dy) % self.height), []))
                for dx in range(-2, 3) for dy in range(-2, 3)
            )

            if (org.energy > org.genome['reproduction'] * 150 and
                org.age > 10 and local_density < 12):

                child_genome = {}
                for key, val in org.genome.items():
                    # HIGHER mutation in offspring for V5
                    child_genome[key] = val + random.gauss(0, 0.06)
                    child_genome[key] = max(0.01, min(1.0, child_genome[key]))

                # More frequent large mutations
                if random.random() < 0.5:  # 50% vs 30% in V4
                    key = random.choice(list(child_genome.keys()))
                    child_genome[key] = max(0.01, min(1.0,
                        child_genome[key] + random.gauss(0, 0.15)))

                child = SpatialOrganism(org.x, org.y, child_genome)
                org.energy *= 0.5
                org.offspring_count += 1
                new_borns.append(child)
                self.spatial_index[(org.x, org.y)].append(child)

        # Remove dead
        for org in dead:
            if org in self.organisms:
                self.organisms.remove(org)
            pos = (org.x, org.y)
            if pos in self.spatial_index and org in self.spatial_index[pos]:
                self.spatial_index[pos].remove(org)

        # Add newborns
        self.organisms.extend(new_borns)

        self.record_state()

    def record_state(self):
        if not self.organisms:
            self.history.append({
                'generation': self.generation,
                'population': 0,
                'avg_energy': 0,
                'diversity': 0,
                'spatial_spread': 0,
                'traits': {}
            })
            return

        energies = [o.energy for o in self.organisms]
        pop = len(self.organisms)

        trait_vars = {}
        for trait in ['speed', 'efficiency', 'cooperation', 'frugality',
                      'aggression', 'awareness']:
            vals = [o.genome[trait] for o in self.organisms]
            trait_vars[trait] = float(np.std(vals)) if len(vals) > 1 else 0

        diversity = float(np.mean(list(trait_vars.values())))

        xs = [o.x for o in self.organisms]
        ys = [o.y for o in self.organisms]
        if pop > 1:
            mean_x = np.mean(xs)
            mean_y = np.mean(ys)
            spread = float(np.mean([np.sqrt((x - mean_x)**2 + (y - mean_y)**2)
                            for x, y in zip(xs, ys)]))
        else:
            spread = 0

        self.history.append({
            'generation': self.generation,
            'population': pop,
            'avg_energy': float(np.mean(energies)),
            'diversity': diversity,
            'spatial_spread': spread,
            'traits': {
                'avg_speed': float(np.mean([o.genome['speed'] for o in self.organisms])),
                'avg_efficiency': float(np.mean([o.genome['efficiency'] for o in self.organisms])),
                'avg_cooperation': float(np.mean([o.genome['cooperation'] for o in self.organisms])),
                'avg_frugality': float(np.mean([o.genome['frugality'] for o in self.organisms])),
                'avg_aggression': float(np.mean([o.genome['aggression'] for o in self.organisms])),
                'avg_awareness': float(np.mean([o.genome['awareness'] for o in self.organisms])),
            }
        })

    def run(self, generations=600):
        for i in range(generations):
            self.step()
            if (i + 1) % 100 == 0:
                print(f"Gen {i+1}: pop={len(self.organisms)}, "
                      f"diversity={self.history[-1]['diversity']:.3f}, "
                      f"spread={self.history[-1]['spatial_spread']:.1f}")


if __name__ == '__main__':
    print("="*60)
    print("ECOSYSTEM V5 - HIGH MUTATION VARIANT")
    print("="*60)
    print("Mutation rates: 0.05-0.4 (vs 0.01-0.2 in V4)")
    print("Mutation step: 0.08 (vs 0.05 in V4)")
    print("Large mutation chance: 50% (vs 30% in V4)")
    print("="*60)
    
    world = SpatialWorld(width=25, height=25)
    world.seed_organisms(n=30)
    print("Starting V5 High Mutation simulation...")
    world.run(generations=600)

    with open('history_v5_high_mutation.json', 'w') as f:
        json.dump(world.history, f)
    print("\nSaved history_v5_high_mutation.json")
    
    # Print final stats
    final = world.history[-1]
    print(f"\nFinal Stats:")
    print(f"  Population: {final['population']}")
    print(f"  Avg Energy: {final['avg_energy']:.2f}")
    print(f"  Diversity: {final['diversity']:.3f}")
    print(f"  Spatial Spread: {final['spatial_spread']:.2f}")
    print(f"\nFinal Traits:")
    for trait, value in final['traits'].items():
        print(f"  {trait}: {value:.3f}")
