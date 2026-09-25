import re

file_path = "reliability_simulator.py"

old_code_block_start_marker = "    # Simulation loop"
old_code_block_end_marker = "    return {"

new_code_block = '''    # Simulation loop
    num_steps = SIMULATION_DURATION_SECONDS // TIME_STEP_SECONDS
    for step in range(num_steps):
        current_time_seconds = step * TIME_STEP_SECONDS

        # --- Game Day Logic ---
        if not game_day_active and (current_time_seconds - last_game_day_time) >= GAME_DAY_INTERVAL_SECONDS:
            game_day_active = True
            game_day_duration_remaining = GAME_DAY_DURATION_SECONDS // TIME_STEP_SECONDS
            game_day_start_time = current_time_seconds
            print(f"!!! Game Day initiated at {current_time_seconds/3600:.1f} hours. !!!")

        if game_day_active:
            game_day_duration_remaining -= 1
            if game_day_duration_remaining <= 0:
                game_day_active = False
                last_game_day_time = current_time_seconds
                print(f"--- Game Day concluded at {current_time_seconds/3600:.1f} hours. ---")

        # --- Chaos Engineering --- (adjusted to use current_time_seconds)
        if (current_time_seconds - last_chaos_injection_time) >= CHAOS_INJECTION_INTERVAL_SECONDS:
            last_chaos_injection_time = current_time_seconds
            if random.random() < CHAOS_INSTANCE_FAILURE_CHANCE and service_instances > min_instances_param:
                instance_to_fail = random.randint(0, service_instances - 1)
                failed_instances.append({'instance_id': instance_to_fail, 'recovery_time': current_time_seconds + CHAOS_FAILURE_DURATION_SECONDS})
                print(f"Chaos: Instance {instance_to_fail} failed at {current_time_seconds/3600:.1f} hours.")
        
        # Check for instance recovery
        for f_instance in list(failed_instances):
            if current_time_seconds >= f_instance['recovery_time']:
                failed_instances.remove(f_instance)
                print(f"Chaos: Instance {f_instance['instance_id']} recovered at {current_time_seconds/3600:.1f} hours.")

        # Network latency spike
        if not network_latency_spike_active and random.random() < NETWORK_LATENCY_SPIKE_PROBABILITY:
            network_latency_spike_active = True
            network_latency_spike_remaining = NETWORK_LATENCY_SPIKE_DURATION
            print(f"Chaos: Network latency spike injected at {current_time_seconds/3600:.1f} hours.")
        if network_latency_spike_active:
            network_latency_spike_remaining -= 1
            if network_latency_spike_remaining <= 0:
                network_latency_spike_active = False
                print(f"Chaos: Network latency spike subsided at {current_time_seconds/3600:.1f} hours.")

        # Database latency spike
        if not database_latency_spike_active and random.random() < DATABASE_LATENCY_SPIKE_PROBABILITY:
            database_latency_spike_active = True
            database_latency_spike_remaining = DATABASE_LATENCY_SPIKE_DURATION
            print(f"Chaos: Database latency spike injected at {current_time_seconds/3600:.1f} hours.")
        if database_latency_spike_active:
            database_latency_spike_remaining -= 1
            if database_latency_spike_remaining <= 0:
                database_latency_spike_active = False
                print(f"Chaos: Database latency spike subsided at {current_time_seconds/3600:.1f} hours.")

        # Dependency failure
        if not dependency_failure_active and random.random() < DEPENDENCY_FAILURE_PROBABILITY:
            dependency_failure_active = True
            dependency_failure_remaining = DEPENDENCY_FAILURE_DURATION_SECONDS // TIME_STEP_SECONDS
            print(f"Chaos: Dependency failure injected at {current_time_seconds/3600:.1f} hours.")
        if dependency_failure_active:
            dependency_failure_remaining -= 1
            if dependency_failure_remaining <= 0:
                dependency_failure_active = False
                print(f"Chaos: Dependency failure recovered at {current_time_seconds/3600:.1f} hours.")

        # Calculate currently available instances
        current_available_instances = service_instances - len(failed_instances)
        current_available_instances = max(0, current_available_instances) # Ensure not negative

        # Generate request rate
        current_request_rate_rps = generate_request_rate_local(current_time_seconds)
        num_requests_in_step = current_request_rate_rps * TIME_STEP_SECONDS

        # Process requests
        successful_requests_in_step, erred_req_in_step, latencies_in_step = process_requests_local(num_requests_in_step, current_available_instances, step)

        # Calculate P99 latency for autoscaling and plotting
        p99_latency_for_autoscaling = calculate_p_percentile(list(latency_samples), 99)

        # --- Auto-Scaling Logic ---
        # Scale up logic
        current_load_factor = (current_request_rate_rps / INSTANCE_CAPACITY_RPS) / service_instances if service_instances > 0 else 1.0
        
        if current_time_seconds - last_scaling_action_time >= AUTOSCALING_COOLDOWN_SECONDS:
            if (p99_latency_for_autoscaling > AUTO_SCALE_UP_LATENCY_THRESHOLD or current_load_factor > AUTO_SCALE_UP_LOAD_FACTOR_THRESHOLD) \
               and service_instances < max_instances_param:
                service_instances = min(max_instances_param, service_instances + AUTO_SCALE_UP_STEP)
                last_scaling_action_time = current_time_seconds
                print(f"Autoscaling: Scaled up to {service_instances} instances at {current_time_seconds/3600:.1f} hours due to high latency/load.")
            # Scale down logic (only if not scaling up and below threshold)
            elif p99_latency_for_autoscaling < AUTO_SCALE_DOWN_LATENCY_THRESHOLD and service_instances > min_instances_param:
                service_instances = max(min_instances_param, service_instances - AUTO_SCALE_DOWN_STEP)
                last_scaling_action_time = current_time_seconds
                print(f"Autoscaling: Scaled down to {service_instances} instances at {current_time_seconds/3600:.1f} hours due to low latency.")

        # Cost calculation
        cumulative_cost += (service_instances * COST_PER_INSTANCE_PER_HOUR) * (TIME_STEP_SECONDS / 3600)

        # SLO & Error Budget Calculation (hourly for better granularity, but logged per step)
        hourly_latency_samples.extend(latencies_in_step)
        hourly_error_counts.append(erred_req_in_step)
        hourly_request_counts.append(num_requests_in_step)

        # Only evaluate hourly if enough data for a full hour, or at the end of simulation
        if current_time_seconds % 3600 == 0 or step == num_steps - 1:
            total_hourly_requests = sum(hourly_request_counts)
            total_hourly_errors = sum(hourly_error_counts)
            
            # Update error budget
            if total_hourly_requests > 0:
                error_budget_burn_rate = update_error_budget_local(total_hourly_errors, total_hourly_requests, error_budget_burn_rate, game_day_active)
                error_budget_remaining -= error_budget_burn_rate * (TIME_STEP_SECONDS / ERROR_BUDGET_WINDOW_SECONDS) # Burn proportional to time step
                error_budget_remaining = max(0.0, error_budget_remaining) # Ensure it doesn't go below 0

            # Update toil
            latency_breach, availability_breach = calculate_slo_breach_local(hourly_latency_samples, total_hourly_errors)
            toil_level = update_toil_local(latency_breach, availability_breach, error_budget_burn_rate, game_day_active)

            # Clear hourly metrics after processing
            hourly_latency_samples.clear()
            hourly_error_counts.clear()
            hourly_request_counts.clear()

        # Update history for plotting
        time_history.append(current_time_seconds / 3600) # In hours
        request_rate_history.append(current_request_rate_rps)
        latency_p99_history.append(calculate_p_percentile(list(latency_samples), 99))
        
        current_error_rate = erred_req_in_step / num_requests_in_step if num_requests_in_step > 0 else 0
        error_rate_history.append(current_error_rate)
        instances_history.append(service_instances)
        error_budget_remaining_history.append(error_budget_remaining * 100) # Store as percentage
        toil_level_history.append(toil_level * 100) # Store as percentage
        cumulative_cost_history.append(cumulative_cost)

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
'''

with open(file_path, 'r') as f:
    content = f.read()

# Find the start and end indices of the old code block
start_index = content.find(old_code_block_start_marker)
# Find the return statement that marks the end of the old block within run_simulation
# We need to be careful to find the *first* return statement after the start marker
end_index = content.find(old_code_block_end_marker, start_index)

# Adjust end_index to include the entire return statement block
if end_index != -1:
    # Find the end of the return dictionary, which is the end of the function logic
    brace_count = 0
    for i in range(end_index, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
        
        if brace_count == 0 and content[i] == '}':
            # Found the closing brace for the return dictionary
            end_index = i + 1  # Include the closing brace
            break

if start_index != -1 and end_index != -1:
    # Extract the portion of the file before and after the old code block
    before_block = content[:start_index]
    after_block = content[end_index:]

    # Construct the new content
    modified_content = before_block + new_code_block + after_block

    # Write the modified content back to the file
    with open(file_path, 'w') as f:
        f.write(modified_content)
    print(f"Successfully replaced the simulation logic in {file_path}")
else:
    print("Error: Could not find the old code block markers in the file.")


