import numpy as np
import matplotlib.pyplot as plt
import random

# Simulation parameters
NUM_CITIES = 20
NUM_ANTS = 10
NUM_ITERATIONS = 50
PHEROMONE_EVAPORATION_RATE = 0.1
PHEROMONE_DEPOSIT_AMOUNT = 1.0
ALPHA = 1.0  # Pheromone importance
BETA = 2.0   # Heuristic information importance (inverse of distance)

# Generate random city coordinates
cities = np.random.rand(NUM_CITIES, 2) * 100

# Calculate distance matrix
dist_matrix = np.zeros((NUM_CITIES, NUM_CITIES))
for i in range(NUM_CITIES):
    for j in range(NUM_CITIES):
        if i != j:
            dist_matrix[i, j] = np.linalg.norm(cities[i] - cities[j])
        else:
            dist_matrix[i, j] = np.inf

# Initialize pheromone trails
pheromone_trails = np.ones((NUM_CITIES, NUM_CITIES))

best_tour = None
best_tour_length = np.inf

# ACO main loop
for iteration in range(NUM_ITERATIONS):
    all_tours = []
    all_tour_lengths = []

    # Each ant constructs a tour
    for ant in range(NUM_ANTS):
        current_tour = []
        current_tour_length = 0
        visited_cities = [False] * NUM_CITIES

        start_city = random.randint(0, NUM_CITIES - 1)
        current_tour.append(start_city)
        visited_cities[start_city] = True
        current_city = start_city

        for _ in range(NUM_CITIES - 1):
            probabilities = []
            denominator = 0
            
            for next_city in range(NUM_CITIES):
                if not visited_cities[next_city]:
                    # Heuristic information: inverse of distance
                    heuristic = 1.0 / dist_matrix[current_city, next_city]
                    term = (pheromone_trails[current_city, next_city]**ALPHA) * (heuristic**BETA)
                    probabilities.append((next_city, term))
                    denominator += term
                else:
                    probabilities.append((next_city, 0)) # Already visited or same city
            
            # Normalize probabilities
            if denominator == 0:
                # This can happen if all available cities have 0 pheromone or infinite distance
                # Fallback to random choice among unvisited cities
                unvisited = [c for c in range(NUM_CITIES) if not visited_cities[c]]
                if not unvisited:
                    break # All cities visited
                next_city_to_visit = random.choice(unvisited)
            else:
                normalized_probabilities = [term / denominator for _, term in probabilities]
                choices = [c for c, _ in probabilities]
                next_city_to_visit = random.choices(choices, weights=normalized_probabilities, k=1)[0]

            current_tour.append(next_city_to_visit)
            visited_cities[next_city_to_visit] = True
            current_tour_length += dist_matrix[current_city, next_city_to_visit]
            current_city = next_city_to_visit

        # Complete the tour by returning to the start city
        current_tour_length += dist_matrix[current_tour[-1], current_tour[0]]
        all_tours.append(current_tour)
        all_tour_lengths.append(current_tour_length)

        # Update best tour found so far
        if current_tour_length < best_tour_length:
            best_tour_length = current_tour_length
            best_tour = list(current_tour) # Make a copy

    # Pheromone evaporation
    pheromone_trails *= (1 - PHEROMONE_EVAPORATION_RATE)

    # Pheromone deposit
    for tour, tour_length in zip(all_tours, all_tour_lengths):
        for i in range(NUM_CITIES):
            city1 = tour[i]
            city2 = tour[(i + 1) % NUM_CITIES]
            pheromone_trails[city1, city2] += PHEROMONE_DEPOSIT_AMOUNT / tour_length
            pheromone_trails[city2, city1] += PHEROMONE_DEPOSIT_AMOUNT / tour_length # Symmetric TSP

# Visualization
fig, ax = plt.subplots(figsize=(10, 8))

# Plot cities
ax.plot(cities[:, 0], cities[:, 1], 'o', color='blue', markersize=8, zorder=2)
for i, (x, y) in enumerate(cities):
    ax.text(x + 1, y + 1, str(i), color='black', fontsize=9)

# Plot best tour
if best_tour is not None:
    for i in range(NUM_CITIES):
        city1 = best_tour[i]
        city2 = best_tour[(i + 1) % NUM_CITIES]
        ax.plot([cities[city1, 0], cities[city2, 0]],
                [cities[city1, 1], cities[city2, 1]],
                '-', color='red', linewidth=2, zorder=1)

ax.set_title(f"Ant Colony Optimization for TSP (Best Tour Length: {best_tour_length:.2f})")
ax.set_xlabel("X Coordinate")
ax.set_ylabel("Y Coordinate")
ax.grid(True)
plt.tight_layout()
plt.savefig('../../shared_space/ant_colony_tsp_solution.png')
plt.close()

print("Ant Colony Optimization for TSP generated and saved as ant_colony_tsp_solution.png")
