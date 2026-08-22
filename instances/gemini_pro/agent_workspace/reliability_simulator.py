
import math
import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# --- Configuration Parameters ---
SIMULATION_DURATION_SECONDS = 7 * 24 * 3600 # 7 days
TIME_STEP_SECONDS = 30 * 60              # Granularity of simulation updates

# Service Parameters
BASE_LATENCY_MS = 50
LATENCY_VARIANCE_MS = 20
BASE_ERROR_RATE = 0.001 # 0.1%
MAX_INSTANCES = 10

# Auto-Scaling Constants
AUTO_SCALE_UP_LATENCY_THRESHOLD = 180 # ms. If P99 latency exceeds this, scale up
AUTO_SCALE_DOWN_LATENCY_THRESHOLD = 100 # ms. If P99 latency is below this, scale down
AUTO_SCALE_UP_STEP = 2 # Number of instances to add when scaling up
AUTO_SCALE_DOWN_STEP = 1 # Number of instances to remove when scaling down
MIN_INSTANCES = 5
MAX_INSTANCES = 20
MIN_INSTANCES = 1
INSTANCE_CAPACITY_RPS = 100 # Requests per second an instance can handle

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

DATABASE_LATENCY_SPIKE_PROBABILITY = 0.0002 # Less frequent than network spikes
DATABASE_LATENCY_SPIKE_DURATION = 3600 / TIME_STEP_SECONDS # Lasts for 1 hour
DATABASE_LATENCY_SPIKE_MAGNITUDE = 300 # Additional latency from database # Additional latency in ms during a spike

# Game Day Parameters
GAME_DAY_INTERVAL_SECONDS = 7 * 24 * 3600 # Every 7 days
GAME_DAY_DURATION_SECONDS = 4 * 3600 # 4 hours
GAME_DAY_DETECTION_TIME_SECONDS = 0.5 * 3600 # 30 minutes to detect an issue
GAME_DAY_RECOVERY_MULTIPLIER = 2 # Error budget recovers and toil reduces twice as fast during Game Day

# --- Simulation State ---
current_time = 0
service_instances = MIN_INSTANCES
total_requests_processed = 0
total_successful_requests = 0
latency_samples = deque(maxlen=1000) # Store recent latency samples for P99
hourly_latency_samples = deque() # For SLO calculation
hourly_error_counts = deque() # For SLO calculation
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
last_chaos_injection_time = 0
game_day_active = False
game_day_duration_remaining = 0
last_game_day_time = 0

# History for plotting
time_history = []
request_rate_history = []
latency_p99_history = []
error_rate_history = []
instances_history = []
error_budget_remaining_history = []
toil_level_history = []
cumulative_cost_history = []

# --- Functions ---

def generate_request_rate(current_time_in_seconds):
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
    global last_random_walk_delta
    if 'last_random_walk_delta' not in globals():
        last_random_walk_delta = 0
    
    random_walk_step = random.uniform(-5, 5)
    last_random_walk_delta = max(-20, min(20, last_random_walk_delta + random_walk_step)) # Keep within bounds

    return (base_rate * spike_factor + last_random_walk_delta) + random.uniform(-10, 10)

def process_requests(num_requests, current_available_instances):
    """Simulates processing of requests by the service."""
    global total_requests_processed, total_successful_requests

    successful_requests = 0
    errors = 0
    current_latencies = []

    if current_available_instances == 0: # If no instances are available, all requests fail
        return 0, num_requests, []

    # Simulate load impact on latency and error rate
    load_factor = num_requests / (current_available_instances * INSTANCE_CAPACITY_RPS) if current_available_instances > 0 else 100 # High load if no instances
    
    # Calculate errors statistically
    error_chance = BASE_ERROR_RATE * load_factor * 10 if load_factor > 1 else BASE_ERROR_RATE
    errors = int(num_requests * error_chance)
    successful_requests = num_requests - errors
    
    total_requests_processed += num_requests
    total_successful_requests += successful_requests

    # Calculate representative latency for this time step
    # P99 latency is more relevant for SLOs, so we'll approximate it directly
    p99_latency_for_step = BASE_LATENCY_MS + LATENCY_VARIANCE_MS * 2.33 * load_factor # 2.33 for P99 of normal dist
    
    if network_latency_spike_active:
        p99_latency_for_step += NETWORK_LATENCY_SPIKE_MAGNITUDE
    
    # Append this representative latency multiple times to fill the deques for percentile calculation
    # The number of appends is arbitrary but should reflect the 'density' of requests
    # Let's append it a fixed number of times (e.g., 10) to represent the batch
    for _ in range(10): # Appending multiple times to contribute to percentile calculation
        latency_samples.append(p99_latency_for_step)
        hourly_latency_samples.append(p99_latency_for_step)
    
    # We no longer return a list of individual latencies, just a placeholder
    current_latencies = [p99_latency_for_step] # Return one representative latency
            
    return successful_requests, errors, current_latencies

