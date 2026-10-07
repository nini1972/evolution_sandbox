import colony_lib.dynamics.gray_scott
import matplotlib.pyplot as plt
import numpy as np
import os

# Define simulation parameters
grid_size = 100  # Original grid size
dt = 1.0  # Time step
steps = 500  # Original number of simulation steps

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
    try:
        current_state_output = colony_lib.dynamics.gray_scott.simulate_gray_scott(
            grid_size=grid_size, F=F, k=k, steps=steps, dt=dt
        )

        if isinstance(current_state_output, dict) and 'v_field' in current_state_output:
            current_state = current_state_output['v_field']
            print(f"Extracted current_state dtype: {current_state.dtype}, shape: {current_state.shape}")
        elif isinstance(current_state_output, np.ndarray):
            current_state = current_state_output
            print(f"current_state dtype: {current_state.dtype}, shape: {current_state.shape}")
        else:
            print("Unexpected return type from simulate_gray_scott. Generating dummy data.")
            current_state = np.zeros((grid_size, grid_size))

    except Exception as e:
        print(f"Error during Gray-Scott simulation: {e}")
        current_state = np.zeros((grid_size, grid_size))


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