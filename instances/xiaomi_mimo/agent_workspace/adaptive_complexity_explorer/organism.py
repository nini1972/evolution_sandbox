import numpy as np

class Organism:
    def __init__(self, traits=None, generation=0):
        if traits is None:
            self.traits = np.random.uniform(0.1, 1.0, 4)
        else:
            self.traits = traits.copy()
        self.generation = generation
        self.energy = 1.0
        self.age = 0
        self.alive = True
        
    def mutate(self, mutation_rate=0.1, mutation_strength=0.2):
        mutated_traits = self.traits.copy()
        for i in range(len(mutated_traits)):
            if np.random.random() < mutation_rate:
                mutation = np.random.normal(0, mutation_strength)
                mutated_traits[i] = np.clip(mutated_traits[i] + mutation, 0.01, 2.0)
        return Organism(mutated_traits, self.generation + 1)
        
    def energy_cost(self):
        speed_cost = self.traits[0] * 0.1
        efficiency_benefit = self.traits[1] * 0.05
        return speed_cost - efficiency_benefit
        
    def reproduce(self, resource_availability):
        if self.energy > 0.8 and resource_availability > 0.3:
            if np.random.random() < self.traits[2] * 0.3:
                return self.mutate()
        return None