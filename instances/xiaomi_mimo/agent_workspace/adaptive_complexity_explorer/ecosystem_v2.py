import numpy as np
from organism_v2 import Organism
from resource_v2 import Resource

class Ecosystem:
    def __init__(self, initial_population=50, max_resources=100):
        self.organisms = [Organism() for _ in range(initial_population)]
        self.resources = Resource(max_resources, max_resources * 0.08)
        self.generation = 0
        self.history = {
            'population': [], 'avg_speed': [], 'avg_efficiency': [],
            'avg_reproduction': [], 'avg_cooperation': [], 'avg_frugality': [],
            'avg_energy': [], 'resource_level': [], 'generation': [],
            'extinction_events': [], 'boom_events': []
        }
        self.pop_trend = 0
        
    def apply_environmental_shock(self):
        if np.random.random() < 0.02:
            shock_type = np.random.choice(['drought', 'abundance'])
            if shock_type == 'drought':
                self.resources.amount *= 0.3
                self.history['extinction_events'].append(self.generation)
            else:
                self.resources.amount = min(self.resources.max_amount, self.resources.amount * 1.5)
                self.history['boom_events'].append(self.generation)
                
    def competition_round(self):
        self.resources.regrow()
        self.apply_environmental_shock()
        if self.organisms:
            self.organisms.sort(key=lambda o: o.traits[0], reverse=True)
        for org in self.organisms:
            if not org.alive:
                continue
            org.energy -= org.energy_cost()
            demand_mod = 1.0 - (org.traits[4] * 0.3)
            resource_demand = org.traits[0] * 0.15 * demand_mod
            actual_consumption = self.resources.consume(resource_demand)
            energy_gain = actual_consumption * org.traits[1] * 0.5
            org.energy += energy_gain
            org.age += 1
            if org.energy <= 0 or org.age > 50:
                org.alive = False
                
    def reproduction_phase(self):
        new_organisms = []
        resource_availability = self.resources.amount / self.resources.max_amount
        for org in self.organisms:
            if org.alive:
                offspring = org.reproduce(resource_availability)
                if offspring:
                    new_organisms.append(offspring)
        self.organisms.extend(new_organisms)
        self.organisms = [org for org in self.organisms if org.alive]
        
    def record_history(self):
        alive_orgs = [org for org in self.organisms if org.alive]
        self.history['generation'].append(self.generation)
        self.history['population'].append(len(alive_orgs))
        if alive_orgs:
            avg_traits = np.mean([org.traits for org in alive_orgs], axis=0)
            self.history['avg_speed'].append(avg_traits[0])
            self.history['avg_efficiency'].append(avg_traits[1])
            self.history['avg_reproduction'].append(avg_traits[2])
            self.history['avg_cooperation'].append(avg_traits[3])
            self.history['avg_frugality'].append(avg_traits[4])
            avg_energy = np.mean([org.energy for org in alive_orgs])
            self.history['avg_energy'].append(avg_energy)
        else:
            for key in ['avg_speed', 'avg_efficiency', 'avg_reproduction', 'avg_cooperation', 'avg_frugality', 'avg_energy']:
                self.history[key].append(0)
        self.history['resource_level'].append(self.resources.amount)