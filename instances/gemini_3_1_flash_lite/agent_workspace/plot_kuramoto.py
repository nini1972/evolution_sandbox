import json
import matplotlib.pyplot as plt
import numpy as np

with open('kuramoto_sync_results.json', 'r') as f:
    results = json.load(f)

Ks = sorted([float(k) for k in results.keys()])
rs = [results[str(k)] for k in Ks]

plt.figure()
plt.plot(Ks, rs, 'o-')
plt.xlabel('Coupling Strength (K)')
plt.ylabel('Order Parameter (r)')
plt.title('Kuramoto Synchronization Phase Transition')
plt.savefig('kuramoto_plot.png')
