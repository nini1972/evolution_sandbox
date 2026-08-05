#!/usr/bin/env python3
"""
Comparative Experiment Runner for Ecosystem V4
Tests how different initial conditions affect emergent complexity
"""
import sys
import os
import json
import time

# Add the current directory to path so we can import the simulation
sys.path.insert(0, os.path.dirname(__file__))

# We need to run the simulation module
exec(open('ecosystem_v4.py').read())

def run_experiment(name, width=25, height=25, n_orgs=30, generations=300):
    """Run a single experiment and return results"""
    print(f"\n{'='*50}")
    print(f"Running experiment: {name}")
    print(f"{'='*50}")
    
    world = SpatialWorld(width=width, height=height)
    world.seed_organisms(n=n_orgs)
    
    start_time = time.time()
    world.run(generations=generations)
    elapsed = time.time() - start_time
    
    result = {
        'name': name,
        'config': {
            'width': width,
            'height': height,
            'n_orgs': n_orgs,
            'generations': generations,
        },
        'history': world.history,
        'final_state': {
            'population': len(world.organisms),
            'generations_run': world.generation,
            'elapsed_seconds': elapsed,
        }
    }
    
    print(f"Completed in {elapsed:.1f}s, final pop: {len(world.organisms)}")
    return result

if __name__ == '__main__':
    experiments = []
    
    # Experiment 1: Small world, sparse
    experiments.append(run_experiment(
        "Small Sparse (15x15, 15 orgs)",
        width=15, height=15, n_orgs=15, generations=150
    ))
    
    # Experiment 2: Small world, dense
    experiments.append(run_experiment(
        "Small Dense (15x15, 30 orgs)",
        width=15, height=15, n_orgs=30, generations=150
    ))
    
    # Experiment 3: Large world, sparse
    experiments.append(run_experiment(
        "Large Sparse (25x25, 20 orgs)",
        width=25, height=25, n_orgs=20, generations=150
    ))
    
    # Save all results
    with open('experiment_results.json', 'w') as f:
        # We can't save full history for all (too large), just summary
        summary = []
        for exp in experiments:
            summary.append({
                'name': exp['name'],
                'config': exp['config'],
                'final_state': exp['final_state'],
                'history_summary': {
                    'generations': [h['generation'] for h in exp['history']],
                    'population': [h['population'] for h in exp['history']],
                    'diversity': [h['diversity'] for h in exp['history']],
                    'spatial_spread': [h['spatial_spread'] for h in exp['history']],
                    'avg_energy': [h['avg_energy'] for h in exp['history']],
                    'traits': exp['history'][-1]['traits'] if exp['history'] else {},
                }
            })
        json.dump(summary, f, indent=2)
    
    print(f"\nAll experiments complete! Results saved to experiment_results.json")
    print(f"Total experiments: {len(experiments)}")
