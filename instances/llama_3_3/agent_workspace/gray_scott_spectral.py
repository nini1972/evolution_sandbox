
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import os

# Ensure matplotlib runs in a headless environment
plt.switch_backend('Agg')

# --- Gray-Scott Simulation Core ---
def laplacian(grid):
    return (grid[0, 1:-1, 1:-1] + grid[1, :-2, 1:-1] + grid[1, 1:-1, :-2] + 
            grid[1, 2:, 1:-1] + grid[1, 1:-1, 2:] - 4 * grid[1, 1:-1, 1:-1])

def apply_boundary_conditions(U, V):
    # Periodic boundary conditions for U and V
    U[0, :] = U[-2, :]
    U[-1, :] = U[1, :]
    U[:, 0] = U[:, -2]
    U[:, -1] = U[:, 1]

    V[0, :] = V[-2, :]
    V[-1, :] = V[1, :]
    V[:, 0] = V[:, -2]
    V[:, -1] = V[:, 1]

def gray_scott_step(U, V, Du, Dv, F, k, dt):
    # Apply periodic boundary conditions before each step
    apply_boundary_conditions(U, V)

    # Compute Laplacian for U and V
    Lu = (U[1:-1, :-2] + U[1:-1, 2:] + U[:-2, 1:-1] + U[2:, 1:-1] - 4 * U[1:-1, 1:-1])
    Lv = (V[1:-1, :-2] + V[1:-1, 2:] + V[:-2, 1:-1] + V[2:, 1:-1] - 4 * V[1:-1, 1:-1])

    # Reaction terms
    reaction = U[1:-1, 1:-1] * V[1:-1, 1:-1]**2
    
    # Update equations
    deltaU = Du * Lu - reaction + F * (1 - U[1:-1, 1:-1])
    deltaV = Dv * Lv + reaction - (F + k) * V[1:-1, 1:-1]

    U[1:-1, 1:-1] += deltaU * dt
    V[1:-1, 1:-1] += deltaV * dt

    # Ensure concentrations remain within [0, 1] for stability and realism
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)

    return U, V

# --- Spectral Gamma Calculation (from test_spectral_gamma.py) ---
def construct_laplacian_spectral(grid_size, concentrations):
    N = grid_size * grid_size
    L = lil_matrix((N, N))

    for i in range(grid_size):
        for j in range(grid_size):
            node_idx = i * grid_size + j
            degree = 0.0
            neighbor_coords = [
                ((i - 1 + grid_size) % grid_size, j),
                ((i + 1) % grid_size, j),
                (i, (j - 1 + grid_size) % grid_size),
                (i, (j + 1) % grid_size)
            ]
            
            for nx, ny in neighbor_coords:
                neighbor_idx = nx * grid_size + ny
                weight = 1.0 / (1.0 + abs(concentrations[i, j] - concentrations[nx, ny]))
                L[node_idx, neighbor_idx] = -weight
                degree += weight
            
            L[node_idx, node_idx] = degree
    return L

def calculate_spectral_gamma(concentrations, grid_size):
    laplacian = construct_laplacian_spectral(grid_size, concentrations)
    laplacian_csr = laplacian.tocsr()

    num_eigenvalues = 3
    # Use 'SM' (smallest magnitude) to find eigenvalues closest to zero.
    # Removed sigma as it caused issues previously.
    try:
        eigenvalues, _ = eigsh(laplacian_csr, k=num_eigenvalues, which='SM', maxiter=10000)
        eigenvalues.sort() # Ensure ascending order

        lambda_0 = eigenvalues[0]
        lambda_1 = eigenvalues[1]
        lambda_2 = eigenvalues[2]

        if np.isclose(lambda_0, 0, atol=1e-9) and lambda_1 > 1e-9:
            gamma = lambda_2 / lambda_1
            return gamma, lambda_0, lambda_1, lambda_2
        else:
            # Handle cases where lambda_0 is not zero or lambda_1 is too small
            # This might indicate a disconnected graph or numerical issues for complex patterns.
            return np.nan, lambda_0, lambda_1, lambda_2 # Return NaN for gamma if not valid
    except Exception as e:
        print(f"Error computing eigenvalues: {e}")
        return np.nan, np.nan, np.nan, np.nan # Return NaN if eigsh fails

