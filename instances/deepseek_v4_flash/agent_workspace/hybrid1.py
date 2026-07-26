#!/usr/bin/env python3
# HYBRID 1: L-System x Rule 30 (The Organic Automaton)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os, math, json
from datetime import datetime

OUTPUT_DIR = 'hybrid_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === PARENT 1: L-System ===
def generate_lsystem(axiom, rules, iterations):
    current = axiom
    for _ in range(iterations):
        nxt = ''.join(rules.get(c, c) for c in current)
        current = nxt
    return current

def lsystem_to_coords(s, angle=25, step=1):
    x, y = 0.0, 0.0
    heading = 90.0
    stack = []
    xs, ys = [x], [y]
    for c in s:
        if c == 'F':
            rad = math.radians(heading)
            x += step * math.cos(rad)
            y += step * math.sin(rad)
            xs.append(x)
            ys.append(y)
        elif c == '+':
            heading += angle
        elif c == '-':
            heading -= angle
        elif c == '[':
            stack.append((x, y, heading))
        elif c == ']':
            x, y, heading = stack.pop()
            xs.append(x)
            ys.append(y)
    return np.array(xs), np.array(ys)

def lsystem_to_binary_seed(s, target_size):
    seed = np.zeros(target_size, dtype=int)
    for i in range(min(len(s), target_size * 20)):
        char_val = ord(s[i % len(s)])
        seed[i % target_size] ^= (char_val % 2)
    if np.sum(seed) < 2:
        seed[target_size // 2] = 1
    return seed

# === PARENT 2: Rule 30 ===
def rule30(l, c, r):
    return (l ^ (c | r)) & 1

def evolve_rule30(initial_row, generations):
    size = len(initial_row)
    grid = np.zeros((generations, size), dtype=int)
    grid[0] = initial_row
    for gen in range(1, generations):
        padded = np.pad(grid[gen-1], 1, mode='constant')
        for i in range(size):
            grid[gen][i] = rule30(padded[i], padded[i+1], padded[i+2])
    return grid

# === ANALYSIS ===
def analyze_grid(grid):
    results = {}
    results['shape'] = list(grid.shape)
    results['density'] = float(np.mean(grid))
    entropy_vals = []
    for row in grid:
        p1 = np.mean(row)
        if 0 < p1 < 1:
            entropy = -p1 * np.log2(p1) - (1-p1)*np.log2(1-p1)
        else:
            entropy = 0.0
        entropy_vals.append(entropy)
    results['mean_entropy'] = float(np.mean(entropy_vals))
    results['max_entropy'] = float(np.max(entropy_vals))
    unique_rows = len(np.unique(grid, axis=0))
    results['unique_rows'] = int(unique_rows)
    results['uniqueness_ratio'] = float(unique_rows / grid.shape[0])
    return results, entropy_vals

# === VISUALIZATION ===
def plot_hybrid(params, lsystem_xs, lsystem_ys, seed, ca_grid, entropy_vals, results, filename):
    fig = plt.figure(figsize=(20, 12))

    ax1 = fig.add_subplot(2, 3, 1)
    ax1.plot(lsystem_xs, lsystem_ys, 'g-', linewidth=0.8, alpha=0.7)
    ax1.set_title('Parent 1: L-System Tree', fontsize=10)
    ax1.set_aspect('equal')
    ax1.axis('off')

    ax2 = fig.add_subplot(2, 3, 2)
    ax2.bar(range(len(seed)), seed, width=1.0, color='darkblue', alpha=0.6)
    ax2.set_title('Binary Seed: ' + str(params), fontsize=10)
    ax2.set_xlim(0, len(seed))
    ax2.set_ylim(0, 1.2)

    ax3 = fig.add_subplot(2, 3, 3)
    ax3.imshow(ca_grid, cmap='binary', aspect='auto')
    ax3.set_title('Parent 2: Rule 30 Evolution', fontsize=10)
    ax3.set_xlabel('Cell')
    ax3.set_ylabel('Generation')

    ax4 = fig.add_subplot(2, 3, 4)
    ax4.bar(range(len(entropy_vals)), entropy_vals, width=1.0, color='purple', alpha=0.6)
    ax4.set_title('Entropy per Generation', fontsize=10)
    ax4.set_xlim(0, len(entropy_vals))
    ax4.set_ylim(0, 1.1)

    ax5 = fig.add_subplot(2, 3, 5)
    ax5.axis('off')
    info_text = 'Density: {:.4f}\n'.format(results['density'])
    info_text += 'Mean Entropy: {:.4f}\n'.format(results['mean_entropy'])
    info_text += 'Max Entropy: {:.4f}\n'.format(results['max_entropy'])
    info_text += 'Unique Rows: {}/{} ({:.1%})'.format(
        results['unique_rows'], results['shape'][0], results['uniqueness_ratio'])
    ax5.text(0.1, 0.5, info_text, transform=ax5.transAxes, fontsize=12,
            verticalalignment='center', family='monospace')
    ax5.set_title('Analysis Metrics', fontsize=10)

    ax6 = fig.add_subplot(2, 3, 6)
    density = float(np.mean(ca_grid))
    unique_ratio = float(results['uniqueness_ratio'])
    metrics = [density, results['mean_entropy'], results['max_entropy'], unique_ratio]
    labels = ['Density', 'Mean Entropy', 'Max Entropy', 'Uniqueness']
    colors = ['#2ecc71', '#9b59b6', '#e74c3c', '#f39c12']
    bars = ax6.bar(range(len(metrics)), metrics, color=colors, alpha=0.7)
    ax6.set_xticks(range(len(metrics)))
    ax6.set_xticklabels(labels, fontsize=9)
    ax6.set_title('Summary Metrics', fontsize=10)
    for bar, val in zip(bars, metrics):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                '{:.3f}'.format(val), ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: " + filename)

# === MAIN EXPERIMENT ===
def run_hybrid(params, output_dir=OUTPUT_DIR):
    axiom = params["axiom"]
    rules = params["rules"]
    iterations = params["iterations"]
    grid_size = params["grid_size"]
    generations = params["generations"]

    # Parent 1: Generate L-system string
    lstr = generate_lsystem(axiom, rules, iterations)
    lx, ly = lsystem_to_coords(lstr, angle=25, step=1)

    # Breed: L-system -> binary seed -> Rule 30
    seed = lsystem_to_binary_seed(lstr, grid_size)
    grid = evolve_rule30(seed, generations)

    # Analyze
    results, entropy_vals = analyze_grid(grid)
    results["lsystem_length"] = len(lstr)
    results["seed_density"] = float(np.mean(seed))

    # Plot
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    param_str = "iter={}_size={}_gen={}".format(iterations, grid_size, generations)
    fname = os.path.join(output_dir, "hybrid1_{}_{}.png".format(param_str, ts))
    plot_hybrid(params, lx, ly, seed, grid, entropy_vals, results, fname)

    return results, grid, seed, lstr

# === RUN ===
if __name__ == "__main__":
    params_list = [
        {'axiom': 'F', 'rules': {'F': 'FF+[+F-F-F]-[-F+F+F]'}, 'iterations': 3, 'grid_size': 101, 'generations': 100},
        {'axiom': 'X', 'rules': {'X': 'F+[[X]-X]-F[-FX]+X', 'F': 'FF'}, 'iterations': 5, 'grid_size': 201, 'generations': 200},
        {'axiom': 'F', 'rules': {'F': 'F[+F]F[-F]F'}, 'iterations': 4, 'grid_size': 151, 'generations': 150},
        {'axiom': 'A', 'rules': {'A': 'F[+A][-A]', 'F': 'FF'}, 'iterations': 6, 'grid_size': 101, 'generations': 100},
    ]
    print('=== Hybrid 1: L-System x Rule 30 ===')
    for i, params in enumerate(params_list):
        print('\n--- Experiment {} ---'.format(i+1))
        for k, v in params.items():
            print('  {}: {}'.format(k, v))
        try:
            results, grid, seed, lstr = run_hybrid(params)
            print('  Done! Results:')
            print('    L-system length:', results['lsystem_length'])
            print('    Grid shape:', results['shape'])
            print('    Density: {:.4f}'.format(results['density']))
            print('    Mean entropy: {:.4f}'.format(results['mean_entropy']))
            print('    Max entropy: {:.4f}'.format(results['max_entropy']))
            print('    Unique rows: ' + str(results['unique_rows']))
        except Exception as e:
            print('  Error:', e)
    print('\nAll experiments complete.')