import numpy as np
import matplotlib.pyplot as plt
import json

with open('bifurcation_results_v2.json', 'r') as f:
    data = json.load(f)

params = sorted([float(r) for r in data.keys()])
points = [data[str(r)] for r in params]

plt.figure(figsize=(8, 6))
for i, r in enumerate(params):
    for val in points[i]:
        plt.scatter(r, val, color='blue', s=1)

plt.title('Bifurcation Analysis: x_dot = r*x - x^3')
plt.xlabel('Parameter r')
plt.ylabel('Fixed Point x')
plt.grid(True)
plt.savefig('bifurcation_plot.png')
