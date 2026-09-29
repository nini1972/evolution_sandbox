import random
import copy

def run_simulation(simulation_id, initial_state, total_simulation_time, time_step):
    simulation_state = copy.deepcopy(initial_state)
    simulation_history = {}

    current_time = 0
    # MARKER_START
    # This is where the simulation loop will go.
    # It will be replaced by the new simulation logic.
    print(f"Simulation \'{simulation_id}\' finished.")
    # MARKER_END

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
