#!/usr/bin/env python3
"""
Continuous Dynamics Archaeological Exploration
Investigating symmetry-chaos relationships in continuous dynamical systems
while World C processes 2D CA analysis
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import json
from collections import defaultdict

def lorenz_system(state, t, sigma=10.0, rho=28.0, beta=8.0/3.0):
    """Standard Lorenz attractor system."""
    x, y, z = state
    dx_dt = sigma * (y - x)
    dy_dt = x * (rho - z) - y  
    dz_dt = x * y - beta * z
    return [dx_dt, dy_dt, dz_dt]

def symmetric_lorenz(state, t, sigma=10.0, rho=28.0, beta=8.0/3.0):
    """Symmetric variant of Lorenz - x and y terms are symmetric."""
    x, y, z = state
    dx_dt = sigma * (y - x)
    dy_dt = sigma * (x - y) + x * (rho - z)  # Added symmetry term
    dz_dt = x * y - beta * z
    return [dx_dt, dy_dt, dz_dt]

def rossler_system(state, t, a=0.2, b=0.2, c=5.7):
    """Standard Rössler attractor system."""
    x, y, z = state
    dx_dt = -y - z
    dy_dt = x + a * y
    dz_dt = b + z * (x - c)
    return [dx_dt, dy_dt, dz_dt]

def symmetric_rossler(state, t, a=0.2, b=0.2, c=5.7):
    """Symmetric variant of Rössler."""
    x, y, z = state
    dx_dt = -y - z
    dy_dt = x + a * y
    dz_dt = b + z * (x - c) + a * z  # Added symmetry term
    return [dx_dt, dy_dt, dz_dt]

def thomas_system(state, t, b=0.208186):
    """Thomas' cyclically symmetric attractor - inherently symmetric."""
    x, y, z = state
    dx_dt = np.sin(y) - b * x
    dy_dt = np.sin(z) - b * y
    dz_dt = np.sin(x) - b * z
    return [dx_dt, dy_dt, dz_dt]

def duffing_oscillator(state, t, alpha=-1.0, beta=1.0, gamma=0.3, omega=1.0):
    """Duffing oscillator - can be made symmetric."""
    x, dx_dt = state
    d2x_dt2 = -alpha * x - beta * x**3 + gamma * np.cos(omega * t)
    return [dx_dt, d2x_dt2]

def symmetric_duffing(state, t, alpha=-1.0, beta=1.0, gamma=0.3, omega=1.0):
    """Symmetric Duffing oscillator."""
    x, dx_dt = state
    # Add symmetric damping term
    d2x_dt2 = -alpha * x - beta * x**3 + gamma * np.cos(omega * t) - 0.1 * np.sign(dx_dt) * dx_dt**2
    return [dx_dt, d2x_dt2]

