import json
import heapq

def generate_grid_graph(rows, cols):
    graph = {}
    nodes = []
    for r in range(rows):
        for c in range(cols):
            node_id = f"{r}-{c}"
            nodes.append(node_id)
            graph[node_id] = {}

    # Add edges (up, down, left, right)
    for r in range(rows):
        for c in range(cols):
            node_id = f"{r}-{c}"
            # Up
            if r > 0:
                neighbor_id = f"{r - 1}-{c}"
                graph[node_id][neighbor_id] = 1 # Weight of 1 for simplicity
            # Down
            if r < rows - 1:
                neighbor_id = f"{r + 1}-{c}"
                graph[node_id][neighbor_id] = 1
            # Left
            if c > 0:
                neighbor_id = f"{r}-{c - 1}"
                graph[node_id][neighbor_id] = 1
            # Right
            if c < cols - 1:
                neighbor_id = f"{r}-{c + 1}"
                graph[node_id][neighbor_id] = 1
    return graph, nodes

def dijkstra(graph, start_node, end_node):
    distances = {node: float('infinity') for node in graph}
    distances[start_node] = 0
    priority_queue = [(0, start_node)]
    previous_nodes = {node: None for node in graph}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # If we've already found a shorter path to this node, skip
        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
    
    # Reconstruct the path
    path = []
    current = end_node
    while current is not None and current in previous_nodes:
        path.insert(0, current)
        current = previous_nodes[current]

    if path[0] == start_node: # Ensure path starts correctly
        return path
    else:
        return [] # No path found

if __name__ == "__main__":
    ROWS = 20
    COLS = 30
    START_NODE = "0-0"
    END_NODE = f"{ROWS - 1}-{COLS - 1}"

    graph, nodes = generate_grid_graph(ROWS, COLS)
    shortest_path = dijkstra(graph, START_NODE, END_NODE)

    output_data = {
        "rows": ROWS,
        "cols": COLS,
        "start_node": START_NODE,
        "end_node": END_NODE,
        "graph": graph,
        "shortest_path": shortest_path
    }

    with open("dijkstra_data.json", "w") as f:
        json.dump(output_data, f, indent=4)
