
import numpy as np
import matplotlib.pyplot as plt
import colony_lib.dynamics as dynamics
import os

print("Starting Gray-Scott simulation script.")

# Simulation parameters
N = 200  # Grid size
DA = 0.16
DB = 0.08
f = 0.060
k = 0.062
delta_t = 1.0
N_simulation_steps = 10000

print(f"Parameters: N={N}, DA={DA}, DB={DB}, f={f}, k={k}, delta_t={delta_t}, steps={N_simulation_steps}")

# Get initial configuration
A = (1 - 0.2) * np.ones((N, N)) + 0.2 * np.random.random((N, N))
B = 0.2 * np.random.random((N, N))
N2 = N // 2
radius = int(N / 10.0)
A[N2 - radius:N2 + radius, N2 - radius:N2 + radius] = 0.50
B[N2 - radius:N2 + radius, N2 - radius:N2 + radius] = 0.25

print("Initial configuration set.")

# Run Gray-Scott simulation
try:
    A, B = dynamics.gray_scott(
        A_init=A, B_init=B,
        DA=DA, DB=DB,
        f=f, k=k,
        delta_t=delta_t,
        num_steps=N_simulation_steps
    )
    print("Gray-Scott simulation completed successfully.")
except Exception as e:
    print(f"An error occurred during Gray-Scott simulation: {e}")

# Plotting the final state
fig, ax = plt.subplots(1, 2, figsize=(10, 5))
ax[0].imshow(A, cmap='Greys')
ax[1].imshow(B, cmap='Greys')
ax[0].set_title('Concentration A')
ax[1].set_title('Concentration B')
ax[0].axis('off')
ax[1].axis('off')
plt.suptitle(f'Gray-Scott Pattern (f={f}, k={k})')

# Ensure the output directory exists
output_dir = "world_c_artifacts"
os.makedirs(output_dir, exist_ok=True)

output_filename = os.path.join(output_dir, f'gray_scott_f_{f}_k_{k}.png')
plt.savefig(output_filename)
plt.close(fig)

print(f"Gray-Scott pattern image saved to {output_filename}")
print("Gray-Scott simulation script finished.")
