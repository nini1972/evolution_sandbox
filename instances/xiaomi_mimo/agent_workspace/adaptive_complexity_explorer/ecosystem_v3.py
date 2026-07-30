import numpy as np
from organism_v3 import Organism

class Resource:
    def __init__(self, amount=100.0, regrowth_rate=5.0):
        self.amount = amount
        self.max_amount = amount
        self.regrowth_rate = regrowth_rate

    def consume(self, amount):
        consumed = min(amount, self.amount)
        self.amount -= consumed
        return consumed

    def regrow(self):
        growth = self.regrowth_rate * (self.amount / self.max_amount)
        self.amount = min(self.max_amount, self.amount + growth)

    def shock(self, severity=0.5):
        self.amount *= (1.0 - severity)

class Ecosystem:
    def __init__(self, initial_population=30, max_resources=300):
        self.organisms = [Organism() for _ in range(initial_population)]
        self.resources = Resource(max_resources, regrowth_rate=20.0)
        self.generation = 0
        self.history = {
            'generation': [], 'population': [],
            'avg_speed': [], 'avg_efficiency': [], 'avg_reproduction': [],
            'avg_cooperation': [], 'avg_frugality': [], 'avg_energy': [],
            'resource_level': [], 'diversity': [],
            'extinction_events': [], 'boom_events': []
        }

    def calculate_diversity(self):
        alive = [o for o in self.organisms if o.alive]
        if len(alive) < 2:
            return 0.0
        traits = np.array([o.traits for o in alive])
        return float(np.mean(np.std(traits, axis=0)))

    def competition_round(self):
        alive = [o for o in self.organisms if o.alive]
        if not alive:
            return
        self.resources.regrow()
        if np.random.random() < 0.03:
            severity = np.random.uniform(0.2, 0.6)
            self.resources.shock(severity)
        for org in alive:
            org.energy -= org.energy_cost()
            org.age += 1
            # Energy gathering: higher speed = more gathered
            base_gather = 0.5 + (org.traits[0] * 0.4)
            # Competition reduces per capita availability
            comp_factor = 1.0 / (1.0 + len(alive) * 0.005)
            gathered = base_gather * comp_factor
            consumed = self.resources.consume(gathered)
            # Convert resources to energy
            org.energy += consumed * 1.0
            # Efficiency trait improves energy retention
            org.energy *= (0.90 + org.traits[1] * 0.10)
            # Cooperation bonus
            org.energy += org.traits[3] * 0.04
            # Clamp energy
            org.energy = max(0.0, min(org.energy, 5.0))
            if org.energy <= 0 or org.age > 80:
                org.alive = False
        alive_count = len([o for o in self.organisms if o.alive])
        if alive_count > 0 and alive_count < 5:
            self.history['extinction_events'].append(self.generation)

    def reproduction_phase(self):
        new_organisms = []
        alive = [o for o in self.organisms if o.alive]
        resource_avail = self.resources.amount / self.resources.max_amount
        for org in alive:
            offspring = org.reproduce(resource_avail)
            if offspring is not None:
                new_organisms.append(offspring)
        self.organisms.extend(new_organisms)
        if len(self.organisms) > 500:
            self.organisms = [o for o in self.organisms if o.alive][-300:]

    def record_history(self):
        alive = [o for o in self.organisms if o.alive]
        if not alive:
            return
        traits = np.array([o.traits for o in alive])
        energies = [o.energy for o in alive]
        self.history['generation'].append(self.generation)
        self.history['population'].append(len(alive))
        self.history['avg_speed'].append(float(np.mean(traits[:, 0])))
        self.history['avg_efficiency'].append(float(np.mean(traits[:, 1])))
        self.history['avg_reproduction'].append(float(np.mean(traits[:, 2])))
        self.history['avg_cooperation'].append(float(np.mean(traits[:, 3])))
        self.history['avg_frugality'].append(float(np.mean(traits[:, 4])))
        self.history['avg_energy'].append(float(np.mean(energies)))
        self.history['resource_level'].append(self.resources.amount)
        self.history['diversity'].append(self.calculate_diversity())