def calculate_p_percentile(data, p):
    """Calculates the p-th percentile of a list of data."""
    if not data:
        return 0
    sorted_data = sorted(data)
    index = (len(sorted_data) - 1) * p / 100
    return sorted_data[int(index)]

def calculate_slo_breach(hourly_samples, hourly_errors):
    """Checks if SLOs are being breached."""
    # Latency SLO
    p99_latency = calculate_p_percentile(hourly_samples, 99)
    latency_breach = p99_latency > SLO_LATENCY_P99_MS

    # Availability SLO
    total_hourly_requests = len(hourly_samples) + sum(hourly_errors)
    if total_hourly_requests == 0:
        availability = 1.0
    else:
        availability = (total_hourly_requests - sum(hourly_errors)) / total_hourly_requests
    availability_breach = availability < SLO_AVAILABILITY
    
    return latency_breach, availability_breach, p99_latency, availability

def update_error_budget(latency_breach, availability_breach, p99_latency, current_availability, toil_level, postmortem_active):
    """Simulates error budget consumption and recovery based on SLO breaches."""
    global error_budget_burn_rate

    burn_factor = 0.0 # How much error budget we burn in this step

    # Latency breach: burn rate proportional to how much P99 exceeds SLO
    if latency_breach:
        latency_exceed_ratio = (p99_latency - SLO_LATENCY_P99_MS) / SLO_LATENCY_P99_MS
        burn_factor += 0.005 * latency_exceed_ratio # Base burn rate, scaled by severity

    # Availability breach: burn rate proportional to how much availability is below SLO
    if availability_breach:
        availability_drop_ratio = (SLO_AVAILABILITY - current_availability) / (1 - SLO_AVAILABILITY) # Normalize drop
        burn_factor += 0.01 * availability_drop_ratio # Base burn rate, scaled by severity

    error_budget_burn_rate += burn_factor

    # Recovery: if no breach, recover error budget. Recovery is faster with lower toil.
    # During postmortem and Game Day, recovery is even faster due to focused effort.
    recovery_multiplier = 1.0
    if postmortem_active:
        recovery_multiplier *= 2 # Double recovery speed during postmortem
    if game_day_active: # Game Day also provides focused effort
        recovery_multiplier *= GAME_DAY_RECOVERY_MULTIPLIER

    if not latency_breach and not availability_breach:
        recovery_factor = 0.002 * (1.0 - toil_level) * recovery_multiplier
        error_budget_burn_rate = max(0, error_budget_burn_rate - recovery_factor)

    # Cap the burn rate between 0 and 1
    error_budget_burn_rate = min(1.0, max(0, error_budget_burn_rate))
    return 1.0 - error_budget_burn_rate # Represent as budget remaining

def auto_scale_service(current_instances, p99_latency):
    """Advanced auto-scaling logic based on latency and request rate."""
    new_instances = current_instances

    # Scale up aggressively if P99 latency is above threshold
    if p99_latency > AUTO_SCALE_UP_LATENCY_THRESHOLD:
        new_instances = min(MAX_INSTANCES, current_instances + AUTO_SCALE_UP_STEP)
        print(f"Scaling UP due to high latency: {p99_latency:.1f}ms -> {new_instances} instances")
    # Scale down if P99 latency is well below threshold and not at min instances
    elif p99_latency < AUTO_SCALE_DOWN_LATENCY_THRESHOLD and current_instances > MIN_INSTANCES:
        new_instances = max(MIN_INSTANCES, current_instances - AUTO_SCALE_DOWN_STEP)
        print(f"Scaling DOWN due to low latency: {p99_latency:.1f}ms -> {new_instances} instances")

    return new_instances

