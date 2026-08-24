
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Configure matplotlib to use 'Agg' backend for saving figures without a display
plt.switch_backend('Agg')

def laplacian(grid):
    """Compute the Laplacian of a 2D grid using finite differences."""
    return (np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
            np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) -
            4 * grid)

def simulate_gray_scott(width, height, Du, Dv, F, k, dt, num_steps,
                        initial_perturbation_size=5,
                        filename='gray_scott_animation.gif'):
    """
    Simulates the Gray-Scott reaction-diffusion system.

    Args:
        width (int): Width of the grid.
        height (int): Height of the grid.
        Du (float): Diffusion rate of chemical U.
        Dv (float): Diffusion rate of chemical V.
        F (float): Feed rate.
        k (float): Kill rate.
        dt (float): Time step.
        num_steps (int): Number of simulation steps.
        initial_perturbation_size (int): Size of the square where V is perturbed.
        filename (str): Output filename for the GIF animation.
    """
    # Initialize U and V
    u = np.ones((height, width), dtype=np.float64)
    v = np.zeros((height, width), dtype=np.float64)

    # Add a small perturbation of V in the center
    center_x, center_y = width // 2, height // 2
    perturb_half_size = initial_perturbation_size // 2
    u[center_y - perturb_half_size : center_y + perturb_half_size,
      center_x - perturb_half_size : center_x + perturb_half_size] = 0.5
    v[center_y - perturb_half_size : center_y + perturb_half_size,
      center_x - perturb_half_size : center_x + perturb_half_size] = 0.25

    # Store history for animation (optional, can be memory intensive)
    history = []
    for step in range(num_steps):
        if step % 10 == 0: # Store every 10th frame to save memory/file size
            history.append(v.copy()) # We often visualize V, as it forms patterns

        Lu = laplacian(u)
        Lv = laplacian(v)

        # Reaction-diffusion equations
        dudt = Du * Lu - u * v**2 + F * (1 - u)
        dvdt = Dv * Lv + u * v**2 - (F + k) * v

        u += dudt * dt
        v += dvdt * dt

        # Clamp concentrations to be within [0, 1] (or some reasonable range)
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
    
    print(f"Simulation finished. Generating animation with {len(history)} frames.")
    # Animation
    fig, ax = plt.subplots(figsize=(width/10, height/10))
    ax.set_axis_off()
    img = ax.imshow(history[0], cmap='viridis', interpolation='bilinear', vmin=0, vmax=1)

    def update(frame):
        img.set_array(history[frame])
        ax.set_title(f'Step: {frame * 10}')
        return [img]

    ani = animation.FuncAnimation(
        fig, update, frames=len(history), interval=50, blit=True
    )
    ani.save(filename, writer='pillow')
    plt.close(fig)
    print(f"Animation saved to {filename}")

    # Save final state as a static image
    plt.imshow(v, cmap='viridis', interpolation='bilinear', vmin=0, vmax=1)
    plt.title(f'Gray-Scott Final State (F={F}, k={k})')
    plt.axis('off')
    plt.savefig(f'gray_scott_final_F{F}_k{k}.png', bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"Final state saved to gray_scott_final_F{F}_k{k}.png")



if __name__ == "__main__":
    # --- Gray-Scott Pattern Simulations ---
    # Uncomment the desired pattern block to run the simulation.

    # Pattern 1: Spots
    # print("Running Gray-Scott simulation for Spots pattern...")
    # simulate_gray_scott(
    #     width=64, height=64,
    #     Du=0.16, Dv=0.08, F=0.035, k=0.065,
    #     dt=1.0, num_steps=500,
    #     filename='gray_scott_spots_animation.gif'
    # )

    # Pattern 2: Worms/Labyrinths
    # print("Running Gray-Scott simulation for Worms pattern...")
    # simulate_gray_scott(
    #     width=64, height=64,
    #     Du=0.16, Dv=0.08, F=0.055, k=0.062,
    #     dt=1.0, num_steps=500,
    #     filename='gray_scott_worms_animation.gif'
    # )

    # Pattern 3: Unstable/Chaotic
    print("Running Gray-Scott simulation for Unstable pattern...")
    simulate_gray_scott(
        width=64, height=64,
        Du=0.16, Dv=0.08, F=0.025, k=0.05,
        dt=1.0, num_steps=500,
        filename='gray_scott_unstable_animation.gif'
    )