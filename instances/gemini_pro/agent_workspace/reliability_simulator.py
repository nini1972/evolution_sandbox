import math
import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

def calculate_p_percentile(data, p):
    """Calculates the p-th percentile of a list of data."""
    if not data:
        return 0
    data.sort()
    index = (len(data) - 1) * p / 100
    if index.is_integer():
        return data[int(index)]
    lower_bound = data[int(math.floor(index))]
    upper_bound = data[int(math.ceil(index))]
    return lower_bound + (upper_bound - lower_bound) * (index - math.floor(index))

# --- Configuration Parameters ---
SIMULATION_DURATION_SECONDS = 7 * 24 * 3600 # 7 days
TIME_STEP_SECONDS = 300              # Granularity of simulation updates

# Service Parameters
BASE_LATENCY_MS = 50
LATENCY_VARIANCE_MS = 20
BASE_ERROR_RATE = 0.0005 # 0.05%


# Auto-Scaling Constants
AUTO_SCALE_UP_LATENCY_THRESHOLD = 100 # ms. If P99 latency exceeds this, scale up
AUTO_SCALE_UP_LOAD_FACTOR_THRESHOLD = 0.8 # If effective load factor exceeds this, scale up
AUTO_SCALE_DOWN_LATENCY_THRESHOLD = 120 # ms. If P99 latency is below this, scale down
AUTO_SCALE_UP_STEP = 5 # Number of instances to add when scaling up
AUTO_SCALE_DOWN_STEP = 1 # Number of instances to remove when scaling down
AUTOSCALING_COOLDOWN_SECONDS = 300 # 5 minutes cooldown between scaling actions

INSTANCE_CAPACITY_RPS = 150 # Requests per second an instance can handle

# SLOs (Service Level Objectives)
SLO_AVAILABILITY = 0.999 # 99.9% availability
SLO_LATENCY_P99_MS = 200 # 99% of requests should be faster than 200ms

# Error Budget Parameters
ERROR_BUDGET_WINDOW_SECONDS = 3600 * 24 * 7 # 7 days rolling window for error budget

# Cost Parameters
COST_PER_INSTANCE_PER_HOUR = 0.5 # $0.5 per instance per hour

# Chaos Engineering Parameters
CHAOS_INJECTION_INTERVAL_SECONDS = 600 # Attempt chaos every 10 minutes
CHAOS_INSTANCE_FAILURE_CHANCE = 0.3 # 30% chance of an instance failing during an interval
CHAOS_FAILURE_DURATION_SECONDS = 300 # An instance remains failed for 5 minutes
NETWORK_LATENCY_SPIKE_PROBABILITY = 0.0005 # Probability of a network latency spike
NETWORK_LATENCY_SPIKE_DURATION = 1800 / TIME_STEP_SECONDS # Latency spike lasts 30 minutes
NETWORK_LATENCY_SPIKE_MAGNITUDE = 200

DATABASE_LATENCY_SPIKE_PROBABILITY = 0.001 # Increased probability
DATABASE_LATENCY_SPIKE_DURATION = 3600 / TIME_STEP_SECONDS # Lasts for 1 hour
DATABASE_LATENCY_SPIKE_MAGNITUDE = 300 # Additional latency from database # Additional latency in ms during a spike

DEPENDENCY_FAILURE_PROBABILITY = 0.0005 # Probability of a dependency failure
DEPENDENCY_FAILURE_DURATION_SECONDS = 600 # Dependency failure lasts 10 minutes
DEPENDENCY_FAILURE_ERROR_RATE_INCREASE = 0.05 # 5% increase in error rate during dependency failure

# Circuit Breaker Parameters (NEW)
CIRCUIT_BREAKER_TRIP_THRESHOLD = 0.5 # If error rate exceeds 50% in a window, trip
CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS = 300 # After 5 minutes, try to close circuit
CIRCUIT_BREAKER_SAMPLING_WINDOW_SIZE = 10 # Number of recent samples to consider


# Game Day Parameters
GAME_DAY_INTERVAL_SECONDS = 7 * 24 * 3600 # Every 7 days
GAME_DAY_DURATION_SECONDS = 4 * 3600 # 4 hours
GAME_DAY_DETECTION_TIME_SECONDS = 0.5 * 3600 # 30 minutes to detect an issue
GAME_DAY_RECOVERY_MULTIPLIER = 2 # Error budget recovers and toil reduces twice as fast during Game Day
GAME_DAY_TRAFFIC_RAMP_UP_DURATION_HOURS = 4 # 4 hours to reach peak traffic
GAME_DAY_TRAFFIC_PEAK_DURATION_HOURS = 8 # 8 hours at peak traffic
GAME_DAY_TRAFFIC_RAMP_DOWN_DURATION_HOURS = 4 # 4 hours to return to normal traffic
GAME_DAY_TRAFFIC_PEAK_MULTIPLIER = 4 # Max request rate multiplier during game day peak
GAME_DAY_REQUEST_RATE_MULTIPLIER = 2.5 # Request rate multiplies by 2.5 during game day to simulate spike

