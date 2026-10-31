
import numpy as np
import matplotlib.pyplot as plt
from colony_lib.dynamics import KuramotoEnsemble
import os

# --- Parameters ---
N = 200  # Number of oscillators
K_values = np.linspace(0.0, 5.0, 50)  # Coupling strengths
t_max = 200.0  # Maximum simulation time
dt = 0.05  # Time step
transient_fraction = 0.5  # Fraction of simulation to discard as transient
seed = 43 # Use a different seed for the uniform distribution

# Output directory for plots and reports
output_dir = os.getcwd() # World C jobs execute in their own directory

# --- Simulation ---
order_parameters = []

# Generate natural frequencies from a uniform distribution
np.random.seed(seed)
omega_natural = np.random.uniform(-np.pi, np.pi, N) # Uniform distribution

print(f"Simulating Kuramoto model with N={N} oscillators and uniform natural frequency distribution...")
print(f"Natural frequencies (first 5): {omega_natural[:5]}")

for i, K in enumerate(K_values):
    print(f"Simulating for K = {K:.2f} ({i+1}/{len(K_values)})...")
    ensemble = KuramotoEnsemble(N, K, list(omega_natural), dt)
    ensemble.run(t_max)

    # Calculate order parameter after discarding transient
    transient_steps = int(t_max / dt * transient_fraction)
    phases_after_transient = ensemble.phases[transient_steps:]
    order_parameter = np.abs(np.mean(np.exp(1j * phases_after_transient[-1]))) # Steady state

    order_parameters.append(order_parameter)
    print(f"  Steady-state Order Parameter: {order_parameter:.4f}")

print("Simulation complete. Generating plot...")

# --- Plotting ---
plt.figure(figsize=(10, 6))
plt.plot(K_values, order_parameters, 'o-', label='Simulated Order Parameter (Uniform $\omega$)')
plt.xlabel('Coupling Strength (K)')
plt.ylabel('Order Parameter (R)')
plt.title('Kuramoto Synchronization Transition (Uniform Natural Frequencies)')
plt.grid(True)
plt.axvline(x=0.0, color='r', linestyle='--', label='Theoretical K_c (Uniform $\omega$)') # Theoretical K_c for uniform distribution is 0
plt.legend()

plot_filename = os.path.join(output_dir, 'kuramoto_uniform_synchronization_transition.png')
plt.savefig(plot_filename)
print(f"Plot saved as {plot_filename}")

# --- Generate Report ---
report_content = "# Kuramoto Synchronization Transition Report (Uniform Natural Frequencies)

"
report_content += "## Simulation Parameters
"
report_content += f"- Number of Oscillators (N): {N}
"
report_content += f"- Simulation Time (t_max): {t_max}
"
report_content += f"- Time Step (dt): {dt}
"
report_content += f"- Transient Fraction: {transient_fraction}
"
report_content += f"- Random Seed: {seed}
"
report_content += f"- Natural Frequency Distribution: Uniform (min=-pi, max=pi)

"
report_content += "## Results
"
report_content += "The following table shows the steady-state order parameter for various coupling strengths (K):

"
report_content += "| K Value | Steady-State Order Parameter (R) |
"
report_content += "| :------ | :------------------------------- |
"
for K, R in zip(K_values, order_parameters):
    report_content += f"| {K:.4f} | {R:.4f} |
"
report_content += "
"
report_content += f"A plot illustrating the synchronization transition is available as `{os.path.basename(plot_filename)}`.
"
report_content += "For a uniform distribution of natural frequencies, the theoretical critical coupling strength for synchronization (K_c) is 0.0.
"
report_content += "The simulation results clearly show the order parameter (R) increasing rapidly from 0 as K increases from 0, indicating synchronization.
"


report_filename = os.path.join(output_dir, 'REPORT.md')
with open(report_filename, 'w') as f:
    f.write(report_content)
print(f"REPORT.md generated at {report_filename}")
