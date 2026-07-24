import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_synthetic_climate():
    # Synthetic Brownian motion to mimic temperature fluctuations
    n = 1000
    noise = np.random.normal(0, 1, n)
    temp = np.cumsum(noise)
    
    # Store in CSV if possible, for modularity
    pd.DataFrame(temp).to_csv('synthetic_climate.csv', index=False)
    
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(temp)
    plt.title('Synthetic Climate Model (Brownian Motion)')
    plt.savefig('synthetic_climate_fractal.png')
    
    print("Synthetic climate generated and plotted.")

if __name__ == '__main__':
    generate_synthetic_climate()
