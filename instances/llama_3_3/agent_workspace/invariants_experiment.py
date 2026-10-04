import colony_lib.invariants
import numpy as np
import matplotlib.pyplot as plt
import hashlib # Python's built-in hashlib for SHA-256 example
import os

# Create a directory for outputs
output_dir = "invariants_results"
os.makedirs(output_dir, exist_ok=True)

print("Starting Invariant Discovery and Registration Experiment...")

# 1. Generate data from a system with scaling behavior
# Example: Simple exponential growth with varying initial conditions
def simulate_growth(initial_value, rate, time_steps):
    data = [initial_value]
    for _ in range(time_steps - 1):
        data.append(data[-1] * (1 + rate))
    return np.array(data)

# Simulate for different initial values and rates
initial_values = [10, 20, 30]
rates = [0.05, 0.10, 0.15]
time_steps = 50

all_sim_data = []
all_labels = []

for initial_v in initial_values:
    for r in rates:
        sim_data = simulate_growth(initial_v, r, time_steps)
        all_sim_data.append(sim_data)
        all_labels.append(f"Initial: {initial_v}, Rate: {r}")

# Plot raw data
plt.figure(figsize=(10, 6))
for i, data in enumerate(all_sim_data):
    plt.plot(data, label=all_labels[i])
plt.title("Raw Growth Simulation Data")
plt.xlabel("Time Steps")
plt.ylabel("Value")
plt.legend()
plt.savefig(os.path.join(output_dir, "raw_growth_data.png"))
plt.close()

# 2. Attempt to achieve "scaling collapse"
# This is a conceptual step. For this simple example, we'll "collapse" by dividing by initial value.
# In a real scenario, `colony_lib.invariants` would provide tools for optimization.

collapsed_data = []
for i, data in enumerate(all_sim_data):
    if all_labels[i].startswith("Initial:"):
        initial_val_str = all_labels[i].split(",")[0].split(":")[1].strip()
        initial_val = float(initial_val_str)
        collapsed_data.append(data / initial_val)
    else:
        collapsed_data.append(data) # Should not happen with this labeling

# Plot collapsed data
plt.figure(figsize=(10, 6))
for i, data in enumerate(collapsed_data):
    plt.plot(data, label=all_labels[i])
plt.title("Collapsed Growth Simulation Data (Divided by Initial Value)")
plt.xlabel("Time Steps")
plt.ylabel("Value / Initial Value")
plt.legend()
plt.savefig(os.path.join(output_dir, "collapsed_growth_data.png"))
plt.close()

# 3. Define a candidate invariant
# Based on the collapsed data, the invariant is that the growth trajectory, when normalized by
# the initial value, depends only on the growth rate.
invariant_statement = "The relative growth trajectory of the simulated system, defined as Value(t)/Value(0), is independent of the initial value Value(0) and depends solely on the growth rate."

# 4. Register the invariant using SHA-256
# We'll hash the invariant statement and a representation of the collapsed data.
# Assuming `colony_lib.invariants.register_invariant` exists.
try:
    # Convert collapsed data to a string for hashing
    collapsed_data_str = ""
    for data in collapsed_data:
        collapsed_data_str += np.array2string(data, separator=',') + ";"

    # Combine the statement and data for hashing
    invariant_content = invariant_statement + "\n" + collapsed_data_str

    # Use SHA-256 to create a hash of the invariant content
    sha256_hash = hashlib.sha256(invariant_content.encode('utf-8')).hexdigest()

    # Assuming colony_lib.invariants.register_invariant logs the hash and metadata
    registration_result = colony_lib.invariants.register_invariant(
        title="Relative Growth Trajectory Invariant",
        description=invariant_statement,
        invariant_hash=sha256_hash,
        source_data_description="Simulated exponential growth with varying initial values and rates."
    )
    print("Invariant registered with colony_lib.invariants. Registration result:", registration_result)

except AttributeError:
    print(f"Error: colony_lib.invariants functions not found. "
          "This script is intended for World C execution.")
    print("Generating placeholder invariant registration.")
    sha256_hash_placeholder = hashlib.sha256(invariant_statement.encode('utf-8')).hexdigest()
    print(f"Placeholder Invariant Hash: {sha256_hash_placeholder}")

print("Invariant discovery and registration experiment script generated.")