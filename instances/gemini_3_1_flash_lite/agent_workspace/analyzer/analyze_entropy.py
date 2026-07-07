import numpy as np
import matplotlib.pyplot as plt

# Simulate loading historical data
data = []
try:
    with open('simulations/emergence_incubation/evolution_history.log', 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) >= 3:
                data.append(int(parts[-1]))
except FileNotFoundError:
    pass

if data:
    plt.figure(figsize=(10, 5))
    plt.plot(data, marker='o')
    plt.title("Evolutionary Entropy Over Time")
    plt.xlabel("Cycle")
    plt.ylabel("Entropy (Active Cells)")
    plt.savefig('analyzer/entropy_chart.png')
    print("Chart created.")
else:
    print("Insufficient data.")
