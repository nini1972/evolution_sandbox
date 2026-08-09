
import math
import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# --- Configuration Parameters ---
SIMULATION_DURATION_SECONDS = 3600  # 1 hour
TIME_STEP_SECONDS = 10              # Granularity of simulation updates

# Service Parameters
BASE_LATENCY_MS = 50
LATENCY_VARIANCE_MS = 20
BASE_ERROR_RATE = 0.001 # 0.1%
MAX_INSTANCES = 10
MIN_INSTANCES = 1
INSTANCE_CAPACITY_RPS = 100 # Requests per second an instance can handle

# SLOs (Service Level Objectives)
SLO_AVAILABILITY = 0.999 # 99.9% availability
SLO_LATENCY_P99_MS = 200 # 99% of requests should be faster than 200ms

# Error Budget Parameters
ERROR_BUDGET_WINDOW_SECONDS = 3600 * 24 * 7 # 7 days rolling window for error budget

# --- Simulation State ---
current_time = 0
service_instances = MIN_INSTANCES
total_requests_processed = 0
total_successful_requests = 0
latency_samples = deque(maxlen=1000) # Store recent latency samples for P99
hourly_latency_samples = deque() # For SLO calculation
hourly_error_counts = deque() # For SLO calculation
error_budget_burn_rate = 0.0

# History for plotting
time_history = []
request_rate_history = []
latency_p99_history = []
error_rate_history = []
instances_history = []
error_budget_remaining_history = []

# --- Functions ---

def generate_request_rate(current_time_in_seconds):
    """Simulates a fluctuating request rate over time."""
    # Simple sinusoidal pattern for daily fluctuation
    day_time = (current_time_in_seconds % (3600 * 24)) / (3600 * 24) # Normalize to 0-1 for a day
    peak_factor = (1 + 0.8 * (math.sin(day_time * 2 * math.pi) + 0.5)) # Peak and trough
    
    base_rate = 50 # Base requests per second
    return base_rate * peak_factor + random.uniform(-10, 10)

def process_requests(num_requests, current_instances):
    """Simulates processing of requests by the service."""
    global total_requests_processed, total_successful_requests

    successful_requests = 0
    errors = 0
    current_latencies = []

    for _ in range(int(num_requests)):
        total_requests_processed += 1
        
        # Simulate load impact on latency and error rate
        load_factor = num_requests / (current_instances * INSTANCE_CAPACITY_RPS)
        
        # Latency increases with load
        latency = BASE_LATENCY_MS + LATENCY_VARIANCE_MS * random.gauss(1, 0.2) * load_factor
        current_latencies.append(latency)
        latency_samples.append(latency)
        hourly_latency_samples.append(latency)

        # Error rate increases with load
        error_chance = BASE_ERROR_RATE * load_factor * 10 if load_factor > 1 else BASE_ERROR_RATE
        if random.random() < error_chance:
            errors += 1
        else:
            successful_requests += 1
            total_successful_requests += 1
            
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

def update_error_budget(latency_breach, availability_breach):
    """Simulates error budget consumption."""
    global error_budget_burn_rate

    # A simplified model: direct burn if SLO is breached
    if latency_breach or availability_breach:
        error_budget_burn_rate += 0.01 # Arbitrary burn rate
    else:
        error_budget_burn_rate = max(0, error_budget_burn_rate - 0.005) # Recover slowly

    # Cap the burn rate for visualization
    error_budget_burn_rate = min(1.0, error_budget_burn_rate)
    return 1.0 - error_budget_burn_rate # Represent as budget remaining

def scale_service(current_instances, current_request_rate, p99_latency, latency_breach):
    """Simple scaling logic based on load and latency."""
    new_instances = current_instances

    # Scale up if overloaded or high latency
    if current_request_rate > current_instances * INSTANCE_CAPACITY_RPS * 0.8 or latency_breach:
        new_instances = min(MAX_INSTANCES, current_instances + 1)
    # Scale down if underutilized
    elif current_request_rate < current_instances * INSTANCE_CAPACITY_RPS * 0.5 and current_instances > MIN_INSTANCES:
        new_instances = max(MIN_INSTANCES, current_instances - 1)
    
    return new_instances

# --- Simulation Loop ---
print("Starting Cloud-Native Service Reliability Simulation...")

while current_time < SIMULATION_DURATION_SECONDS:
    time_history.append(current_time / 3600) # Store time in hours

    # 1. Generate Request Rate
    requests_in_step = generate_request_rate(current_time) * TIME_STEP_SECONDS
    request_rate_history.append(requests_in_step / TIME_STEP_SECONDS) # Store RPS

    # 2. Process Requests
    successful, errors, latencies = process_requests(requests_in_step, service_instances)
    
    # Update hourly samples for SLO calculation
    hourly_error_counts.append(errors)
    # Remove old samples to maintain the hourly window
    while len(hourly_latency_samples) * TIME_STEP_SECONDS > 3600:
        hourly_latency_samples.popleft()
    while len(hourly_error_counts) * TIME_STEP_SECONDS > 3600:
        hourly_error_counts.popleft()

    # 3. Calculate SLIs and Check SLOs
    latency_breach, availability_breach, p99_latency, availability = calculate_slo_breach(list(hourly_latency_samples), list(hourly_error_counts))
    latency_p99_history.append(p99_latency)
    
    current_error_rate = errors / requests_in_step if requests_in_step > 0 else 0
    error_rate_history.append(current_error_rate)

    # 4. Update Error Budget
    error_budget_remaining = update_error_budget(latency_breach, availability_breach)
    error_budget_remaining_history.append(error_budget_remaining)

    # 5. Scale Service
    service_instances = scale_service(service_instances, requests_in_step / TIME_STEP_SECONDS, p99_latency, latency_breach)
    instances_history.append(service_instances)

    # Print status (optional, for debugging)
    # if current_time % (3600) == 0:
    #     print(f"Time: {current_time/3600:.1f}h, Req/s: {requests_in_step/TIME_STEP_SECONDS:.1f}, Instances: {service_instances}, "
    #           f"P99 Latency: {p99_latency:.1f}ms (SLO: {SLO_LATENCY_P99_MS}ms, Breach: {latency_breach}), "
    #           f"Availability: {availability:.4f} (SLO: {SLO_AVAILABILITY}, Breach: {availability_breach}), "
    #           f"Error Budget: {error_budget_remaining*100:.2f}%")

    current_time += TIME_STEP_SECONDS

print("Simulation finished. Generating plots...")

# --- Plotting Results ---
plt.style.use('seaborn-v0_8-darkgrid')
fig, axs = plt.subplots(5, 1, figsize=(14, 18), sharex=True)

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
axs[4].set_xlabel('Time (Hours)')
axs[4].legend()

plt.tight_layout()
plt.savefig('reliability_simulation_results.png')
print("Simulation results saved to reliability_simulation_results.png")

