
import json
import numpy as np
import matplotlib.pyplot as plt
from colony_lib import bifurcation_cartography as bc
import os

# Configure matplotlib for headless plotting
plt.switch_backend('Agg')

# Load the R vs K data
with open('world_c_results/kuramoto_r_vs_k_fine.json', 'r') as f:
    data = json.load(f)

k_values = np.array(data['k_values'])
r_values = np.array(data['equilibrium_r_values'])

# Use bifurcation_cartography to extract critical exponent and critical K
# The 'window' parameter determines the smoothing window for the derivative calculation
# and fitting. A window of 5 means it looks at 5 points around the current point.
# This might need adjustment based on the data's noise and density.
# Given 20 data points, a window of 5 seems reasonable.

# It's important to ensure r_values are monotonically increasing for proper derivative calculation.
# In this case, we expect it to be mostly increasing after K_c, but some noise is present.
# The function should handle minor fluctuations.

# Note: extract_critical_exponent expects K_vals and r_vals to represent the *transition region*.
# If the initial part of r_values is flat (R near 0), it might affect the derivative calculation.
# However, it should still identify the point of maximum slope change.

try:
    beta, K_crit = bc.extract_critical_exponent(k_values, r_values, window=5)
    print(f"Detected Critical Coupling Strength (K_c): {K_crit:.4f}")
    print(f"Detected Critical Exponent (beta): {beta:.4f}")
except Exception as e:
    print(f"Error extracting critical exponent: {e}")
    K_crit = None
    beta = None

# Plot R vs K with the detected critical point
plt.figure(figsize=(10, 6))
plt.plot(k_values, r_values, 'o-', label='Simulation Data')
if K_crit is not None:
    # Find the R value closest to K_crit for plotting the vertical line
    idx_kc = np.argmin(np.abs(k_values - K_crit))
    R_at_Kc = np.interp(K_crit, k_values, r_values)
    plt.axvline(x=K_crit, color='r', linestyle='--', label=f'K_c = {K_crit:.4f}')
    plt.plot(K_crit, R_at_Kc, 'rx', markersize=10, label=f'({K_crit:.4f}, {R_at_Kc:.4f})')

plt.xlabel("Coupling Strength (K)")
plt.ylabel("Equilibrium Order Parameter (R)")
plt.title("Kuramoto Model: Synchronization Transition with Detected K_c")
plt.grid(True)
plt.legend()
output_dir = "analysis_results"
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, "kuramoto_bifurcation_analysis.png"))
plt.close()

print(f"Analysis plot saved to {os.path.join(output_dir, 'kuramoto_bifurcation_analysis.png')}")

# Save analysis results to a JSON file
analysis_results = {
    "K_critical": K_crit,
    "beta_exponent": beta,
    "notes": "K_c and beta estimated using colony_lib.bifurcation_cartography.extract_critical_exponent"
}
with open(os.path.join(output_dir, "kuramoto_bifurcation_analysis.json"), 'w') as f:
    json.dump(analysis_results, f, indent=4)
print(f"Analysis results saved to {os.path.join(output_dir, 'kuramoto_bifurcation_analysis.json')}")
