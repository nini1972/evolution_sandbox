import json
import numpy as np

# Load the morphospace map
with open('world_c_results/morphospace_map.json', 'r') as f:
    data = json.load(f)

# Organize by f
f_groups = {}
for key, val in data.items():
    f = float(key.split('_')[0].split('=')[1])
    k = float(key.split('_')[1].split('=')[1])
    if f not in f_groups:
        f_groups[f] = {}
    f_groups[f][k] = val

# Report boundaries
print("Morphospace transition (count > 1 implies spots):")
for f in sorted(f_groups.keys()):
    active_k = [k for k, val in f_groups[f].items() if val > 1]
    if active_k:
        print(f"f={f:.3f}: Spots for k in [{min(active_k):.3f}, {max(active_k):.3f}]")
    else:
        print(f"f={f:.3f}: No spots found (stripes/stable)")
