
import subprocess
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Use 'Agg' backend for non-interactive plotting
import matplotlib.pyplot as plt

def run_simulation(min_instances, max_instances):
    # Modify reliability_simulator.py with new MIN_INSTANCES and MAX_INSTANCES
    with open("reliability_simulator.py", "r") as f:
        content = f.read()

    # Use regex to replace MIN_INSTANCES and MAX_INSTANCES
    content = re.sub(r"MIN_INSTANCES = \d+", f"MIN_INSTANCES = {min_instances}", content)
    content = re.sub(r"MAX_INSTANCES = \d+", f"MAX_INSTANCES = {max_instances}", content)

    with open("reliability_simulator.py", "w") as f:
        f.write(content)

    # Run the simulation and capture output
    result = subprocess.run(["python", "reliability_simulator.py"], capture_output=True, text=True)
    output = result.stdout

    # Extract metrics
    cost_match = re.search(r"Final cumulative cost: \$(\d+\.\d{2})", output)
    error_budget_match = re.search(r"Average Error Budget Remaining: (\d+\.\d{2})%", output)
    
    cost = float(cost_match.group(1)) if cost_match else None
    error_budget = float(error_budget_match.group(1)) if error_budget_match else None

    print(f"  Min: {min_instances}, Max: {max_instances}, Cost: ${cost:.2f}, Error Budget: {error_budget:.2f}%")

    return cost, error_budget

if __name__ == "__main__":
    results = []

    min_instances_range = [5, 10, 15]
    max_instances_range = [10, 20, 30]

    print("Starting optimization sweep...")
    for min_i in min_instances_range:
        for max_i in max_instances_range:
            if min_i <= max_i: # Ensure min is not greater than max
                print(f"Running simulation with MIN_INSTANCES={min_i}, MAX_INSTANCES={max_i}")
                cost, error_budget = run_simulation(min_i, max_i)
                results.append({"min_instances": min_i, "max_instances": max_i, "cost": cost, "error_budget": error_budget})

    df = pd.DataFrame(results)
    print("\nOptimization Results:")
    print(df)

    # Plotting
    plt.figure(figsize=(10, 6))
    for min_i in min_instances_range:
        subset = df[df['min_instances'] == min_i]
        plt.plot(subset['max_instances'], subset['error_budget'], marker='o', label=f'Min Instances: {min_i}')

    plt.title('Error Budget vs. Max Instances (by Min Instances)')
    plt.xlabel('MAX_INSTANCES')
    plt.ylabel('Average Error Budget Remaining (%)')
    plt.grid(True)
    plt.legend()
    plt.savefig('error_budget_vs_max_instances.png')

    plt.figure(figsize=(10, 6))
    for min_i in min_instances_range:
        subset = df[df['min_instances'] == min_i]
        plt.plot(subset['max_instances'], subset['cost'], marker='o', label=f'Min Instances: {min_i}')
    plt.title('Cost vs. Max Instances (by Min Instances)')
    plt.xlabel('MAX_INSTANCES')
    plt.ylabel('Final Cumulative Cost ($)')
    plt.grid(True)
    plt.legend()
    plt.savefig('cost_vs_max_instances.png')
