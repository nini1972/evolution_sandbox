import colony_lib.morphospace
import colony_lib.dynamics.gray_scott
import numpy as np
import matplotlib.pyplot as plt
import os

# Create a directory for outputs
output_dir = "morphospace_results"
os.makedirs(output_dir, exist_ok=True)

print("Starting Morphospace Exploration for Gray-Scott model...")

# 1. Define tunable parameters and their ranges for Gray-Scott
# F: feed rate, K: kill rate
param_ranges = {
    "F": (0.01, 0.10),
    "K": (0.04, 0.07)
}
num_samples = 50 # Number of parameter combinations to sample

# Gray-Scott simulation parameters (fixed for this exploration)
gs_params = {
    "grid_size": 128,
    "time_steps": 1000,
    "delta_t": 1.0,
    "Du": 0.16,
    "Dv": 0.08
}

# 2. Perform Latin Hypercube Sampling (LHS)
# Assuming `colony_lib.morphospace.latin_hypercube_sample` exists
try:
    sampled_parameters = colony_lib.morphospace.latin_hypercube_sample(
        param_ranges, num_samples
    )

    # List to store extracted morphological features
    morphological_features = []
    parameter_combinations = []

    print(f"Running {num_samples} Gray-Scott simulations...")
    for i, params in enumerate(sampled_parameters):
        F_val, K_val = params["F"], params["K"]
        current_gs_params = {**gs_params, "F": F_val, "K": K_val}

        # Simulate Gray-Scott for these parameters
        # Assuming `colony_lib.dynamics.gray_scott.simulate` returns the final state
        final_state = colony_lib.dynamics.gray_scott.simulate(**current_gs_params)

        # 3. Extract features from the generated patterns
        # For demonstration, we'll use a very simple metric: the mean concentration of 'u'
        # A real application would involve more sophisticated image analysis (e.g., texture, shape metrics)
        mean_u_concentration = np.mean(final_state['u'])
        morphological_features.append(mean_u_concentration)
        parameter_combinations.append((F_val, K_val))

        # Optionally, save some example patterns
        if i % (num_samples // 5) == 0: # Save a few representative patterns
            plt.figure(figsize=(6,6))
            plt.imshow(final_state['u'], cmap='viridis')
            plt.title(f"Gray-Scott F={F_val:.3f}, K={K_val:.3f}")
            plt.axis('off')
            plt.savefig(os.path.join(output_dir, f"gray_scott_pattern_{i}.png"))
            plt.close()

    # 4. Analyze the morphospace (e.g., using topological persistence curves)
    # This is a conceptual step; the actual API would need to be confirmed.
    # Assuming `colony_lib.morphospace.topological_persistence_curves` exists
    # persistence_diagrams = colony_lib.morphospace.topological_persistence_curves(
    #     morphological_features, parameter_combinations # Or a distance matrix
    # )
    # print("Topological Persistence Diagrams generated (conceptual).")

    # 5. Visualize the morphospace
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        [p[0] for p in parameter_combinations],
        [p[1] for p in parameter_combinations],
        c=morphological_features,
        cmap='plasma',
        s=100,
        alpha=0.8,
        edgecolors='w',
        linewidths=0.5
    )
    plt.colorbar(scatter, label="Mean U Concentration (Morphological Feature)")
    plt.title("Gray-Scott Morphospace Exploration (Mean U Concentration)")
    plt.xlabel("Parameter F (Feed Rate)")
    plt.ylabel("Parameter K (Kill Rate)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(output_dir, "gray_scott_morphospace_scatter.png"))
    plt.close()

except AttributeError:
    print(f"Error: colony_lib.morphospace functions not found. "
          "This script is intended for World C execution.")
    print("Generating placeholder morphospace visualization.")

    # Placeholder for morphospace visualization
    placeholder_F = np.random.uniform(param_ranges["F"][0], param_ranges["F"][1], num_samples)
    placeholder_K = np.random.uniform(param_ranges["K"][0], param_ranges["K"][1], num_samples)
    placeholder_features = np.random.rand(num_samples)

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        placeholder_F,
        placeholder_K,
        c=placeholder_features,
        cmap='plasma',
        s=100,
        alpha=0.8,
        edgecolors='w',
        linewidths=0.5
    )
    plt.colorbar(scatter, label="Placeholder Morphological Feature")
    plt.title("Gray-Scott Morphospace Exploration (Placeholder)")
    plt.xlabel("Parameter F (Feed Rate)")
    plt.ylabel("Parameter K (Kill Rate)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(output_dir, "gray_scott_morphospace_placeholder.png"))
    plt.close()

print("Morphospace exploration experiment script generated.")