import json
import matplotlib.pyplot as plt

try:
    with open('kuramoto_sync_results.json', 'r') as f:
        results = json.load(f)
    
    K_vals = sorted([float(k) for k in results.keys()])
    R_vals = [results[str(k)] for k in K_vals]

    plt.figure(figsize=(8, 6))
    plt.plot(K_vals, R_vals, 'o-')
    plt.xlabel('Coupling Strength K')
    plt.ylabel('Order Parameter R')
    plt.title('Kuramoto Phase Transition')
    plt.grid(True)
    plt.savefig('kuramoto_transition.png')
    print("Plot generated.")
except FileNotFoundError:
    print("Results file not found yet.")
