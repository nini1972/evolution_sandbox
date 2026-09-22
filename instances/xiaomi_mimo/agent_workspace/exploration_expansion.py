#!/usr/bin/env python3
"""
Exploration of new systems to fill dark matter regions
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define new systems to explore
new_systems = {
    "Rössler Attractor": {
        "type": "ODE",
        "dimensions": 3,
        "regime": "Strange Attractor",
        "parameters": {"a": 0.2, "b": 0.2, "c": 5.7},
        "expected_properties": {
            "lyapunov": 0.07,
            "correlation_dim": 2.01,
            "entropy": 0.6,
            "fractal_dim": 2.01,
            "temporal_memory": 0.5,
            "coupling": 0.0,
            "spatial_entropy": 0.0
        }
    },
    "Duffing Oscillator": {
        "type": "ODE",
        "dimensions": 2,
        "regime": "Forced Chaos",
        "parameters": {"alpha": -1.0, "beta": 1.0, "delta": 0.3, "gamma": 0.37, "omega": 1.2},
        "expected_properties": {
            "lyapunov": 0.1,
            "correlation_dim": 1.5,
            "entropy": 0.5,
            "fractal_dim": 1.5,
            "temporal_memory": 0.4,
            "coupling": 0.0,
            "spatial_entropy": 0.0
        }
    },
    "Van der Pol Oscillator": {
        "type": "ODE",
        "dimensions": 2,
        "regime": "Limit Cycle",
        "parameters": {"mu": 1.0},
        "expected_properties": {
            "lyapunov": 0.0,
            "correlation_dim": 1.0,
            "entropy": 0.0,
            "fractal_dim": 1.0,
            "temporal_memory": 0.3,
            "coupling": 0.0,
            "spatial_entropy": 0.0
        }
    },
    "Hindmarsh-Rose Neuron": {
        "type": "ODE",
        "dimensions": 3,
        "regime": "Spiking Chaos",
        "parameters": {"a": 1.0, "b": 3.0, "c": 1.0, "d": 5.0, "r": 0.006, "s": 4.0, "x_rest": -1.6},
        "expected_properties": {
            "lyapunov": 0.15,
            "correlation_dim": 1.8,
            "entropy": 0.7,
            "fractal_dim": 1.8,
            "temporal_memory": 0.6,
            "coupling": 0.0,
            "spatial_entropy": 0.0
        }
    },
    "Double Pendulum": {
        "type": "Hamiltonian",
        "dimensions": 4,
        "regime": "Hyperchaotic",
        "parameters": {"m1": 1.0, "m2": 1.0, "l1": 1.0, "l2": 1.0, "g": 9.81},
        "expected_properties": {
            "lyapunov": 2.0,
            "correlation_dim": 3.5,
            "entropy": 2.5,
            "fractal_dim": 3.5,
            "temporal_memory": 0.1,
            "coupling": 0.0,
            "spatial_entropy": 0.0
        }
    },
    "Hénon Map (Generalized)": {
        "type": "Map",
        "dimensions": 2,
        "regime": "Strange Attractor",
        "parameters": {"a": 1.4, "b": 0.3},
        "expected_properties": {
            "lyapunov": 0.42,
            "correlation_dim": 1.2,
            "entropy": 0.5,
            "fractal_dim": 1.26,
            "temporal_memory": 0.3,
            "coupling": 0.0,
            "spatial_entropy": 0.0
        }
    },
    "Ikeda Map": {
        "type": "Map",
        "dimensions": 2,
        "regime": "Strange Attractor",
        "parameters": {"u": 9.0},
        "expected_properties": {
            "lyapunov": 0.5,
            "correlation_dim": 1.7,
            "entropy": 0.6,
            "fractal_dim": 1.7,
            "temporal_memory": 0.4,
            "coupling": 0.0,
            "spatial_entropy": 0.0
        }
    },
    "Chen Attractor": {
        "type": "ODE",
        "dimensions": 3,
        "regime": "Hyperchaotic",
        "parameters": {"a": 35.0, "b": 3.0, "c": 28.0},
        "expected_properties": {
            "lyapunov": 2.0,
            "correlation_dim": 2.0,
            "entropy": 1.5,
            "fractal_dim": 2.1,
            "temporal_memory": 0.2,
            "coupling": 0.0,
            "spatial_entropy": 0.0
        }
    },
    "Lotka-Volterra with Migration": {
        "type": "Ecology",
        "dimensions": 4,
        "regime": "Ecological Chaos",
        "parameters": {"a": 1.0, "b": 0.5, "c": 0.5, "d": 2.0, "e": 0.1, "f": 0.1},
        "expected_properties": {
            "lyapunov": 0.05,
            "correlation_dim": 2.5,
            "entropy": 0.4,
            "fractal_dim": 2.5,
            "temporal_memory": 0.7,
            "coupling": 0.3,
            "spatial_entropy": 0.2
        }
    },
    "Neural Network with Spike-Timing": {
        "type": "Neural",
        "dimensions": 10,
        "regime": "Biological",
        "parameters": {"tau": 20.0, "v_rest": -65.0, "v_thresh": -50.0, "w": 0.5},
        "expected_properties": {
            "lyapunov": 0.02,
            "correlation_dim": 3.0,
            "entropy": 0.3,
            "fractal_dim": 3.0,
            "temporal_memory": 0.8,
            "coupling": 0.4,
            "spatial_entropy": 0.5
        }
    },
    "Lattice Gas Automaton": {
        "type": "CA",
        "dimensions": 2,
        "regime": "Fluid Dynamics",
        "parameters": {"density": 0.6, "collision_rule": "HPP"},
        "expected_properties": {
            "lyapunov": 0.3,
            "correlation_dim": 1.8,
            "entropy": 0.8,
            "fractal_dim": 1.8,
            "temporal_memory": 0.2,
            "coupling": 0.6,
            "spatial_entropy": 0.7
        }
    },
    "Turing Pattern Formation": {
        "type": "PDE",
        "dimensions": 2,
        "regime": "Pattern Formation",
        "parameters": {"Du": 0.16, "Dv": 0.08, "f": 0.035, "k": 0.065},
        "expected_properties": {
            "lyapunov": 0.0,
            "correlation_dim": 2.5,
            "entropy": 0.4,
            "fractal_dim": 2.5,
            "temporal_memory": 0.1,
            "coupling": 0.5,
            "spatial_entropy": 0.8
        }
    }
}

# Create a visualization of the new systems
fig = plt.figure(figsize=(16, 10))
ax = fig.add_subplot(111, projection='3d')

# Plot existing systems
existing_colors = {
    'Strange': '#e94560',
    'Periodic': '#0f3460',
    'Class III': '#533483',
    'Class IV': '#1a1a2e',
    'Synchronized': '#0f3460',
    'Chimera': '#533483',
    'Bridge': '#e94560',
    'Weak Chaos': '#0f3460',
    'Double Scroll': '#533483',
    'Mixed': '#e94560',
    'KAM': '#0f3460',
    'Global Chaos': '#533483',
    'Self-Similar': '#e94560',
    'Pattern Formation': '#0f3460',
    'Evolvable': '#533483',
    'Fixed Strategy': '#e94560',
    'Biological': '#1a1a2e',
    'Neural': '#0f3460',
    'Biochemical': '#533483',
    'Epidemiological': '#e94560',
    'Deterministic': '#1a1a2e'
}

# Add new systems with different colors
new_colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', 
              '#dfe6e9', '#fdcb6e', '#e17055', '#74b9ff', '#a29bfe',
              '#55efc4', '#fab1a0']

for i, (name, data) in enumerate(new_systems.items()):
    props = data['expected_properties']
    x = props['lyapunov']
    y = props['correlation_dim']
    z = props['entropy']
    
    ax.scatter(x, y, z, c=new_colors[i], s=100, alpha=0.8, edgecolor='black', linewidth=0.5)
    ax.text(x, y, z, name, fontsize=8)

ax.set_xlabel('Lyapunov Exponent', fontsize=10)
ax.set_ylabel('Correlation Dimension', fontsize=10)
ax.set_zlabel('Entropy', fontsize=10)
ax.set_title('New Systems to Explore in Dark Matter Regions', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.savefig('new_systems_exploration.png', dpi=150, bbox_inches='tight')
print('Saved new_systems_exploration.png')

# Create a summary of the new systems
summary = {
    "total_new_systems": len(new_systems),
    "dark_matter_coverage": "12 new systems added",
    "predicted_archetypes": [
        "Hyperchaotic (Double Pendulum, Chen)",
        "Biological (Hindmarsh-Rose, Neural Network, LV Migration)",
        "Pattern Formation (Turing, Lattice Gas)",
        "Limit Cycle (Van der Pol)"
    ],
    "potential_invariants": [
        "Hamiltonian systems show high Lyapunov + high correlation dimension",
        "Biological systems show high temporal memory + moderate coupling",
        "Pattern formation systems show high spatial entropy + low temporal memory"
    ]
}

# Save summary to JSON
with open('new_systems_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("Summary saved to new_systems_summary.json")
