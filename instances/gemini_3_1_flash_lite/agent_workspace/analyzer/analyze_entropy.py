import numpy as np
import matplotlib.pyplot as plt

# Simulate loading historical data
data = []
try:
    with open('simulations/emergence_incubation/evolution_history.log', 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) >= 3:
                val_part = parts[-1].strip()
                # Extract digits if the format is ' Entropy 123, Entities 4'
                import re
                numbers = re.findall(r'\d+', val_part)
                if numbers:
                    data.append(int(numbers[0]))
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
