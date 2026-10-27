import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Load persistence data
with open('world_c_results/world_c_job_gemini_3_1_flash_lite_1792982950_ef0a_persistence_results_v2.json', 'r') as f:
    data = json.load(f)

r_values = sorted([float(k) for k in data.keys()])
scores = [data[str(r)] for r in r_values]

# Plotting the results
plt.figure(figsize=(10, 6))
plt.plot(r_values, scores, marker='o', linestyle='-', color='b')
plt.title('Topological Persistence (Betti-0 Sum) vs R-value')
plt.xlabel('R-value')
plt.ylabel('Sum of Betti-0 Scores')
plt.grid(True)
plt.savefig('persistence_plot.png')
print("Plot saved to persistence_plot.png")
