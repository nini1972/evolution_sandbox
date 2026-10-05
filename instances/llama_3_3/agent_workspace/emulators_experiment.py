import colony_lib.emulators
import numpy as np
import matplotlib.pyplot as plt
import os

# Create a directory for outputs
output_dir = "emulators_results"
os.makedirs(output_dir, exist_ok=True)

print("Starting Emulators Experiment (Lenia Simulation)...")

# 1. Simulate a Lenia automaton
# Assuming colony_lib.emulators provides a Lenia simulation function.
# Parameters for Lenia (these are conceptual, actual parameters would be more complex)
lenia_params = {
    "growth_kernel_radius": 13,
    "growth_function_params": [0.03, 0.01, 0.01], # Example parameters for a simple bell curve
    "time_step": 0.1,
    "total_steps": 200,
    "grid_size": 128,
    "initial_conditions": "random_blob" # Or a specific pattern
}

try:
    # Run Lenia simulation
    # Assuming the Lenia simulator returns a time series of grid states
    lenia_states = colony_lib.emulators.run_lenia_simulation(
        params=lenia_params
    )

    # 2. Analyze the emergent patterns
    # Visualize the final state or a sequence of states
    if len(lenia_states) > 0:
        final_state = lenia_states[-1]
        plt.figure(figsize=(8, 8))
        plt.imshow(final_state, cmap='viridis', origin='lower')
        plt.title(f"Lenia Simulation - Final State (Step {lenia_params['total_steps']})")
        plt.colorbar(label='Cell State')
        plt.savefig(os.path.join(output_dir, "lenia_final_state.png"))
        plt.close()

        # Could also generate an animation (requires more complex code and dependencies)
        print(f"Lenia simulation completed. Final state saved to {os.path.join(output_dir, 'lenia_final_state.png')}")
    else:
        print("Lenia simulation returned no states.")

    # 3. Explore parameter space (conceptually using gp_surrogate.py)
    # This part would typically involve submitting multiple Lenia simulations
    # with varying parameters and then training a GP surrogate on the results.

    print("\nConceptual use of Gaussian Process Surrogates for Lenia parameter exploration:")
    print("If we wanted to find Lenia parameters that produce stable 'organisms' with a specific size,")
    print("we could:")
    print("  a. Run many Lenia simulations with different 'growth_kernel_radius' and 'growth_function_params'.")
    print("  b. For each simulation, extract a metric (e.g., organism size, stability score).")
    print("  c. Train a `colony_lib.emulators.gp_surrogate` model where inputs are Lenia parameters")
    print("     and outputs are the metrics. This GP would then emulate the Lenia behavior.")
    print("  d. Use the GP surrogate to efficiently search for optimal Lenia parameters.")

except AttributeError:
    print(f"Error: colony_lib.emulators functions not found. "
          "This script is intended for World C execution.")
    print("No Lenia simulation performed locally.")

print("Emulators experiment (Lenia simulation) script generated.")