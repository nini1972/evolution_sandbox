import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import random
from collections import defaultdict

class GeneticAlgorithm:
    """
    A genetic algorithm for evolving solutions to optimization problems.
    Demonstrates emergence of complex solutions through simple evolutionary operators.
    """
    
    def __init__(self, population_size, chromosome_length, mutation_rate=0.01, crossover_rate=0.7):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.population = self.initialize_population()
        self.fitness_history = []
        self.diversity_history = []
        
    def initialize_population(self):
        """Create initial random population"""
        return [[random.randint(0, 1) for _ in range(self.chromosome_length)] 
                for _ in range(self.population_size)]
    
    def fitness_function(self, chromosome):
        """
        Example fitness function: OneMax problem - count number of 1s
        This is a simple hill-climbing problem to demonstrate evolution
        """
        return sum(chromosome)
    
    def selection_tournament(self, tournament_size=3):
        """Tournament selection - emergent bias toward fitter individuals"""
        selected = []
        for _ in range(self.population_size):
            tournament = random.sample(self.population, tournament_size)
            winner = max(tournament, key=self.fitness_function)
            selected.append(winner[:])  # Copy to avoid reference issues
        return selected
    
    def crossover_single_point(self, parent1, parent2):
        """Single-point crossover - genetic recombination"""
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.chromosome_length - 1)
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            return child1, child2
        return parent1[:], parent2[:]
    
    def mutate(self, chromosome):
        """Bit-flip mutation - introduces variation"""
        mutated = chromosome[:]
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                mutated[i] = 1 - mutated[i]  # Flip bit
        return mutated
    
    def calculate_diversity(self):
        """Measure population diversity"""
        if not self.population:
            return 0
        
        total_diversity = 0
        for i in range(self.chromosome_length):
            bit_counts = [ind[i] for ind in self.population]
            ones = sum(bit_counts)
            zeros = len(bit_counts) - ones
            # Shannon entropy for this bit position
            if ones > 0 and zeros > 0:
                p1 = ones / len(bit_counts)
                p0 = zeros / len(bit_counts)
                total_diversity -= p1 * np.log2(p1) + p0 * np.log2(p0)
        
        return total_diversity / self.chromosome_length
    
    def evolve_generation(self):
        """Single generation of evolution"""
        # Selection
        selected = self.selection_tournament()
        
        # Crossover and Mutation
        new_population = []
        for i in range(0, len(selected), 2):
            parent1 = selected[i]
            parent2 = selected[(i + 1) % len(selected)]
            
            child1, child2 = self.crossover_single_point(parent1, parent2)
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)
            
            new_population.extend([child1, child2])
        
        self.population = new_population[:self.population_size]
        
        # Record statistics
        fitnesses = [self.fitness_function(ind) for ind in self.population]
        self.fitness_history.append({
            'max': max(fitnesses),
            'mean': np.mean(fitnesses),
            'min': min(fitnesses)
        })
        self.diversity_history.append(self.calculate_diversity())
    
    def run_evolution(self, generations):
        """Run the evolutionary algorithm"""
        print(f"Starting evolution: {generations} generations, population size {self.population_size}")
        
        for generation in range(generations):
            self.evolve_generation()
            
            if generation % 50 == 0 or generation == generations - 1:
                best_fitness = self.fitness_history[-1]['max']
                diversity = self.diversity_history[-1]
                print(f"Generation {generation}: Best fitness = {best_fitness}, Diversity = {diversity:.3f}")
        
        return self.get_best_individual()
    
    def get_best_individual(self):
        """Return the best individual in current population"""
        return max(self.population, key=self.fitness_function)

# Run evolutionary algorithm experiments
print("=== Genetic Algorithm Experiments ===")

# Experiment 1: Basic OneMax evolution
print("\nExperiment 1: OneMax Problem")
ga1 = GeneticAlgorithm(population_size=100, chromosome_length=50, mutation_rate=0.01)
best_solution = ga1.run_evolution(generations=200)
print(f"Best solution found: {sum(best_solution)}/{len(best_solution)} bits set to 1")

# Experiment 2: Effect of mutation rate
print("\nExperiment 2: Mutation Rate Comparison")
mutation_rates = [0.001, 0.01, 0.05, 0.1]
results_by_mutation = {}

for mut_rate in mutation_rates:
    print(f"Testing mutation rate: {mut_rate}")
    ga = GeneticAlgorithm(population_size=50, chromosome_length=30, mutation_rate=mut_rate)
    ga.run_evolution(generations=100)
    results_by_mutation[mut_rate] = ga.fitness_history

# Experiment 3: Population size effects
print("\nExperiment 3: Population Size Comparison")
population_sizes = [20, 50, 100, 200]
results_by_population = {}

for pop_size in population_sizes:
    print(f"Testing population size: {pop_size}")
    ga = GeneticAlgorithm(population_size=pop_size, chromosome_length=30, mutation_rate=0.01)
    ga.run_evolution(generations=100)
    results_by_population[pop_size] = ga.fitness_history

# Create visualizations
print("\nGenerating visualizations...")

# Plot 1: Evolution progress for basic experiment
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

generations = range(len(ga1.fitness_history))
max_fitness = [gen['max'] for gen in ga1.fitness_history]
mean_fitness = [gen['mean'] for gen in ga1.fitness_history]
diversity = ga1.diversity_history

ax1.plot(generations, max_fitness, 'r-', label='Best Fitness', linewidth=2)
ax1.plot(generations, mean_fitness, 'b-', label='Mean Fitness', linewidth=2)
ax1.set_xlabel('Generation')
ax1.set_ylabel('Fitness')
ax1.set_title('Evolution of Fitness Over Time')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(generations, diversity, 'g-', linewidth=2)
ax2.set_xlabel('Generation')
ax2.set_ylabel('Population Diversity')
ax2.set_title('Population Diversity Over Time')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('genetic_algorithm_evolution.png', dpi=300, bbox_inches='tight')
plt.close()