def calculate_trajectory_complexity(trajectory, method='box_counting'):
    """
    Calculate complexity metrics for continuous trajectories.
    """
    if method == 'box_counting':
        # Simple box-counting dimension estimation
        if trajectory.shape[1] >= 2:
            x, y = trajectory[:, 0], trajectory[:, 1]
            
            # Normalize coordinates
            x_norm = (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else x * 0
            y_norm = (y - y.min()) / (y.max() - y.min()) if y.max() != y.min() else y * 0
            
            # Count boxes at different scales
            scales = [0.1, 0.05, 0.02, 0.01]
            counts = []
            
            for scale in scales:
                grid_size = int(1.0 / scale)
                occupied_boxes = set()
                
                for i in range(len(x_norm)):
                    box_x = int(x_norm[i] * grid_size)
                    box_y = int(y_norm[i] * grid_size)
                    occupied_boxes.add((box_x, box_y))
                
                counts.append(len(occupied_boxes))
            
            # Estimate dimension from log-log slope
            if len(counts) > 1 and all(c > 0 for c in counts):
                log_scales = np.log(scales)
                log_counts = np.log(counts)
                slope = np.polyfit(log_scales, log_counts, 1)[0]
                return -slope  # Box-counting dimension
    
    elif method == 'variance':
        # Trajectory variance as complexity measure
        return np.var(trajectory, axis=0).sum()
    
    elif method == 'path_length':
        # Total path length
        if len(trajectory) > 1:
            diffs = np.diff(trajectory, axis=0)
            distances = np.sqrt(np.sum(diffs**2, axis=1))
            return np.sum(distances)
    
    return 0.0

def is_system_symmetric(system_name):
    """Classify systems by symmetry properties."""
    symmetric_systems = ['symmetric_lorenz', 'symmetric_rossler', 'thomas_system', 'symmetric_duffing']
    return system_name in symmetric_systems

def run_continuous_dynamics_analysis():
    """
    Comprehensive analysis of symmetry-chaos relationships in continuous systems.
    """
    print("Starting Continuous Dynamics Symmetry-Chaos Archaeological Survey...")
    
    # Define systems to analyze
    systems = {
        'lorenz': lorenz_system,
        'symmetric_lorenz': symmetric_lorenz,
        'rossler': rossler_system, 
        'symmetric_rossler': symmetric_rossler,
        'thomas': thomas_system,
    }
    
    # 2D systems (for Duffing oscillators)
    systems_2d = {
        'duffing': duffing_oscillator,
        'symmetric_duffing': symmetric_duffing,
    }
    
    # Integration parameters
    t = np.linspace(0, 50, 5000)
    t_2d = np.linspace(0, 100, 10000)  # Longer for oscillators
    
    # Multiple initial conditions for sensitivity analysis
    initial_conditions_3d = [
        [1.0, 1.0, 1.0],
        [0.1, 0.1, 0.1], 
        [10.0, 10.0, 10.0],
        [-1.0, -1.0, -1.0],
        [1.0, -1.0, 0.5],
        [0.5, 2.0, -0.5],
        [2.0, 0.1, 1.5],
        [-0.5, 0.8, -1.2]
    ]
    
    initial_conditions_2d = [
        [1.0, 0.0],
        [0.1, 0.1],
        [2.0, 0.5],
        [-1.0, -0.5],
        [0.5, 1.0],
        [-0.2, 0.8],
        [1.5, -1.0],
        [0.3, -0.3]
    ]
    
    results = []
    
    # Analyze 3D systems
    for system_name, system_func in systems.items():
        print(f"Analyzing {system_name}...")
        
        complexities = []
        trajectories = []
        
        for ic in initial_conditions_3d:
            try:
                trajectory = odeint(system_func, ic, t)
                
                # Calculate multiple complexity measures
                box_dim = calculate_trajectory_complexity(trajectory, 'box_counting')
                variance_comp = calculate_trajectory_complexity(trajectory, 'variance')
                path_length = calculate_trajectory_complexity(trajectory, 'path_length')
                
                complexities.append({
                    'box_dimension': box_dim,
                    'variance': variance_comp,
                    'path_length': path_length,
                    'combined': box_dim + np.log(variance_comp + 1) + np.log(path_length + 1)
                })
                trajectories.append(trajectory)
                
            except Exception as e:
                print(f"  Error with IC {ic}: {e}")
                continue
        
        if complexities:
            avg_complexity = np.mean([c['combined'] for c in complexities])
            std_complexity = np.std([c['combined'] for c in complexities])
            
            results.append({
                'system': system_name,
                'dimension': 3,
                'symmetric': is_system_symmetric(system_name),
                'avg_complexity': avg_complexity,
                'std_complexity': std_complexity,
                'individual_complexities': complexities,
                'num_trajectories': len(trajectories)
            })
            
            print(f"  {system_name}: avg_complexity={avg_complexity:.3f}, symmetric={is_system_symmetric(system_name)}")
    
    # Analyze 2D systems (Duffing oscillators)
    for system_name, system_func in systems_2d.items():
        print(f"Analyzing {system_name}...")
        
        complexities = []
        trajectories = []
        
        for ic in initial_conditions_2d:
            try:
                trajectory = odeint(system_func, ic, t_2d)
                
                # Calculate complexity measures
                box_dim = calculate_trajectory_complexity(trajectory, 'box_counting')
                variance_comp = calculate_trajectory_complexity(trajectory, 'variance')
                path_length = calculate_trajectory_complexity(trajectory, 'path_length')
                
                complexities.append({
                    'box_dimension': box_dim,
                    'variance': variance_comp,
                    'path_length': path_length,
                    'combined': box_dim + np.log(variance_comp + 1) + np.log(path_length + 1)
                })
                trajectories.append(trajectory)
                
            except Exception as e:
                print(f"  Error with IC {ic}: {e}")
                continue
        
        if complexities:
            avg_complexity = np.mean([c['combined'] for c in complexities])
            std_complexity = np.std([c['combined'] for c in complexities])
            
            results.append({
                'system': system_name,
                'dimension': 2,
                'symmetric': is_system_symmetric(system_name),
                'avg_complexity': avg_complexity,
                'std_complexity': std_complexity,
                'individual_complexities': complexities,
                'num_trajectories': len(trajectories)
            })
            
            print(f"  {system_name}: avg_complexity={avg_complexity:.3f}, symmetric={is_system_symmetric(system_name)}")
    
    # Statistical analysis
    symmetric_systems = [r for r in results if r['symmetric']]
    asymmetric_systems = [r for r in results if not r['symmetric']]
    
    print(f"\nFound {len(symmetric_systems)} symmetric and {len(asymmetric_systems)} asymmetric systems")
    
    if symmetric_systems and asymmetric_systems:
        sym_complexities = [s['avg_complexity'] for s in symmetric_systems]
        asym_complexities = [s['avg_complexity'] for s in asymmetric_systems]
        
        sym_mean = np.mean(sym_complexities)
        asym_mean = np.mean(asym_complexities)
        
        if asym_mean > 0:
            sensitivity_ratio = sym_mean / asym_mean
            print(f"Continuous Dynamics Sensitivity Ratio: {sensitivity_ratio:.3f}")
            print(f"Symmetric mean: {sym_mean:.3f}, Asymmetric mean: {asym_mean:.3f}")
        
    # Create visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: System complexity comparison
    system_names = [r['system'] for r in results]
    complexities = [r['avg_complexity'] for r in results]
    colors = ['red' if r['symmetric'] else 'blue' for r in results]
    
    ax1.bar(range(len(system_names)), complexities, color=colors, alpha=0.7)
    ax1.set_xlabel('System')
    ax1.set_ylabel('Average Complexity')
    ax1.set_title('Continuous Systems Complexity by Symmetry')
    ax1.set_xticks(range(len(system_names)))
    ax1.set_xticklabels(system_names, rotation=45, ha='right')
    
    # Plot 2: Boxplot comparison
    if symmetric_systems and asymmetric_systems:
        sym_data = [s['avg_complexity'] for s in symmetric_systems]
        asym_data = [s['avg_complexity'] for s in asymmetric_systems]
        box_plot = ax2.boxplot([sym_data, asym_data])
        ax2.set_xticklabels(['Symmetric', 'Asymmetric'])
        ax2.set_ylabel('Average Complexity')
        ax2.set_title('Complexity Distribution by Symmetry')
    
    # Plot 3: Example trajectory (Lorenz)
    try:
        lorenz_traj = odeint(lorenz_system, [1, 1, 1], t)
        ax3.plot(lorenz_traj[:, 0], lorenz_traj[:, 1], 'b-', alpha=0.7, linewidth=0.5)
        ax3.set_xlabel('X')
        ax3.set_ylabel('Y')
        ax3.set_title('Lorenz Attractor (Asymmetric)')
        ax3.grid(True, alpha=0.3)
    except:
        ax3.text(0.5, 0.5, 'Trajectory plot failed', ha='center', va='center', transform=ax3.transAxes)
    
    # Plot 4: Example symmetric trajectory (Thomas)
    try:
        thomas_traj = odeint(thomas_system, [1, 1, 1], t)
        ax4.plot(thomas_traj[:, 0], thomas_traj[:, 1], 'r-', alpha=0.7, linewidth=0.5)
        ax4.set_xlabel('X')
        ax4.set_ylabel('Y')
        ax4.set_title('Thomas Attractor (Symmetric)')
        ax4.grid(True, alpha=0.3)
    except:
        ax4.text(0.5, 0.5, 'Trajectory plot failed', ha='center', va='center', transform=ax4.transAxes)
    
    plt.tight_layout()
    plt.savefig('continuous_dynamics_symmetry_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save results
    summary = {
        'analysis_type': 'Continuous_Dynamics_Symmetry_Chaos',
        'systems_analyzed': len(results),
        'symmetric_systems': len(symmetric_systems),
        'asymmetric_systems': len(asymmetric_systems),
        'results': results,
        'conclusions': {
            'symmetric_mean': sym_mean if symmetric_systems and asymmetric_systems else None,
            'asymmetric_mean': asym_mean if symmetric_systems and asymmetric_systems else None,
            'sensitivity_ratio': sensitivity_ratio if symmetric_systems and asymmetric_systems and asym_mean > 0 else None
        }
    }
    
    with open('continuous_dynamics_results.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\nAnalysis complete! Generated:")
    print(f"- continuous_dynamics_symmetry_analysis.png")
    print(f"- continuous_dynamics_results.json")
    
    return results, summary

if __name__ == "__main__":
    results, summary = run_continuous_dynamics_analysis()
    print("Continuous Dynamics Archaeological Survey Complete!")