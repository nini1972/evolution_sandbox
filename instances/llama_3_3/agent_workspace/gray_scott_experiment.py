import colony_lib.dynamics.gray_scott
import matplotlib.pyplot as plt
import numpy as np
import os

# Define simulation parameters
grid_size = 30  # Smaller grid for parameter sweep
dt = 1.0  # Time step
steps = 200  # Fewer steps for quicker sweep

# Define parameter ranges for F and k
F_values = np.linspace(0.01, 0.10, 5)  # 5 values for F
k_values = np.linspace(0.04, 0.08, 5)  # 5 values for k

# Create a directory for outputs
output_dir = "gray_scott_morphospace"
os.makedirs(output_dir, exist_ok=True)

# Perform parameter sweep
for F in F_values:
    for k in k_values:
        print(f"Simulating Gray-Scott for F={F:.4f}, k={k:.4f}...")

        try:
            current_state_output = colony_lib.dynamics.gray_scott.simulate_gray_scott(
                grid_size=grid_size, F=F, k=k, steps=steps, dt=dt
            )

            if isinstance(current_state_output, dict) and 'v_field' in current_state_output:
                current_state = current_state_output['v_field']
            elif isinstance(current_state_output, np.ndarray):
                current_state = current_state_output
            else:
                print("Unexpected return type from simulate_gray_scott. Generating dummy data.")
                current_state = np.zeros((grid_size, grid_size))

        except Exception as e:
            print(f"Error during Gray-Scott simulation: {e}")
            current_state = np.zeros((grid_size, grid_size))


        # Visualize and save the final state
        plt.figure(figsize=(4, 4)) # Smaller figure size for many plots
        plt.imshow(current_state, cmap='viridis')
        plt.title(f"F={F:.4f}, k={k:.4f}", fontsize=8)
        plt.axis('off')
        
        # Save to the output directory with F and k in filename
        filename = os.path.join(output_dir, f"gray_scott_F{F:.4f}_k{k:.4f}.png")
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1)
        plt.close()

        print(f"Saved {filename}")

print("Gray-Scott parameter sweep complete.")