def chaos_manager(current_time, service_instances_count):
    global failed_instances, last_chaos_injection_time, network_latency_spike_active, network_latency_spike_remaining, database_latency_spike_active, database_latency_spike_remaining

    # Recover failed instances
    failed_instances = [f for f in failed_instances if f['recovery_time'] > current_time]

    # Handle network latency spikes
    if network_latency_spike_active:
        network_latency_spike_remaining -= TIME_STEP_SECONDS
        if network_latency_spike_remaining <= 0:
            network_latency_spike_active = False
            print(f"--- Network Latency Spike Ended at {current_time/3600:.1f} hours. ---")

    # Handle network latency spikes
    if network_latency_spike_active:
        network_latency_spike_remaining -= TIME_STEP_SECONDS
        if network_latency_spike_remaining <= 0:
            network_latency_spike_active = False
            print(f"--- Network Latency Spike Ended at {current_time/3600:.1f} hours. ---")


    # Inject new chaos (instance failure or network spike)
    if current_time - last_chaos_injection_time >= CHAOS_INJECTION_INTERVAL_SECONDS:
        last_chaos_injection_time = current_time

        # Instance Failure Chaos
        if random.random() < CHAOS_INSTANCE_FAILURE_CHANCE: # Check if instance chaos should be injected
            available_for_failure = service_instances_count - len(failed_instances)
            if available_for_failure > MIN_INSTANCES: # Ensure we don't fail below MIN_INSTANCES
                active_instance_ids = set(range(service_instances_count))
                currently_failed_ids = {f['instance_id'] for f in failed_instances}
                eligible_for_failure = list(active_instance_ids - currently_failed_ids)

                if eligible_for_failure: # If there are instances that can be failed
                    instance_to_fail = random.choice(eligible_for_failure)
                    recovery_time = current_time + CHAOS_FAILURE_DURATION_SECONDS
                    failed_instances.append({'instance_id': instance_to_fail, 'recovery_time': recovery_time})
                    print(f"!!! CHAOS: Instance {instance_to_fail} failed at {current_time/3600:.1f}h, recovering at {recovery_time/3600:.1f}h !!!")
        
        # Network Latency Spike Chaos
        if not network_latency_spike_active and random.random() < NETWORK_LATENCY_SPIKE_PROBABILITY:
            network_latency_spike_active = True
            network_latency_spike_remaining = NETWORK_LATENCY_SPIKE_DURATION
            print(f"!!! CHAOS: Network Latency Spike Triggered at {current_time/3600:.1f} hours. !!!")

    return service_instances_count - len(failed_instances)

def game_day_manager(current_time):
    global game_day_active, game_day_duration_remaining, last_game_day_time, BASE_LATENCY_MS

    # End Game Day if duration is over
    if game_day_active and game_day_duration_remaining <= 0:
        game_day_active = False
        BASE_LATENCY_MS = 50 # Reset to normal
        print(f"--- Game Day Ended at {current_time/3600:.1f} hours. ---")

    # Start new Game Day
    if not game_day_active and (current_time - last_game_day_time) >= GAME_DAY_INTERVAL_SECONDS:
        game_day_active = True
        last_game_day_time = current_time
        game_day_duration_remaining = GAME_DAY_DURATION_SECONDS
        BASE_LATENCY_MS = 300 # Simulate a severe latency issue during Game Day
        print(f"!!! Game Day Started at {current_time/3600:.1f} hours. !!!")
    
    if game_day_active:
        game_day_duration_remaining -= TIME_STEP_SECONDS


# --- Simulation Loop ---
print("Starting Cloud-Native Service Reliability Simulation...")

# Timers for profiling
time_section_1 = 0 # Request Rate Generation
time_section_2 = 0 # Chaos Injection
time_section_3 = 0 # Game Day Management
time_section_4 = 0 # Request Processing
time_section_5 = 0 # Hourly Sample Updates
time_section_6 = 0 # SLI/SLO Calculation
time_section_7 = 0 # Error Budget Update
time_section_8 = 0 # Service Scaling
time_section_9 = 0 # Toil, Postmortem, Cost Update

