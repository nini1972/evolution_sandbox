import math
import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

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

    def process_requests_local(num_requests, current_available_instances, current_time):
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
            # We