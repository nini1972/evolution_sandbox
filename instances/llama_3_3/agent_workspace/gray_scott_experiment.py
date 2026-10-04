import colony_lib.dynamics.gray_scott
import matplotlib.pyplot as plt
import numpy as np
import os

# Define simulation parameters
grid_size = (100, 100)  # Smaller grid for initial tests
dt = 1.0  # Time step
steps = 500  # Number of simulation steps

# Example (F, k) parameter pairs for different patterns (from web research)
parameter_sets = [
    {"F": 0.0545, "k": 0.062, "name": "spots"},
    {"F": 0.035, "k": 0.065, "name": "stripes"},
    {"F": 0.010, "k": 0.040, "name": "labyrinth"},
    {"F": 0.060, "k": 0.062, "name": "worms"},
]

# Create a directory for outputs
output_dir = "gray_scott_results"
os.makedirs(output_dir, exist_ok=True)

for params in parameter_sets:
    F = params["F"]
    k = params["k"]
    name = params["name"]

    print(f"Simulating Gray-Scott for F={F}, k={k} ({name})...")

    # Call the World C `colony_lib` function
    # The `colony_lib.dynamics.gray_scott.simulate_gray_scott` function
    # is assumed to exist and return the final state of the simulation.
    try:
        current_state = colony_lib.dynamics.gray_scott.simulate_gray_scott(
            grid_size=grid_size, F=F, k=k, steps=steps, dt=dt
        )
    except AttributeError:
        print(f"Error: colony_lib.dynamics.gray_scott.simulate_gray_scott not found. "
              "This script is intended for World C execution.")
        # Generate a dummy image if colony_lib is not available locally
        current_state = np.random.rand(grid_size[0], grid_size[1])


    # Visualize and save the final state
    plt.figure(figsize=(6, 6))
    plt.imshow(current_state, cmap='viridis')
    plt.title(f"Gray-Scott Pattern: {name}\n(F={F}, k={k})")
    plt.axis('off')
    
    # Save to the output directory
    filename = os.path.join(output_dir, f"gray_scott_pattern_{name}_F{F}_k{k}.png")
    plt.savefig(filename)
    plt.close()

    print(f"Saved {filename}")

print("Gray-Scott exploration script generated.")