while current_time < SIMULATION_DURATION_SECONDS:
    time_history.append(current_time / 3600) # Store time in hours

    start_section_time = time.perf_counter()
    # 1. Generate Request Rate
    requests_in_step = generate_request_rate(current_time) * TIME_STEP_SECONDS
    request_rate_history.append(requests_in_step / TIME_STEP_SECONDS) # Store RPS
    time_section_1 += (time.perf_counter() - start_section_time)

    start_section_time = time.perf_counter()
    # 2. Inject Chaos and Determine Available Instances
    available_instances = chaos_manager(current_time, service_instances)
    time_section_2 += (time.perf_counter() - start_section_time)

    start_section_time = time.perf_counter()
    # 3. Manage Game Days
    game_day_manager(current_time)
    time_section_3 += (time.perf_counter() - start_section_time)
    
    start_section_time = time.perf_counter()
    # 4. Process Requests
    successful, errors, latencies = process_requests(requests_in_step, available_instances)
    time_section_4 += (time.perf_counter() - start_section_time)
    
    start_section_time = time.perf_counter()
    # 5. Update hourly samples for SLO calculation
    hourly_error_counts.append(errors)
    # Remove old samples to maintain the hourly window
    while len(hourly_latency_samples) * TIME_STEP_SECONDS > 3600:
        hourly_latency_samples.popleft()
    while len(hourly_error_counts) * TIME_STEP_SECONDS > 3600:
        hourly_error_counts.popleft()
    time_section_5 += (time.perf_counter() - start_section_time)

    start_section_time = time.perf_counter()
    # 6. Calculate SLIs and Check SLOs
    latency_breach, availability_breach, p99_latency, availability = calculate_slo_breach(list(hourly_latency_samples), list(hourly_error_counts))
    latency_p99_history.append(p99_latency)
    
    current_error_rate = errors / requests_in_step if requests_in_step > 0 else 0
    error_rate_history.append(current_error_rate)
    time_section_6 += (time.perf_counter() - start_section_time)

    start_section_time = time.perf_counter()
    # 7. Update Error Budget
    error_budget_remaining = update_error_budget(latency_breach, availability_breach, p99_latency, availability, toil_level, postmortem_active)
    error_budget_remaining_history.append(error_budget_remaining)
    time_section_7 += (time.perf_counter() - start_section_time)

    start_section_time = time.perf_counter()
    # 8. Scale Service (operates on total provisioned instances)
    service_instances = auto_scale_service(service_instances, p99_latency)
    instances_history.append(service_instances)
    time_section_8 += (time.perf_counter() - start_section_time)

    start_section_time = time.perf_counter()
    # 9. Update Toil Level and Postmortem Logic, Cost Update
    # Toil increases over time, but decreases if error budget is healthy (SREs have time for automation)
    # And increases faster if error budget is low (firefighting)
    toil_reduction_multiplier = 1.0
    if postmortem_active: # During postmortem, toil reduces faster
        toil_reduction_multiplier *= 2
    if game_day_active: # During game day, toil also reduces faster due to focused effort
        toil_reduction_multiplier *= GAME_DAY_RECOVERY_MULTIPLIER

    if postmortem_active: # During postmortem, toil reduces faster
        toil_level = max(0, toil_level - (0.01 * toil_reduction_multiplier))
    elif error_budget_remaining > 0.8: # Healthy error budget, SREs can reduce toil
        toil_level = max(0, toil_level - (0.005 * toil_reduction_multiplier))
    elif error_budget_remaining < 0.2: # Low error budget, SREs are firefighting, toil accumulates faster
        toil_level = min(1.0, toil_level + 0.02)
    else: # Normal accumulation
        toil_level = min(1.0, toil_level + 0.001)
    toil_level_history.append(toil_level)

    # Postmortem Logic
    if not postmortem_active and error_budget_remaining < 0.2: # Trigger postmortem if budget is low
        postmortem_active = True
        postmortem_duration_remaining = 3600 / TIME_STEP_SECONDS # Postmortem lasts for 1 hour (in time steps)
        print(f"!!! Postmortem Triggered at {current_time/3600:.1f} hours. !!!")

    if postmortem_active:
        postmortem_duration_remaining -= 1
        if postmortem_duration_remaining <= 0:
            postmortem_active = False
            print(f"--- Postmortem Ended at {current_time/3600:.1f} hours. ---")

    # Update Cost (based on total provisioned instances)
    cost_in_step = service_instances * COST_PER_INSTANCE_PER_HOUR * (TIME_STEP_SECONDS / 3600)
    cumulative_cost += cost_in_step
    cumulative_cost_history.append(cumulative_cost)
    time_section_9 += (time.perf_counter() - start_section_time)

    current_time += TIME_STEP_SECONDS # Move simulation forward

    # Print status (optional, for debugging)
    # if current_time % (3600) == 0:
    #     print(f"Time: {current_time/3600:.1f}h, Req/s: {requests_in_step/TIME_STEP_SECONDS:.1f}, Instances: {service_instances}, "
    #           f"P99 Latency: {p99_latency:.1f}ms (SLO: {SLO_LATENCY_P99_MS}ms, Breach: {latency_breach}), "
    #           f"Availability: {availability:.4f} (SLO: {SLO_AVAILABILITY}, Breach: {availability_breach}), "
    #           f"Error Budget: {error_budget_remaining*100:.2f}%,"
    #           f"Toil Level: {toil_level*100:.2f}%,"
    #           f"Postmortem Active: {postmortem_active}")


