    current_time = 0
    while current_time < total_simulation_time:
        # Agent actions and interactions
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


        # Record snapshot of the simulation state
        simulation_history[current_time] = copy.deepcopy(simulation_state)

        current_time += time_step
        # Optional: Add a break condition or more complex time step management
        if current_time % 10 == 0: # Print every 10 time steps
            print(f"Simulation {simulation_id}: Time = {current_time}/{total_simulation_time}")

    print(f"Simulation '{simulation_id}' finished.")

    return simulation_history

if __name__ == "__main__":
    initial_state = {
        "agent_1": {"x": 10, "y": 10, "energy": 1.0},
        "agent_2": {"x": 20, "y": 20, "energy": 1.0},
    }
    total_time = 100
    dt = 1
    history = run_simulation("test_sim", initial_state, total_time, dt)
    print("Simulation history length:", len(history))
    print("Last state:", history[total_time - dt])
