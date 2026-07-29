from ecosystem_v2 import Ecosystem
from organism_v2 import Organism
from visualize_v2 import plot_ecosystem_history
import json
import numpy as np

def run_sustainable_simulation(num_generations=500, initial_population=30):
    ecosystem = Ecosystem(initial_population=initial_population, max_resources=100)
    print("Running Sustainable Ecosystem Simulation...")
    print(f"Initial population: {initial_population}")
    
    for gen in range(num_generations):
        ecosystem.competition_round()
        ecosystem.reproduction_phase()
        ecosystem.record_history()
        ecosystem.generation += 1
        
        if gen % 50 == 0:
            pop = len([o for o in ecosystem.organisms if o.alive])
            print(f"Gen {gen}: Pop={pop}, Resources={ecosystem.resources.amount:.2f}")
            
            if pop == 0:
                print("Extinction! Resetting with founders...")
                for _ in range(10):
                    ecosystem.organisms.append(Organism())
                ecosystem.generation += 1
    
    print("\nSimulation complete!")
    plot_ecosystem_history(ecosystem.history, save_path='sustainable_evolution.png')
    
    with open('sustainable_history.json', 'w') as f:
        json.dump(ecosystem.history, f, indent=2)
    
    return ecosystem

if __name__ == "__main__":
    run_sustainable_simulation()