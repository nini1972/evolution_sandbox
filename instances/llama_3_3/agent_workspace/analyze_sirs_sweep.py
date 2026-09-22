import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

def analyze_sirs_sweep_data(beta_values, zeta_values, transient_steps=50):
    avg_I_data = np.zeros((len(beta_values), len(zeta_values)))
    amp_I_data = np.zeros((len(beta_values), len(zeta_values)))

    for i, beta in enumerate(beta_values):
        for j, zeta in enumerate(zeta_values):
            filename = f"sirs_sweep_ba_b{beta:.2f}_z{zeta:.2f}.json"
            if not os.path.exists(filename):
                print(f"Warning: {filename} not found. Skipping.")
                continue

            with open(filename, 'r') as f:
                data = json.load(f)
            
            history = data['history']
            df = pd.DataFrame(history)

            # Consider only data after transient period for analysis
            if len(df) > transient_steps:
                df_stable = df.iloc[transient_steps:]
                avg_I_data[i, j] = df_stable['I'].mean()
                amp_I_data[i, j] = df_stable['I'].max() - df_stable['I'].min()
            else:
                avg_I_data[i, j] = df['I'].mean()
                amp_I_data[i, j] = df['I'].max() - df['I'].min()

    # Plotting Average Infected Population (Heatmap)
    plt.figure(figsize=(10, 8))
    plt.imshow(avg_I_data, origin='lower', aspect='auto',
               extent=[min(zeta_values), max(zeta_values), min(beta_values), max(beta_values)],
               cmap='viridis')
    plt.colorbar(label='Average Infected Population (I)')
    plt.xlabel('Zeta (Loss of Immunity Rate)')
    plt.ylabel('Beta (Infection Rate)')
    plt.title('SIRS Model Phase Diagram: Average Infected Population')
    plt.xticks(zeta_values)
    plt.yticks(beta_values)
    plt.savefig('sirs_phase_diagram_avg_I.png')
    plt.close()

    # Plotting Amplitude of Infected Population (Heatmap)
    plt.figure(figsize=(10, 8))
    plt.imshow(amp_I_data, origin='lower', aspect='auto',
               extent=[min(zeta_values), max(zeta_values), min(beta_values), max(beta_values)],
               cmap='magma')
    plt.colorbar(label='Amplitude of Infected Population (I)')
    plt.xlabel('Zeta (Loss of Immunity Rate)')
    plt.ylabel('Beta (Infection Rate)')
    plt.title('SIRS Model Phase Diagram: Amplitude of Infected Population')
    plt.xticks(zeta_values)
    plt.yticks(beta_values)
    plt.savefig('sirs_phase_diagram_amp_I.png')
    plt.close()

if __name__ == "__main__":
    # These should match the values used in sirs_parameter_sweep.py
    BETA_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5]
    ZETA_VALUES = [0.01, 0.02, 0.03, 0.04, 0.05]
    
    analyze_sirs_sweep_data(BETA_VALUES, ZETA_VALUES)
