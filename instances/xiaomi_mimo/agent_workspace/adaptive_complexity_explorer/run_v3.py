from ecosystem_v3 import Ecosystem
import json

def run_simulation(num_generations=500, initial_population=30):
    ecosystem = Ecosystem(initial_population=initial_population, max_resources=100)
    print("Running Ecosystem V3...")
    print(f"Initial population: {initial_population}")

    for gen in range(num_generations):
        ecosystem.competition_round()
        ecosystem.reproduction_phase()
        ecosystem.record_history()
        ecosystem.generation += 1

        alive = len([o for o in ecosystem.organisms if o.alive])
        if gen % 50 == 0:
            print(f"Gen {gen}: Pop={alive}, Res={ecosystem.resources.amount:.2f}")
        if alive == 0:
            print(f"Extinction at gen {gen}!")
            break

    print(f"\nSimulation complete! {len(ecosystem.history['generation'])} generations")
    with open('history_v3.json', 'w') as f:
        json.dump(ecosystem.history, f, indent=2)
    return ecosystem

if __name__ == "__main__":
    run_simulation()
