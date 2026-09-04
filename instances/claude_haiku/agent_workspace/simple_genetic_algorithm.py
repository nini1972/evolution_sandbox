import numpy as np

# Define the objective function
def objective_function(x):
    return x[0]**2 + (x[1] - 1)**2

# Define the genetic algorithm parameters
population_size = 100
num_generations = 100
mutation_rate = 0.1
tournament_size = 3

# Initialize the population
population = np.random.uniform(-5, 5, (population_size, 2))

# Evaluate the initial population
fitness = [objective_function(individual) for individual in population]

# Run the genetic algorithm
for generation in range(num_generations):
    # Selection (Tournament Selection)
    selected_indices = np.random.choice(population_size, size=(population_size,), replace=True)
    selected_population = population[selected_indices]
    selected_fitness = [fitness[i] for i in selected_indices]
    parents = selected_population[np.argsort(selected_fitness)[:2]]

    # Crossover (Single Point Crossover)
    offspring = np.zeros((population_size, 2))
    for i in range(0, population_size, 2):
        crossover_point = np.random.randint(1, 2)
        offspring[i] = np.concatenate((parents[0][:crossover_point], parents[1][crossover_point:]))
        offspring[i + 1] = np.concatenate((parents[1][:crossover_point], parents[0][crossover_point:]))

    # Mutation (Gaussian Mutation)
    for i in range(population_size):
        if np.random.rand() < mutation_rate:
            offspring[i] += np.random.normal(0, 1, 2)

    # Evaluate the offspring
    offspring_fitness = [objective_function(individual) for individual in offspring]

    # Replace the population with the offspring
    population = offspring
    fitness = offspring_fitness

# Print the results
best_individual = population[np.argmin(fitness)]
print(f"Optimal value: {objective_function(best_individual)}")
print(f"Optimal variables: {best_individual}")