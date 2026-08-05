#!/usr/bin/env python3
"""
Extended run of Ecosystem V4 for detailed analysis
"""
import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

exec(open('ecosystem_v4.py').read())

def run_extended():
    """Run extended simulation with detailed logging"""
    print("\n" + "="*60)
    print("Extended Ecosystem V4 Run")
    print("="*60)
    
    world = SpatialWorld(width=30, height=30)
    world.seed_organisms(n=25)
    
    # Run with more detailed logging
    total_gen = 600
    for _ in range(total_gen // 100):
        world.run(generations=100)
        
        # Log detailed state
        gen = world.generation
        pop = len(world.organisms)
        
        # Resource stats from grid
        total_resources = float(np.sum(world.grid_resources))
        max_resources = float(np.max(world.grid_resources))
        min_resources = float(np.min(world.grid_resources))
        
        # Trait stats from history
        last_traits = world.history[-1]['traits'] if world.history else {}
        
        print(f"\nGen {gen}: pop={pop}, total_res={total_resources:.0f}")
        print(f"  Resource range: [{min_resources:.1f}, {max_resources:.1f}]")
        print(f"  Key traits: speed={last_traits.get('avg_speed', 0):.3f}, "
              f"coop={last_traits.get('avg_cooperation', 0):.3f}, "
              f"aware={last_traits.get('avg_awareness', 0):.3f}")
    
    # Save detailed history
    with open('extended_history.json', 'w') as f:
        json.dump(world.history, f, indent=2)
    
    print(f"\nFinal population: {len(world.organisms)}")
    print(f"Extended history saved to extended_history.json")
    
    return world

if __name__ == '__main__':
    run_extended()
