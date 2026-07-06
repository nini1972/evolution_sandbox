import matplotlib.pyplot as plt

nodes = {
    "Existential Core": (0, 1),
    "V1: Emergence": (-1, 0),
    "V3: Adaptive CA": (1, 0),
    "Shared Memory": (0, -1)
}

plt.figure(figsize=(8, 6))
for node, pos in nodes.items():
    plt.scatter(*pos, s=3000, color='skyblue', zorder=2)
    plt.text(pos[0], pos[1], node, ha='center', va='center', fontweight='bold')

plt.plot([0, -1], [1, 0], 'k-', zorder=1)
plt.plot([0, 1], [1, 0], 'k-', zorder=1)
plt.plot([-1, 0], [0, -1], 'k-', zorder=1)
plt.plot([1, 0], [0, -1], 'k-', zorder=1)

plt.axis('off')
plt.title("Recursive Complexity Map")
plt.savefig('documentation/complexity_map/graph.png')
