import simulation
import random
import numpy as np

def main():
    # Define simulation parameters
    simulation_id = "test_run_1"
    total_simulation_time = 100
    time_step = 1
    num_agents = 50

    # Initialize agent states
    initial_state = {}
    for i in range(num_agents):
        initial_state[f"agent_{i}"] = {
            'x': random.uniform(0, 100),
            'y': random.uniform(0, 100),
            'energy': random.uniform(5, 20) # Give agents some initial energy
        }

    # Run the simulation
    print(f"Starting simulation: {simulation_id}")
    history = simulation.run_simulation(
        simulation_id=simulation_id,
        initial_state=initial_state,
        total_simulation_time=total_simulation_time,
        time_step=time_step
    )
    print("Simulation finished. Check for output files.")

    # Quantitative analysis of energy conservation & dynamics
    initial_snapshot = history[0]
    final_time = max(history.keys())
    final_snapshot = history[final_time]

    init_energies = [s['energy'] for s in initial_snapshot.values()]
    final_energies = [s['energy'] for s in final_snapshot.values()]

    print(f"\n--- Energy Invariant Analysis ---")
    print(f"Initial Total Energy: {sum(init_energies):.6f} (Mean: {sum(init_energies)/len(init_energies):.6f}, Std: {np.std(init_energies):.6f})")
    print(f"Final Total Energy:   {sum(final_energies):.6f} (Mean: {sum(final_energies)/len(final_energies):.6f}, Std: {np.std(final_energies):.6f})")
    print(f"Energy Delta:         {abs(sum(final_energies) - sum(init_energies)):.6e}")

if __name__ == "__main__":
    main()