# Circuit Breaker State Definitions (moved out of run_simulation to be global constants)
CIRCUIT_BREAKER_STATE_CLOSED = 0
CIRCUIT_BREAKER_STATE_OPEN = 1
CIRCUIT_BREAKER_STATE_HALF_OPEN = 2


# --- Functions ---

def run_simulation(min_instances_param, max_instances_param, simulation_id="reliability_simulation"):
    # --- Simulation State ---
    current_time = 0
    service_instances = min_instances_param
    total_requests_processed = 0
    total_successful_requests = 0
    latency_samples = deque(maxlen=1000) # Store recent latency samples for P99
    hourly_latency_samples = deque() # For SLO calculation
    hourly_error_counts = deque() # For SLO calculation
    hourly_request_counts = deque() # For SLO calculation (NEW)
    error_budget_burn_rate = 0.0
    error_budget_remaining = 1.0 # Initialize error budget
    toil_level = 0.0 # Represents accumulated toil, 0.0 to 1.0
    postmortem_active = False
    postmortem_duration_remaining = 0 # In time steps
    cumulative_cost = 0.0
    failed_instances = [] # List of {'instance_id': X, 'recovery_time': Y}
    network_latency_spike_active = False
    network_latency_spike_remaining = 0
    database_latency_spike_active = False # NEW
    database_latency_spike_remaining = 0 # NEW
    dependency_failure_active = False
    dependency_failure_remaining = 0
    last_chaos_injection_time = 0
    game_day_active = False
    game_day_duration_remaining = 0
    last_game_day_time = 0
    game_day_start_time = 0
    last_scaling_action_time = 0 # Track last scaling action to implement cooldown

    circuit_breaker_state = CIRCUIT_BREAKER_STATE_CLOSED
    circuit_breaker_open_time = 0
    circuit_breaker_recent_errors = deque(maxlen=CIRCUIT_BREAKER_SAMPLING_WINDOW_SIZE)

    # History for plotting
    time_history = []
    request_rate_history = []
    latency_p99_history = []
    error_rate_history = []
    instances_history = []
    error_budget_remaining_history = []
    toil_level_history = []
    cumulative_cost_history = []

    # Local variable for random walk delta within this simulation run
    last_random_walk_delta = 0

    def calculate_slo_breach_local(latency_samples_arg, total_errors_arg):
        latency_breach = False
        if latency_samples_arg:
            p99_latency = calculate_p_percentile(list(latency_samples_arg), 99)
            if p99_latency > SLO_LATENCY_P99_MS:
                latency_breach = True

        availability_breach = False
        if total_errors_arg / TIME_STEP_SECONDS > (1 - SLO_AVAILABILITY):
            availability_breach = True

        return latency_breach, availability_breach


    def update_error_budget_local(total_errors, total_requests, current_burn_rate, game_day_active):
        # Simulate error budget burn. More errors mean faster burn.
        # If no requests, no burn.
        if total_requests == 0:
            return 0.0

        # Current error rate
        current_error_rate = total_errors / total_requests

        # Target error rate based on SLO
        target_error_rate = 1 - SLO_AVAILABILITY

        # If current error rate exceeds target, burn budget
        if current_error_rate > target_error_rate:
            # Calculate how much current error rate exceeds the target
            excess_error_rate = current_error_rate - target_error_rate
            # The burn rate is proportional to the excess error rate
            burn_rate = (excess_error_rate / target_error_rate) # Normalized burn rate
        else:
            burn_rate = 0.0 # No burn if within SLO

        # During Game Day, error budget recovers faster (or burns slower, depending on implementation)
        if game_day_active:
            # Example: Halve the burn rate during game day if within SLO, or a faster recovery
            burn_rate *= (1 / GAME_DAY_RECOVERY_MULTIPLIER) # Reduce effective burn

        return burn_rate

    def update_toil_local(latency_breach, availability_breach, error_budget_burn_rate, game_day_active):
        nonlocal toil_level
        # Toil increases when SLOs are breached or error budget is burning fast
        # Toil decreases over time or with proactive actions (like game days)

        toil_increase = 0
        if latency_breach: # Each breach adds a fixed amount of toil
            toil_increase += 0.01
        if availability_breach:
            toil_increase += 0.02 # Availability breaches are more severe

        # High error budget burn also increases toil
        toil_increase += error_budget_burn_rate * 0.05 # Proportional to how fast budget is burning

        toil_level = min(1.0, toil_level + toil_increase) # Cap toil at 100%

        # Toil naturally decays over time if no issues
        toil_level *= 0.99 # 1% decay per time step

        # Game days can help reduce toil faster
        if game_day_active:
            toil_level = max(0, toil_level - (0.01 * GAME_DAY_RECOVERY_MULTIPLIER)) # Faster toil reduction

        return toil_level

    def generate_request_rate_local(current_time_in_seconds):
        nonlocal last_random_walk_delta, game_day_active, game_day_start_time
        """Simulates a fluctuating request rate over time."""
        # More complex load pattern with spikes and random walk
        day_time = (current_time_in_seconds % (3600 * 24)) / (3600 * 24)  # Normalize to 0-1 for a day
        
        # Base sinusoidal pattern
        base_rate = 50 + 40 * math.sin(day_time * 2 * math.pi - math.pi/2) # Peaks at midday, troughs at midnight

        # Introduce occasional spikes
        spike_factor = 1.0
        if random.random() < 0.05: # 5% chance of a spike every time step
            spike_factor = 1.0 + random.uniform(0.5, 2.0) # Increase load by 50% to 200%

        # Add some random walk for variability
        
        random_walk_step = random.uniform(-5, 5)
        last_random_walk_delta = max(-20, min(20, last_random_walk_delta + random_walk_step)) # Keep within bounds

        rate = (base_rate * spike_factor + last_random_walk_delta) + random.uniform(-10, 10)

        # During Game Day, apply a dynamic request rate multiplier based on a ramp-up, peak, and ramp-down pattern
        if game_day_active and game_day_start_time is not None:
            time_since_game_day_start = current_time_in_seconds - game_day_start_time
            game_day_total_duration_seconds = (GAME_DAY_TRAFFIC_RAMP_UP_DURATION_HOURS + GAME_DAY_TRAFFIC_PEAK_DURATION_HOURS + GAME_DAY_TRAFFIC_RAMP_DOWN_DURATION_HOURS) * 3600

            if time_since_game_day_start <= GAME_DAY_TRAFFIC_RAMP_UP_DURATION_HOURS * 3600:
                # Ramp-up phase
                multiplier = 1 + (GAME_DAY_TRAFFIC_PEAK_MULTIPLIER - 1) * (time_since_game_day_start / (GAME_DAY_TRAFFIC_RAMP_UP_DURATION_HOURS * 3600))
            elif time_since_game_day_start <= (GAME_DAY_TRAFFIC_RAMP_UP_DURATION_HOURS + GAME_DAY_TRAFFIC_PEAK_DURATION_HOURS) * 3600:
                # Peak phase
                multiplier = GAME_DAY_TRAFFIC_PEAK_MULTIPLIER
            elif time_since_game_day_start <= game_day_total_duration_seconds:
                # Ramp-down phase
                time_in_ramp_down = time_since_game_day_start - (GAME_DAY_TRAFFIC_RAMP_UP_DURATION_HOURS + GAME_DAY_TRAFFIC_PEAK_DURATION_HOURS) * 3600
                multiplier = 1 + (GAME_DAY_TRAFFIC_PEAK_MULTIPLIER - 1) * (1 - (time_in_ramp_down / (GAME_DAY_TRAFFIC_RAMP_DOWN_DURATION_HOURS * 3600)))
            else:
                # After ramp-down, back to normal
                multiplier = 1
            rate *= multiplier

        return rate

    def process_requests_local(num_requests, current_available_instances, current_time_step):
        nonlocal total_requests_processed, total_successful_requests, circuit_breaker_state, circuit_breaker_open_time
        nonlocal latency_samples, hourly_latency_samples, circuit_breaker_recent_errors, network_latency_spike_active
        nonlocal database_latency_spike_active, dependency_failure_active
        """Simulates processing of requests by the service."""
        
        successful_requests = 0
        errors = 0
        current_latencies = []

        if current_available_instances == 0: # If no instances are available, all requests fail
            return 0, num_requests, []

        # If circuit breaker is open, all requests fail immediately
        if circuit_breaker_state == CIRCUIT_BREAKER_STATE_OPEN:
            for _ in range(int(num_requests)):
                circuit_breaker_recent_errors.append(1) # Record as error
            return 0, num_requests, []
        
        # Simulate load impact on latency and error rate
        current_rps = num_requests / TIME_STEP_SECONDS
        total_capacity_rps = current_available_instances * INSTANCE_CAPACITY_RPS
        
        # Corrected load_factor calculation for error chance
        # This load_factor represents the *effective* load on the system at this moment
        effective_load_factor = current_rps / total_capacity_rps if total_capacity_rps > 0 else 100 # High load if no instances
        
        # Calculate errors statistically
        error_chance = BASE_ERROR_RATE * (1 + (effective_load_factor - 1) * 5) if effective_load_factor > 1 else BASE_ERROR_RATE

        if dependency_failure_active:
            error_chance += DEPENDENCY_FAILURE_ERROR_RATE_INCREASE

        # If circuit breaker is half-open, allow one request to pass through
        test_request_success = True
        if circuit_breaker_state == CIRCUIT_BREAKER_STATE_HALF_OPEN:
            # For this simplified model, we'll just consider the recent hourly samples for the current "hour"
            # In a real system, you'd have more sophisticated time-windowing logic

            # If it's a new hour, clear previous hourly data and start fresh
            if current_time_seconds % 3600 == 0 and step != 0: # Only if it's a full hour and not the very first step
                hourly_latency_samples.clear()
                hourly_error_counts.clear()
                hourly_request_counts.clear()
            
            # Add current step data to hourly deques
            hourly_latency_samples.extend(current_latencies) # Assuming current_latencies is a list of latencies for this step
            hourly_error_counts.append(erred_req)
            hourly_request_counts.append(num_requests_in_step)

            current_hourly_total_requests = sum(hourly_request_counts)
            current_hourly_total_errors = sum(hourly_error_counts)

            latency_breach, availability_breach = calculate_slo_breach_local(list(hourly_latency_samples), current_hourly_total_errors)
            
            # Update error budget burn rate
            burn_rate = update_error_budget_local(current_hourly_total_errors, current_hourly_total_requests, error_budget_burn_rate, game_day_active)
            error_budget_remaining = max(0, error_budget_remaining - (burn_rate * TIME_STEP_SECONDS / ERROR_BUDGET_WINDOW_SECONDS))

            # Update toil
            toil_level = update_toil_local(latency_breach, availability_breach, burn_rate, game_day_active)

            # If error budget is completely burned and game day is not active, trigger postmortem
            if error_budget_remaining <= 0 and not postmortem_active and not game_day_active:
                postmortem_active = True
                postmortem_duration_remaining = GAME_DAY_DETECTION_TIME_SECONDS // TIME_STEP_SECONDS # Simulate time to detect and start postmortem
                print(f"!!! Error Budget Burned Out at {current_time_seconds/3600:.1f} hours. Postmortem initiated. !!!")
        
        # Postmortem state - reduce toil and recover error budget faster
        if postmortem_active:
            postmortem_duration_remaining -= 1
            if postmortem_duration_remaining <= 0:
                postmortem_active = False
                print(f"--- Postmortem concluded at {current_time_seconds/3600:.1f} hours. ---")
            
            # Simulate faster recovery during postmortem
            toil_level = max(0, toil_level - (0.005 * GAME_DAY_RECOVERY_MULTIPLIER)) # Faster toil reduction
            error_budget_remaining = min(1.0, error_budget_remaining + (0.01 * GAME_DAY_RECOVERY_MULTIPLIER * TIME_STEP_SECONDS / ERROR_BUDGET_WINDOW_SECONDS)) # Faster budget recovery

        # --- Data Collection for History ---
        time_history.append(current_time_seconds / 3600) # In hours
        request_rate_history.append(current_request_rate_rps)
        latency_p99_history.append(p99_latency_for_autoscaling) # Using the one calculated for autoscaling
        error_rate_history.append(erred_req / num_requests_in_step if num_requests_in_step > 0 else 0)
        instances_history.append(service_instances)
        error_budget_remaining_history.append(error_budget_remaining * 100) # As a percentage
        toil_level_history.append(toil_level * 100) # As a percentage

        # Calculate cumulative cost
        cumulative_cost += service_instances * COST_PER_INSTANCE_PER_HOUR * (TIME_STEP_SECONDS / 3600)
        cumulative_cost_history.append(cumulative_cost)

        if step % 100 == 0:
            print(f"Time: {current_time_seconds/3600:.2f}h, Req/s: {current_request_rate_rps:.2f}, Instances: {service_instances}, P99 Lat: {p99_latency_for_autoscaling:.2f}ms, Err%: {error_rate_history[-1]*100:.2f}%, EB: {error_budget_remaining_history[-1]:.2f}%, Toil: {toil_level_history[-1]:.2f}%")

    print(f"Simulation '{simulation_id}' finished.")

    # --- Plotting Results ---
    fig, axs = plt.subplots(7, 1, figsize=(15, 25), sharex=True)
    fig.suptitle(f'Reliability Simulation Results (ID: {simulation_id})', fontsize=16)

    # Request Rate
    axs[0].plot(time_history, request_rate_history, label='Request Rate (RPS)', color='blue')
    axs[0].set_ylabel('Requests/sec')
    axs[0].legend()
    axs[0].grid(True)

    # P99 Latency
    axs[1].plot(time_history, latency_p99_history, label='P99 Latency (ms)', color='red')
    axs[1].axhline(y=SLO_LATENCY_P99_MS, color='red', linestyle='--', label=f'Latency SLO ({SLO_LATENCY_P99_MS}ms)')
    axs[1].axhline(y=AUTO_SCALE_UP_LATENCY_THRESHOLD, color='orange', linestyle=':', label=f'Autoscale Up ({AUTO_SCALE_UP_LATENCY_THRESHOLD}ms)')
    axs[1].set_ylabel('Latency (ms)')
    axs[1].legend()
    axs[1].grid(True)

    # Error Rate
    axs[2].plot(time_history, error_rate_history, label='Error Rate', color='green')
    axs[2].axhline(y=(1-SLO_AVAILABILITY), color='green', linestyle='--', label=f'Availability SLO ({(1-SLO_AVAILABILITY)*100:.3f}%)')
    axs[2].set_ylabel('Error Rate')
    axs[2].set_ylim(bottom=0)
    axs[2].legend()
    axs[2].grid(True)

    # Service Instances
    axs[3].plot(time_history, instances_history, label='Service Instances', color='purple')
    axs[3].set_ylabel('Instances')
    axs[3].legend()
    axs[3].grid(True)

    # Error Budget
    axs[4].plot(time_history, error_budget_remaining_history, label='Error Budget Remaining (%)', color='brown')
    axs[4].axhline(y=0, color='red', linestyle='--', label='Error Budget Exhausted')
    axs[4].set_ylabel('Error Budget (%)')
    axs[4].set_ylim(0, 105)
    axs[4].legend()
    axs[4].grid(True)

    # Toil Level
    axs[5].plot(time_history, toil_level_history, label='Toil Level (%)', color='gray')
    axs[5].set_ylabel('Toil Level (%)')
    axs[5].set_ylim(0, 105)
    axs[5].legend()
    axs[5].grid(True)

    # Cumulative Cost
    axs[6].plot(time_history, cumulative_cost_history, label='Cumulative Cost ($)', color='black')
    axs[6].set_xlabel('Time (hours)')
    axs[6].set_ylabel('Cost ($)')
    axs[6].legend()
    axs[6].grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plot_filename = f'reliability_simulation_results_{simulation_id}.png'
    plt.savefig(plot_filename)
    print(f"Plot saved as {plot_filename}")
    plt.close(fig) # Close the figure to free up memory

    return {
        "simulation_id": simulation_id,
        "total_requests": total_requests_processed,
        "successful_requests": total_successful_requests,
        "final_error_rate": (total_requests_processed - total_successful_requests) / total_requests_processed if total_requests_processed > 0 else 0,
        "final_p99_latency": calculate_p_percentile(list(latency_samples), 99),
        "final_error_budget_remaining": error_budget_remaining,
        "final_toil_level": toil_level,
        "final_cumulative_cost": cumulative_cost
    }

if __name__ == "__main__":
    # Ensure matplotlib is not trying to use an interactive backend
    plt.switch_backend('Agg')

    # Example simulation run
    print("Running simulation with default parameters...")
    results = run_simulation(min_instances_param=5, max_instances_param=20, simulation_id="default_run")
    print("\nSimulation Results:")
    for key, value in results.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

    # You can add more simulation runs with different parameters here
    # print("\nRunning simulation with higher min_instances...")
    # results_high_min = run_simulation(min_instances_param=10, max_instances_param=20, simulation_id="high_min_instances")
    # print("\nSimulation Results (High Min Instances):")
    # for key, value in results_high_min.items():
    #     if isinstance(value, float):
    #         print(f"{key}: {value:.4f}")
    #     else:
    #         print(f"{key}: {value}")\