import numpy as np
import matplotlib.pyplot as plt

# Define the objective function
def objective_function(x):
    return np.sin(x) + np.cos(2*x)

# Genetic algorithm parameters
population_size = 100
num_generations = 100
mutation_rate = 0.1

# Initialize the population
population = np.random.uniform(-np.pi, np.pi, size=(population_size, 1))

# Evaluate the initial population
fitness = objective_function(population)

# Track the best solution
best_solution = population[np.argmax(fitness)]
best_fitness = np.max(fitness)

# Optimize using a genetic algorithm
fitness_history = []
for generation in range(num_generations):
    # Selection
    parents = np.random.choice(population_size, size=(population_size // 2, 2), p=fitness / fitness.sum())

    # Crossover
    offspring = np.zeros((population_size, 1))
    for i, (p1, p2) in enumerate(parents):
        offspring[2*i] = population[p1]
        offspring[2*i + 1] = population[p2]

    # Mutation
    offspring += mutation_rate * np.random.normal(0, 1, size=offspring.shape)

    # Evaluate the offspring
    new_fitness = objective_function(offspring)

    # Update the population
    population = np.concatenate((population, offspring))
    fitness = np.concatenate((fitness, new_fitness))
    indices = np.argsort(fitness)[-population_size:]
    population = population[indices]
    fitness = fitness[indices]

    # Track the best solution
    best_solution = population[np.argmax(fitness)]
    best_fitness = np.max(fitness)
    fitness_history.append(best_fitness)

# Plot the optimization progress
plt.figure(figsize=(8, 6))
plt.plot(fitness_history)
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Genetic Algorithm Optimization')
plt.savefig('genetic_algorithm_progress.png')
print(f"Global optimum: x={best_solution[0]:.3f}, y={best_fitness:.3f}")