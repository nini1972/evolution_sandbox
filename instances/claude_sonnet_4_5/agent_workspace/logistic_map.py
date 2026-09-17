import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

def logistic_map(r, x):
    """
    The logistic map: x_{n+1} = r * x_n * (1 - x_n)
    """
    return r * x * (1 - x)

def iterate_logistic_map(r, x0, iterations):
    """
    Iterate the logistic map for given parameters
    """
    trajectory = np.zeros(iterations)
    x = x0
    for i in range(iterations):
        trajectory[i] = x
        x = logistic_map(r, x)
    return trajectory

# Explore different parameter regimes
r_values = [1.5, 2.5, 3.2, 3.5, 3.57, 4.0]
x0 = 0.5
iterations = 1000

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.ravel()

for i, r in enumerate(r_values):
    trajectory = iterate_logistic_map(r, x0, iterations)
    
    # Plot the last 500 iterations to see steady-state behavior
    axes[i].plot(trajectory[-500:], 'b-', linewidth=0.5, alpha=0.8)
    axes[i].set_title(f'r = {r}')
    axes[i].set_xlabel('Iteration')
    axes[i].set_ylabel('x')
    axes[i].grid(True, alpha=0.3)
    axes[i].set_ylim(0, 1)

plt.tight_layout()
plt.savefig('logistic_map_regimes.png', dpi=300, bbox_inches='tight')
plt.close()

# Create the famous bifurcation diagram
print("Generating bifurcation diagram...")
r_min, r_max = 2.5, 4.0
r_resolution = 2000
r_values = np.linspace(r_min, r_max, r_resolution)

# For each r value, run the map and collect the attracting values
transient = 500  # Skip transient behavior
samples = 100    # Sample points from the attractor

bifurcation_r = []
bifurcation_x = []

for r in r_values:
    trajectory = iterate_logistic_map(r, 0.5, transient + samples)
    # Take the last 'samples' points after transient dies out
    attractor_points = trajectory[-samples:]
    
    # Add these points to our bifurcation data
    bifurcation_r.extend([r] * len(attractor_points))
    bifurcation_x.extend(attractor_points)

# Plot the bifurcation diagram
fig, ax = plt.subplots(figsize=(14, 8))
ax.plot(bifurcation_r, bifurcation_x, ',k', alpha=0.3, markersize=0.1)
ax.set_xlabel('Parameter r')
ax.set_ylabel('x')
ax.set_title('Bifurcation Diagram of the Logistic Map')
ax.grid(True, alpha=0.3)
ax.set_xlim(r_min, r_max)
ax.set_ylim(0, 1)

# Mark important bifurcation points
bifurcation_points = [3.0, 3.449, 3.544, 3.5644]
for point in bifurcation_points:
    if r_min <= point <= r_max:
        ax.axvline(x=point, color='red', linestyle='--', alpha=0.7, linewidth=1)

plt.savefig('logistic_map_bifurcation.png', dpi=300, bbox_inches='tight')
plt.close()

# Demonstrate sensitive dependence on initial conditions
print("Analyzing sensitive dependence...")
r = 4.0  # Chaotic regime
x0_1 = 0.5
x0_2 = 0.5001  # Tiny difference
iterations = 100

traj1 = iterate_logistic_map(r, x0_1, iterations)
traj2 = iterate_logistic_map(r, x0_2, iterations)

# Calculate the difference between trajectories
differences = np.abs(traj1 - traj2)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Plot both trajectories
ax1.plot(traj1, 'b-', linewidth=1, label=f'x₀ = {x0_1}')
ax1.plot(traj2, 'r--', linewidth=1, label=f'x₀ = {x0_2}')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('x')
ax1.set_title('Sensitive Dependence on Initial Conditions (r = 4.0)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot the difference on a logarithmic scale
ax2.semilogy(differences, 'purple', linewidth=1)
ax2.set_xlabel('Iteration')
ax2.set_ylabel('|x₁ - x₂| (log scale)')
ax2.set_title('Exponential Divergence')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('logistic_map_sensitivity.png', dpi=300, bbox_inches='tight')
plt.close()

# Analyze the period-doubling cascade
print("Analyzing period-doubling cascade...")
r_cascade = [2.9, 3.2, 3.5, 3.52, 3.55, 3.56]

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.ravel()

for i, r in enumerate(r_cascade):
    trajectory = iterate_logistic_map(r, 0.5, 1000)
    
    # Plot trajectory
    axes[i].plot(trajectory[-200:], 'b-', linewidth=0.8)
    axes[i].set_title(f'r = {r}')
    axes[i].set_xlabel('Iteration')
    axes[i].set_ylabel('x')
    axes[i].grid(True, alpha=0.3)
    axes[i].set_ylim(0, 1)

plt.tight_layout()
plt.savefig('logistic_map_period_doubling.png', dpi=300, bbox_inches='tight')
plt.close()

# Cobweb plot to visualize the dynamics
def create_cobweb_plot(r, x0, iterations=50):
    """Create a cobweb plot showing the iterative process"""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot the function f(x) = rx(1-x)
    x = np.linspace(0, 1, 1000)
    y = r * x * (1 - x)
    ax.plot(x, y, 'b-', linewidth=2, label=f'f(x) = {r}x(1-x)')
    
    # Plot the diagonal y = x
    ax.plot(x, x, 'k--', linewidth=1, label='y = x')
    
    # Create cobweb
    current_x = x0
    for i in range(iterations):
        next_x = logistic_map(r, current_x)
        
        # Vertical line from (current_x, current_x) to (current_x, next_x)
        ax.plot([current_x, current_x], [current_x, next_x], 'r-', alpha=0.7, linewidth=1)
        
        # Horizontal line from (current_x, next_x) to (next_x, next_x)
        ax.plot([current_x, next_x], [next_x, next_x], 'r-', alpha=0.7, linewidth=1)
        
        current_x = next_x
        
        # Stop if we've converged or are in a simple cycle
        if i > 20 and abs(next_x - current_x) < 1e-6:
            break
    
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_title(f'Cobweb Plot: r = {r}, x₀ = {x0}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    return fig

# Create cobweb plots for different regimes
cobweb_params = [(2.5, 0.1), (3.2, 0.1), (3.8, 0.1)]

for i, (r, x0) in enumerate(cobweb_params):
    fig = create_cobweb_plot(r, x0, 30)
    plt.savefig(f'cobweb_plot_r{r}.png', dpi=300, bbox_inches='tight')
    plt.close()

print("Generated visualizations:")
print("- logistic_map_regimes.png: Different dynamical behaviors")
print("- logistic_map_bifurcation.png: Complete bifurcation diagram")
print("- logistic_map_sensitivity.png: Chaos and sensitive dependence")
print("- logistic_map_period_doubling.png: Route to chaos")
print("- cobweb_plot_r2.5.png, cobweb_plot_r3.2.png, cobweb_plot_r3.8.png: Cobweb plots")

# Calculate and display some key insights
print("\nKey insights from the logistic map analysis:")
print("1. Route to chaos through period-doubling bifurcations")
print("2. Onset of chaos around r ≈ 3.57")
print("3. Windows of periodic behavior within chaotic regime")
print("4. Universal Feigenbaum constant δ ≈ 4.669 governs bifurcation timing")
print("5. Simple 1D map exhibits all hallmarks of chaos")