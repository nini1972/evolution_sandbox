from ecosystem_v2 import Ecosystem
from visualize_v2 import plot_ecosystem_history
import json

def run_simulation(num_generations=200, initial_population=50):
    ecosystem = Ecosystem(initial_population=initial_population, max_resources=100)
    print("Starting Competitive Ecosystem Simulation v2...")
    print(f"Initial population: {initial_population}")
    print("Features: Environmental shocks, frugality trait")
    
    for gen in range(num_generations):
        ecosystem.competition_round()
        ecosystem.reproduction_phase()
        ecosystem.record_history()
        ecosystem.generation += 1
        
        if gen % 20 == 0:
            pop = len([o for o in ecosystem.organisms if o.alive])
            print(f"Gen {gen}: Population={pop}, Resources={ecosystem.resources.amount:.2f}")
            
            if pop == 0:
                print("Extinction event! Simulation paused.")
                break
    
    print("\nSimulation complete!")
    plot_ecosystem_history(ecosystem.history)
    
    with open('history_v2.json', 'w') as f:
        json.dump(ecosystem.history, f, indent=2)
    
    return ecosystem

if __name__ == "__main__":
    run_simulation()