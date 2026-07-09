import matplotlib.pyplot as plt
import re

log_file = 'simulations/emergence_incubation/evolution_history.log'
entropies = []
entity_counts = []

with open(log_file, 'r') as f:
    for line in f:
        # Expected line: "Thu Jul  9 03:15:02 UTC 2026: Entropy 126, Entities 3" 
        # (Parsing based on the format in main_cycle_v3)
        match = re.search(r'Entropy (\d+), Entities (\d+)', line)
        if match:
            entropies.append(int(match.group(1)))
            entity_counts.append(int(match.group(2)))

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(entropies)
plt.title('System Entropy')
plt.subplot(1, 2, 2)
plt.plot(entity_counts)
plt.title('Entity Count')
plt.savefig('documentation/complexity_map/graph.png')
print('Chart saved to documentation/complexity_map/graph.png')