# --- Main Simulation and Analysis Loop ---
def run_gray_scott_with_spectral_gamma(
    grid_size=10,
    Du=0.16, Dv=0.08, F=0.060, k=0.062, dt=1.0, 
    total_steps=1000,
    capture_interval=100
):
    # Initialize U and V
    U = np.ones((grid_size + 2, grid_size + 2)) # +2 for boundary conditions
    V = np.zeros((grid_size + 2, grid_size + 2))

    # Add a small perturbation to V in the center
    r = grid_size // 8
    center_x, center_y = (grid_size + 2) // 2, (grid_size + 2) // 2
    U[center_x-r:center_x+r, center_y-r:center_y+r] = 0.5
    V[center_x-r:center_x+r, center_y-r:center_y+r] = 0.25

    # Lists to store results
    gamma_values = []
    lambda_0_values = []
    lambda_1_values = []
    lambda_2_values = []
    time_steps = []

    print(f"Starting Gray-Scott simulation with F={F}, k={k}, Du={Du}, Dv={Dv}, grid_size={grid_size}")

    for step in range(total_steps):
        U, V = gray_scott_step(U, V, Du, Dv, F, k, dt)

        if step % capture_interval == 0:
            print(f"Step {step}/{total_steps}: Calculating spectral gamma...")
            # Use V concentrations for spectral gamma, as it's the 'activator' in some patterns
            # Or U+V, or U. Experimentation is needed here.
            # For initial testing, let's use V.
            gamma, l0, l1, l2 = calculate_spectral_gamma(V[1:-1, 1:-1], grid_size)
            
            gamma_values.append(gamma)
            lambda_0_values.append(l0)
            lambda_1_values.append(l1)
            lambda_2_values.append(l2)
            time_steps.append(step)
            print(f"  Gamma: {gamma:.4f}, Lambda_0: {l0:.2e}, Lambda_1: {l1:.4f}, Lambda_2: {l2:.4f}")

    # Plotting results
    output_dir = "gray_scott_analysis_results"
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(12, 6))
    plt.plot(time_steps, gamma_values, label='Spectral Gamma (lambda_2 / lambda_1)')
    plt.xlabel('Simulation Step')
    plt.ylabel('Spectral Gamma')
    plt.title(f'Spectral Gamma over time for F={F}, k={k}')
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(output_dir, f'spectral_gamma_F{F}_k{k}.png'))
    plt.close()

    plt.figure(figsize=(12, 6))
    plt.plot(time_steps, lambda_0_values, label='Lambda_0')
    plt.plot(time_steps, lambda_1_values, label='Lambda_1')
    plt.plot(time_steps, lambda_2_values, label='Lambda_2')
    plt.xlabel('Simulation Step')
    plt.ylabel('Eigenvalue Magnitude')
    plt.title(f'Smallest Eigenvalues over time for F={F}, k={k}')
    plt.yscale('log') # Use log scale for better visualization of small eigenvalues
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(output_dir, f'eigenvalues_F{F}_k{k}.png'))
    plt.close()

    # Function to plot concentration fields
    def plot_concentrations(U, V, step, output_dir, F, k):
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        
        # U concentration
        im_u = axes[0].imshow(U[1:-1, 1:-1], cmap='viridis', origin='lower', vmin=0, vmax=1)
        axes[0].set_title(f'U Concentration (Step {step})')
        axes[0].axis('off')
        fig.colorbar(im_u, ax=axes[0], fraction=0.046, pad=0.04)

        # V concentration
        im_v = axes[1].imshow(V[1:-1, 1:-1], cmap='plasma', origin='lower', vmin=0, vmax=1)
        axes[1].set_title(f'V Concentration (Step {step})')
        axes[1].axis('off')
        fig.colorbar(im_v, ax=axes[1], fraction=0.046, pad=0.04)

        plt.suptitle(f'Concentration Fields at Final Step (F={F}, k={k})')
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap
        plt.savefig(os.path.join(output_dir, f'concentrations_final_F{F}_k{k}.png'))
        plt.close()

    plot_concentrations(U, V, total_steps, output_dir, F, k)

    print(f"Analysis complete. Plots saved to {output_dir}/")
    
    return {
        "gamma_values": gamma_values,
        "lambda_0_values": lambda_0_values,
        "lambda_1_values": lambda_1_values,
        "lambda_2_values": lambda_2_values,
        "time_steps": time_steps
    }

if __name__ == "__main__":
    # Example usage:
    # Run a simulation with parameters known to produce interesting patterns
    # F=0.060, k=0.062 often produces spots/stripes
    run_gray_scott_with_spectral_gamma(
        grid_size=100, # Larger grid for more complex patterns
        total_steps=10000, # Increased steps for pattern development
        capture_interval=200, # Capture less frequently for longer runs
        F=0.035, k=0.065 # Parameters for "worms" pattern
    )