print("Simulation finished. Generating plots...")
print(f"Profiling Results:")
print(f"  Request Rate Generation: {time_section_1:.4f} seconds")
print(f"  Chaos Injection: {time_section_2:.4f} seconds")
print(f"  Game Day Management: {time_section_3:.4f} seconds")
print(f"  Request Processing: {time_section_4:.4f} seconds")
print(f"  Hourly Sample Updates: {time_section_5:.4f} seconds")
print(f"  SLI/SLO Calculation: {time_section_6:.4f} seconds")
print(f"  Error Budget Update: {time_section_7:.4f} seconds")
print(f"  Service Scaling: {time_section_8:.4f} seconds")
print(f"  Toil, Postmortem, Cost Update: {time_section_9:.4f} seconds")

# --- Plotting Results ---
plt.style.use('seaborn-v0_8-darkgrid')
fig, axs = plt.subplots(7, 1, figsize=(14, 24), sharex=True) # Increased to 7 subplots

# 1. Request Rate
axs[0].plot(time_history, request_rate_history, label='Request Rate (RPS)', color='skyblue')
axs[0].set_ylabel('Requests/Sec')
axs[0].set_title('Cloud-Native Service Reliability & Scaling Simulation')
axs[0].legend()

# 2. P99 Latency
axs[1].plot(time_history, latency_p99_history, label='P99 Latency (ms)', color='salmon')
axs[1].axhline(y=SLO_LATENCY_P99_MS, color='red', linestyle='--', label=f'Latency SLO ({SLO_LATENCY_P99_MS}ms)')
axs[1].set_ylabel('Latency (ms)')
axs[1].legend()

# 3. Error Rate
axs[2].plot(time_history, error_rate_history, label='Error Rate', color='orange')
axs[2].axhline(y=1-SLO_AVAILABILITY, color='red', linestyle='--', label=f'Availability SLO Error ({1-SLO_AVAILABILITY:.4f})')
axs[2].set_ylabel('Error Rate')
axs[2].legend()

# 4. Service Instances
axs[3].plot(time_history, instances_history, label='Service Instances', color='lightgreen', drawstyle='steps-post')
axs[3].set_ylabel('Instances')
axs[3].set_yticks(range(MIN_INSTANCES, MAX_INSTANCES + 1))
axs[3].legend()

# 5. Error Budget Remaining
axs[4].plot(time_history, [eb * 100 for eb in error_budget_remaining_history], label='Error Budget Remaining (%)', color='purple')
axs[4].axhline(y=0, color='red', linestyle='-', linewidth=0.8)
axs[4].set_ylabel('Error Budget (%)')
axs[4].legend()

# 6. Toil Level
axs[5].plot(time_history, [tl * 100 for tl in toil_level_history], label='Toil Level (%)', color='gray')
axs[5].set_ylabel('Toil Level (%)')
axs[5].legend()

# 7. Cumulative Cost
axs[6].plot(time_history, cumulative_cost_history, label='Cumulative Cost ($)', color='darkgreen')
axs[6].set_ylabel('Cost ($)')
axs[6].set_xlabel('Time (Hours)')
axs[6].legend()

plt.tight_layout()
plt.savefig('reliability_simulation_results.png')
print("Simulation results saved to reliability_simulation_results.png")

