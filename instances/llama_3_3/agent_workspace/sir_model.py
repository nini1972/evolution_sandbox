import random

def simulate_sir_model(graph, initial_infected_nodes, beta, gamma, num_steps):
    """Simulates the SIR model on a given graph."""
    states = {node: 'S' for node in graph.nodes()}
    for node in initial_infected_nodes:
        states[node] = 'I'

    history = {'S': [], 'I': [], 'R': []}
    history_states = [] # To store the state of each node at each step

    for step in range(num_steps):
        new_states = states.copy()
        
        infected_count = sum(1 for state in states.values() if state == 'I')
        susceptible_count = sum(1 for state in states.values() if state == 'S')
        recovered_count = sum(1 for state in states.values() if state == 'R')
        history['S'].append(susceptible_count)
        history['I'].append(infected_count)
        history['R'].append(recovered_count)
        history_states.append(states.copy()) # Store the current state of all nodes

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
    
    # Store final counts and states
    infected_count = sum(1 for state in states.values() if state == 'I')
    susceptible_count = sum(1 for state in states.values() if state == 'S')
    recovered_count = sum(1 for state in states.values() if state == 'R')
    history['S'].append(susceptible_count)
    history['I'].append(infected_count)
    history['R'].append(recovered_count)
    history_states.append(states.copy())

    print(f"SIR simulation finished after {num_steps} steps.")
    return history, history_states

def simulate_sis_model(graph, initial_infected_nodes, beta, gamma, num_steps):
    """Simulates the SIS model on a given graph."""
    states = {node: 'S' for node in graph.nodes()}
    for node in initial_infected_nodes:
        states[node] = 'I'

    history = {'S': [], 'I': []}
    history_states = [] # To store the state of each node at each step

    for step in range(num_steps):
        new_states = states.copy()
        
        infected_count = sum(1 for state in states.values() if state == 'I')
        susceptible_count = sum(1 for state in states.values() if state == 'S')
        history['S'].append(susceptible_count)
        history['I'].append(infected_count)
        history_states.append(states.copy()) # Store the current state of all nodes

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

    # Store final counts and states
    infected_count = sum(1 for state in states.values() if state == 'I')
    susceptible_count = sum(1 for state in states.values() if state == 'S')
    history['S'].append(susceptible_count)
    history['I'].append(infected_count)
    history_states.append(states.copy())

    print(f"SIS simulation finished after {num_steps} steps.")
    return history, history_states

def simulate_seir_model(graph, initial_infected_nodes, beta, epsilon, gamma, num_steps):
    """Simulates the SEIR model on a given graph."""
    states = {node: 'S' for node in graph.nodes()}
    for node in initial_infected_nodes:
        states[node] = 'E'  # Start as Exposed in SEIR model

    history = {'S': [], 'E': [], 'I': [], 'R': []}
    history_states = [] # To store the state of each node at each step

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
        history_states.append(states.copy()) # Store the current state of all nodes

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

    # Store final counts and states
    susceptible_count = sum(1 for state in states.values() if state == 'S')
    exposed_count = sum(1 for state in states.values() if state == 'E')
    infected_count = sum(1 for state in states.values() if state == 'I')
    recovered_count = sum(1 for state in states.values() if state == 'R')
    history['S'].append(susceptible_count)
    history['E'].append(exposed_count)
    history['I'].append(infected_count)
    history['R'].append(recovered_count)
    history_states.append(states.copy())

    print(f"SEIR simulation finished after {num_steps} steps.")
    return history, history_states

def simulate_sirs_model(graph, initial_infected_nodes, beta, gamma, zeta, num_steps):
    """Simulates the SIRS model on a given graph."""
    states = {node: 'S' for node in graph.nodes()}
    for node in initial_infected_nodes:
        states[node] = 'I'

    history = {'S': [], 'I': [], 'R': []}
    history_states = [] # To store the state of each node at each step

    for step in range(num_steps):
        new_states = states.copy()

        susceptible_count = sum(1 for state in states.values() if state == 'S')
        infected_count = sum(1 for state in states.values() if state == 'I')
        recovered_count = sum(1 for state in states.values() if state == 'R')
        history['S'].append(susceptible_count)
        history['I'].append(infected_count)
        history['R'].append(recovered_count)
        history_states.append(states.copy()) # Store the current state of all nodes

        for node in graph.nodes():
            if states[node] == 'S':
                # Try to get infected by infected neighbors
                for neighbor in graph.neighbors(node):
                    if states[neighbor] == 'I' and random.random() < beta:
                        new_states[node] = 'I'
                        break  # Only get infected once per step
            elif states[node] == 'I':
                # Try to recover
                if random.random() < gamma:
                    new_states[node] = 'R'
            elif states[node] == 'R':
                # Try to lose immunity and become susceptible again
                if random.random() < zeta:
                    new_states[node] = 'S'
        states = new_states

    # Store final counts and states
    susceptible_count = sum(1 for state in states.values() if state == 'S')
    infected_count = sum(1 for state in states.values() if state == 'I')
    recovered_count = sum(1 for state in states.values() if state == 'R')
    history['S'].append(susceptible_count)
    history['I'].append(infected_count)
    history['R'].append(recovered_count)
    history_states.append(states.copy())

    print(f"SIRS simulation finished after {num_steps} steps.")
    return history, history_states
