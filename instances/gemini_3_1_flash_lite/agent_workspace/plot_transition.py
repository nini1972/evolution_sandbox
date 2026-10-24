import json
import matplotlib.pyplot as plt
import numpy as np

# Load the metrics
with open('world_c_results/world_c_job_gemini_3_1_flash_lite_1792723700_4caa_transition_scaling_metrics.json', 'r') as f:
    data = json.load(f)

# Sort by radius and access keys correctly
radii = sorted([float(r) for r in data.keys()])
# Map float radii back to original string format used in JSON keys
activity = [data[f'{r:.1f}' if r != 13.0 and r != 14.0 and r != 15.0 and r != 16.0 and r != 10.0 and r != 11.0 and r != 12.0 else str(int(r)) if r in [10, 11, 12, 13, 14, 15, 16] else f'{r}'] for r in radii]

# Simpler fix:
activity = []
for r in radii:
    # Try the string conversion as it exists in JSON
    # If it's an integer, it's '10', if it's float like 13.5, it's '13.5'
    key = str(r) if r % 1 != 0 else str(int(r))
    activity.append(data[key])


# Plotting
plt.figure(figsize=(10, 6))
plt.plot(radii, activity, marker='o', linestyle='-', color='b')
plt.title('Lenia2D Activity vs. Kernel Radius (R)')
plt.xlabel('Kernel Radius (R)')
plt.ylabel('Normalized Activity Metric')
plt.grid(True)
plt.savefig('scaling_transition.png')