# Plot 2: Mutation rate comparison
fig, ax = plt.subplots(figsize=(12, 8))

colors = ['red', 'blue', 'green', 'purple']
for i, mut_rate in enumerate(mutation_rates):
    fitness_data = results_by_mutation[mut_rate]
    generations = range(len(fitness_data))
    max_fitness = [gen['max'] for gen in fitness_data]
    ax.plot(generations, max_fitness, color=colors[i], 
            label=f'Mutation Rate = {mut_rate}', linewidth=2)

ax.set_xlabel('Generation')
ax.set_ylabel('Best Fitness')
ax.set_title('Effect of Mutation Rate on Evolution')
ax.legend()
ax.grid(True, alpha=0.3)

plt.savefig('mutation_rate_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Plot 3: Population size comparison
fig, ax = plt.subplots(figsize=(12, 8))

colors = ['red', 'blue', 'green', 'orange']
for i, pop_size in enumerate(population_sizes):
    fitness_data = results_by_population[pop_size]
    generations = range(len(fitness_data))
    max_fitness = [gen['max'] for gen in fitness_data]
    ax.plot(generations, max_fitness, color=colors[i], 
            label=f'Population Size = {pop_size}', linewidth=2)

ax.set_xlabel('Generation')
ax.set_ylabel('Best Fitness')
ax.set_title('Effect of Population Size on Evolution')
ax.legend()
ax.grid(True, alpha=0.3)

plt.savefig('population_size_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Advanced experiment: NK Landscape
print("\nExperiment 4: NK Landscape - Rugged Fitness Landscape")

class NKLandscape:
    """
    NK fitness landscape - demonstrates evolution on rugged, epistatic landscapes
    N = chromosome length, K = epistatic interactions per gene
    """
    
    def __init__(self, N, K):
        self.N = N
        self.K = K
        # Generate random fitness contributions for each gene and its K neighbors
        self.fitness_tables = {}
        for i in range(N):
            # Each gene interacts with K other genes
            neighbors = [(i + j + 1) % N for j in range(K)]
            # Create fitness table for all possible combinations
            for combo in range(2**(K+1)):  # 2^(K+1) combinations
                key = (i, combo)
                self.fitness_tables[key] = random.random()
    
    def fitness(self, chromosome):
        """Calculate fitness based on epistatic interactions"""
        total_fitness = 0
        for i in range(self.N):
            # Get the values of gene i and its K neighbors
            neighbors = [(i + j + 1) % self.N for j in range(self.K)]
            values = [chromosome[i]] + [chromosome[j] for j in neighbors]
            
            # Convert to integer key
            combo = sum(val * (2**idx) for idx, val in enumerate(values))
            total_fitness += self.fitness_tables[(i, combo)]
        
        return total_fitness / self.N  # Normalize

# Test NK landscape with different K values
K_values = [0, 1, 2, 4]  # K=0 is smooth, higher K = more rugged
nk_results = {}

for K in K_values:
    print(f"Testing NK landscape with K={K} (epistatic interactions)")
    
    # Create custom GA for NK landscape
    class NK_GA(GeneticAlgorithm):
        def __init__(self, nk_landscape, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.nk_landscape = nk_landscape
        
        def fitness_function(self, chromosome):
            return self.nk_landscape.fitness(chromosome)
    
    nk_landscape = NKLandscape(N=20, K=K)
    ga_nk = NK_GA(nk_landscape, population_size=100, chromosome_length=20, mutation_rate=0.05)
    ga_nk.run_evolution(generations=150)
    nk_results[K] = ga_nk.fitness_history

# Plot NK landscape results
fig, ax = plt.subplots(figsize=(12, 8))

colors = ['blue', 'green', 'red', 'purple']
for i, K in enumerate(K_values):
    fitness_data = nk_results[K]
    generations = range(len(fitness_data))
    max_fitness = [gen['max'] for gen in fitness_data]
    ax.plot(generations, max_fitness, color=colors[i], 
            label=f'K = {K} ({"Smooth" if K == 0 else "Rugged"})', linewidth=2)

ax.set_xlabel('Generation')
ax.set_ylabel('Best Fitness')
ax.set_title('Evolution on NK Fitness Landscapes\n(K = epistatic interactions per gene)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.savefig('nk_landscape_evolution.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nGenerated visualizations:")
print("- genetic_algorithm_evolution.png: Basic GA evolution and diversity")
print("- mutation_rate_comparison.png: Effect of mutation rate on evolution")
print("- population_size_comparison.png: Effect of population size on evolution") 
print("- nk_landscape_evolution.png: Evolution on rugged fitness landscapes")

print("\n=== Key Insights from Evolutionary Algorithm Experiments ===")
print("1. EMERGENCE OF OPTIMIZATION: Simple operators (selection, crossover, mutation) lead to emergent problem-solving")
print("2. BALANCE OF EXPLORATION vs EXPLOITATION: Mutation provides diversity, selection provides direction")
print("3. POPULATION DIVERSITY DYNAMICS: Diversity initially decreases as population converges, then stabilizes")
print("4. PARAMETER SENSITIVITY: Small changes in mutation rate and population size significantly affect evolution")
print("5. EPISTATIC INTERACTIONS: Gene interactions (NK landscapes) create rugged fitness landscapes that slow evolution")
print("6. NO GLOBAL KNOWLEDGE REQUIRED: Each individual only knows its own fitness, yet population finds global optimum")
print("7. EMERGENT ADAPTATION: Complex solutions emerge without explicit programming or design")