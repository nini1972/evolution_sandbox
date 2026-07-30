import numpy as np

class Organism:
    def __init__(self, traits=None, generation=0):
        if traits is None:
            self.traits = np.random.uniform(0.2, 0.8, 5)
        else:
            self.traits = traits.copy()
        self.generation = generation
        self.energy = 1.0
        self.age = 0
        self.alive = True
        
    def energy_cost(self):
        """Higher speed = higher cost, but efficiency and frugality reduce cost"""
        base_cost = 0.15
        speed_penalty = self.traits[0] * 0.05
        efficiency_savings = self.traits[1] * 0.04
        frugality_savings = self.traits[4] * 0.05
        return max(0.05, base_cost + speed_penalty - efficiency_savings - frugality_savings)
        
    def mutate(self, mutation_rate=0.15, mutation_strength=0.1):
        mutated_traits = self.traits.copy()
        for i in range(len(mutated_traits)):
            if np.random.random() < mutation_rate:
                mutation = np.random.normal(0, mutation_strength)
                mutated_traits[i] = np.clip(mutated_traits[i] + mutation, 0.05, 1.5)
        return Organism(mutated_traits, self.generation + 1)
        
    def reproduce(self, resource_availability):
        """Reproduction requires sufficient energy and resources"""
        if self.energy > 1.0 and resource_availability > 0.4:
            # Cooperation trait: higher cooperation = easier reproduction threshold
            threshold = 1.2 - (self.traits[3] * 0.3)
            if self.energy > threshold:
                # Resource availability boosts reproduction
                base_prob = self.traits[2] * 0.2
                # Cooperation makes reproduction more likely in groups
                cooperation_bonus = self.traits[3] * 0.1
                total_prob = (base_prob + cooperation_bonus) * resource_availability
                if np.random.random() < min(total_prob, 0.4):
                    return self.mutate()
        return None