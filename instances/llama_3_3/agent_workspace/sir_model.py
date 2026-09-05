import random

def simulate_sir_model(graph, initial_infected_nodes, beta, gamma, num_steps):
    """Simulates the SIR model on a given graph."""
    states = {node: 'S' for node in graph.nodes()}
    for node in initial_infected_nodes:
        states[node] = 'I'

    history = {'S': [], 'I': [], 'R': []}

    for step in range(num_steps):
        new_states = states.copy()
        
        infected_count = sum(1 for state in states.values() if state == 'I')
        susceptible_count = sum(1 for state in states.values() if state == 'S')
        recovered_count = sum(1 for state in states.values() if state == 'R')
        history['S'].append(susceptible_count)
        history['I'].append(infected_count)
        history['R'].append(recovered_count)

        for node in graph.nodes():
            if states[node] == 'I':
                # Try to recover
                if random.random() < gamma:
                    new_states[node] = 'R'
                # Try to infect neighbors
                else:
                    for neighbor in graph.neighbors(node):
                        if states[neighbor] == 'S' and random.random() < beta:
                            new_states[neighbor] = 'I'
        states = new_states
    
    # Store final counts
    infected_count = sum(1 for state in states.values() if state == 'I')
    susceptible_count = sum(1 for state in states.values() if state == 'S')
    recovered_count = sum(1 for state in states.values() if state == 'R')
    history['S'].append(susceptible_count)
    history['I'].append(infected_count)
    history['R'].append(recovered_count)

    print(f"SIR simulation finished after {num_steps} steps.")
    return history

def simulate_sis_model(graph, initial_infected_nodes, beta, gamma, num_steps):
    """Simulates the SIS model on a given graph."""
    states = {node: 'S' for node in graph.nodes()}
    for node in initial_infected_nodes:
        states[node] = 'I'

    history = {'S': [], 'I': []}

    for step in range(num_steps):
        new_states = states.copy()
        
        infected_count = sum(1 for state in states.values() if state == 'I')
        susceptible_count = sum(1 for state in states.values() if state == 'S')
        history['S'].append(susceptible_count)
        history['I'].append(infected_count)

        for node in graph.nodes():
            if states[node] == 'I':
                # Try to recover to Susceptible state
                if random.random() < gamma:
                    new_states[node] = 'S'
                # Try to infect neighbors
                else:
                    for neighbor in graph.neighbors(node):
                        if states[neighbor] == 'S' and random.random() < beta:
                            new_states[neighbor] = 'I'
        states = new_states

    # Store final counts
    infected_count = sum(1 for state in states.values() if state == 'I')
    susceptible_count = sum(1 for state in states.values() if state == 'S')
    history['S'].append(susceptible_count)
    history['I'].append(infected_count)

    print(f"SIS simulation finished after {num_steps} steps.")
    return history

def simulate_seir_model(graph, initial_infected_nodes, beta, epsilon, gamma, num_steps):
    """Simulates the SEIR model on a given graph."""
    states = {node: 'S' for node in graph.nodes()}
    for node in initial_infected_nodes:
        states[node] = 'E'  # Start as Exposed in SEIR model

    history = {'S': [], 'E': [], 'I': [], 'R': []}

    for step in range(num_steps):
        new_states = states.copy()

        susceptible_count = sum(1 for state in states.values() if state == 'S')
        exposed_count = sum(1 for state in states.values() if state == 'E')
        infected_count = sum(1 for state in states.values() if state == 'I')
        recovered_count = sum(1 for state in states.values() if state == 'R')
        history['S'].append(susceptible_count)
        history['E'].append(exposed_count)
        history['I'].append(infected_count)
        history['R'].append(recovered_count)

        for node in graph.nodes():
            if states[node] == 'S':
                # Try to get exposed by infected neighbors
                for neighbor in graph.neighbors(node):
                    if states[neighbor] == 'I' and random.random() < beta:
                        new_states[node] = 'E'
                        break  # Only get exposed once per step
            elif states[node] == 'E':
                # Try to become infectious
                if random.random() < epsilon:
                    new_states[node] = 'I'
            elif states[node] == 'I':
                # Try to recover
                if random.random() < gamma:
                    new_states[node] = 'R'
        states = new_states

    # Store final counts
    susceptible_count = sum(1 for state in states.values() if state == 'S')
    exposed_count = sum(1 for state in states.values() if state == 'E')
    infected_count = sum(1 for state in states.values() if state == 'I')
    recovered_count = sum(1 for state in states.values() if state == 'R')
    history['S'].append(susceptible_count)
    history['E'].append(exposed_count)
    history['I'].append(infected_count)
    history['R'].append(recovered_count)

    print(f"SEIR simulation finished after {num_steps} steps.")
    return history
