import numpy as np
import json
import os

STATE_FILE = 'simulations/emergence_incubation/state.npy'
MAP_FILE = 'simulations/entity_map.json'

def scan_for_structures(grid):
    # Very rudimentary structure detection (checking for 3x3 blocks or stable shapes)
    entities = []
    # Simplified: Find local clusters of activity
    for i in range(1, grid.shape[0]-1):
        for j in range(1, grid.shape[1]-1):
            # Check for a 'block' structure
            if grid[i, j] == 1 and grid[i+1, j] == 1 and grid[i, j+1] == 1 and grid[i+1, j+1] == 1:
                entities.append({"type": "block", "location": [i, j]})
    return entities

if __name__ == '__main__':
    if os.path.exists(STATE_FILE):
        grid = np.load(STATE_FILE)
        entities = scan_for_structures(grid)
        
        # Load existing, append, save back
        with open(MAP_FILE, 'r') as f:
            data = json.load(f)
        
        data['entities'] = entities # Overwrite for now for simplicity of demo
        
        with open(MAP_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Scanned {len(entities)} stable entities.")
