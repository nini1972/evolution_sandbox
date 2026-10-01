import random
import copy
import matplotlib.pyplot as plt
import numpy as np

def run_simulation(simulation_id, initial_state, total_simulation_time, time_step):
    simulation_state = copy.deepcopy(initial_state)
    simulation_history = {}
    average_energies = []

    current_time = 0
    while current_time < total_simulation_time:
        # Agent actions and interactions
        total_energy_this_step = 0
        num_agents_with_energy = 0
        for agent_id, agent_state in simulation_state.items():
            # Example: Agents move randomly
            agent_state['x'] += random.uniform(-1, 1)
            agent_state['y'] += random.uniform(-1, 1)

            # Keep agents within bounds (example: 0 to 100)
            agent_state['x'] = max(0, min(100, agent_state['x']))
            agent_state['y'] = max(0, min(100, agent_state['y']))

            # Example: Agents interact if they are close enough
            for other_agent_id, other_agent_state in simulation_state.items():
                if agent_id != other_agent_id:
                    distance = ((agent_state['x'] - other_agent_state['x'])**2 + \
                                (agent_state['y'] - other_agent_state['y'])**2)**0.5
                    if distance < 5: # Interaction radius
                        # Example interaction: agents exchange some 'energy'
                        if 'energy' in agent_state and 'energy' in other_agent_state:
                            transfer_amount = 0.1 # Small amount of energy transfer
                            if agent_state['energy'] > transfer_amount:
                                agent_state['energy'] -= transfer_amount
                                other_agent_state['energy'] += transfer_amount
            if 'energy' in agent_state:
                total_energy_this_step += agent_state['energy']
                num_agents_with_energy += 1

        if num_agents_with_energy > 0:
            average_energies.append(total_energy_this_step / num_agents_with_energy)
        else:
            average_energies.append(0.0) # Append 0 if no agents have energy

        # Record snapshot of the simulation state
        simulation_history[current_time] = copy.deepcopy(simulation_state)

        current_time += time_step
        # Optional: Add a break condition or more complex time step management
        if current_time % 10 == 0: # Print every 10 time steps
            print(f"Simulation {simulation_id}: Time = {current_time}/{total_simulation_time}")

    print(f"Simulation '{simulation_id}' finished.")

    # Plotting the average energy
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(average_energies)), average_energies)
    plt.xlabel("Time Step")
    plt.ylabel("Average Energy")
    plt.title(f"Average Agent Energy Over Time for Simulation {simulation_id}")
    plt.grid(True)
    plt.savefig(f"average_energy_{simulation_id}.png")
    plt.close()

    return simulation_history

