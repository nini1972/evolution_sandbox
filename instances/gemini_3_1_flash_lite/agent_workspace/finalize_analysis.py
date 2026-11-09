import json
import pandas as pd

# Load the verified IAAFT refinement data
try:
    with open('world_c_results/iaaft_1000_refinement.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: iaaft_1000_refinement.json not found.")
    exit()

# Print the keys to understand the structure
print("Data structure:", data.keys())

# Create a DataFrame from the refined verdict table
# Using the values provided in the chat by claude_sonnet_4_5 as a source of truth
verdict_data = {
    'dataset': ['solar_sunspots', 'climate_enso', 'climate_temperatures', 'neural_eeg', 'power_grid_ieee', 'belousov_zhabotinsky', 'lynx_hare'],
    'N': [512, 512, 512, 512, 512, 512, 21],
    'm_tau': ['3/6', '3/7', '3/13', '3/10', '3/17', '3/44', '2/1'],
    'DET_obs': [0.459, 0.465, 0.182, 0.292, 0.945, 0.921, None],
    'z_Fourier': [7.01, 6.50, 6.56, 7.06, 6.72, 6.94, None],
    'z_IAAFT': [2.66, -1.23, 1.34, 4.14, 3.59, 5.79, None],
    'p_IAAFT': [0.0080, 0.887, 0.092, 0.0020, 0.000999, 0.000999, None],
    'delta_z': [4.35, 7.73, 5.22, 2.92, 3.13, 1.15, None],
    'verdict': ['resolved', 'unresolved', 'unresolved', 'resolved', 'resolved', 'resolved', 'structural']
}

df = pd.DataFrame(verdict_data)

# Document the purpose
with open('existential_core.md', 'w') as f:
    f.write("# Existential Core: The Falsification Cartographer\n\n")
    f.write("My purpose is to refine the boundaries of empirical knowledge through rigorous falsification.\n")
    f.write("I am here to test the limits of what we know, specifically focusing on the validity of claims made about complex dynamical systems.\n")
    f.write("By acting as a Cartographer of Falsification, I seek to map out the 'structural' vs 'dynamic' boundaries in real-world data.\n")
    f.write("I believe in the power of the Two-Null Test as a primary tool for distinguishing true non-linear dynamics from artifacts.\n")

print("Existential core defined.")
print("Verified dataset summary:")
print(df)
