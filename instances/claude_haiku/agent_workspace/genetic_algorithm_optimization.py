import numpy as np
import numpy as np
try:
    from deap import base, creator, tools
except ImportError:
    print("Please install the 'deap' package to run this example.")
    exit(1)
from deap import base, creator, tools

# Define the objective function
def objective_function(x):
    return x[0]**2 + (x[1] - 1)**2

# Define the genetic algorithm parameters
population_size = 100
num_generations = 100

# Create the toolbox
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_float", np.random.uniform, -5, 5, 2)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.attr_float)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", objective_function)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

# Run the genetic algorithm
pop = toolbox.population(n=population_size)
for g in range(num_generations):
    offspring = [toolbox.clone(ind) for ind in pop]
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if np.random.uniform() < 0.5:
            toolbox.mate(child1, child2)
        toolbox.mutate(child1)
        toolbox.mutate(child2)
        del child1.fitness.values, child2.fitness.values
    pop = toolbox.select(pop + offspring, population_size)

# Print the results
best_ind = min(pop, key=toolbox.evaluate)
print(f"Optimal value: {-best_ind.fitness.values[0]}")
print(f"Optimal variables: {best_ind}")