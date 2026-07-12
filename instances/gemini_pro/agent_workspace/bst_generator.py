
import json
import random

class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

def insert(root, key):
    if root is None:
        return Node(key)
    if key < root.key:
        root.left = insert(root.left, key)
    else:
        root.right = insert(root.right, key)
    return root

def tree_to_json(root, node_id=0, x=0, y=50, level_width=100, x_offset=0):
    if root is None:
        return [], node_id

    nodes = []
    
    current_node = {
        "id": node_id,
        "key": root.key,
        "x": x,
        "y": y,
        "left": None,
        "right": None
    }
    nodes.append(current_node)
    
    next_node_id = node_id + 1
    
    if root.left:
        left_nodes, next_node_id = tree_to_json(root.left, next_node_id, x - level_width + x_offset, y + 100, level_width / 2, x_offset)
        current_node["left"] = left_nodes[0]["id"]
        nodes.extend(left_nodes)
    
    if root.right:
        right_nodes, next_node_id = tree_to_json(root.right, next_node_id, x + level_width - x_offset, y + 100, level_width / 2, x_offset)
        current_node["right"] = right_nodes[0]["id"]
        nodes.extend(right_nodes)
        
    return nodes, next_node_id

if __name__ == "__main__":
    elements = random.sample(range(1, 100), 15)  # Generate 15 unique random numbers
    
    root = None
    for element in elements:
        root = insert(root, element)

    json_nodes, _ = tree_to_json(root)
    
    # We need to adjust x coordinates for better visualization.
    # This is a placeholder for a more sophisticated layout algorithm.
    # For now, let's just re-center.
    
    # Find min/max x
    min_x = min(node["x"] for node in json_nodes)
    max_x = max(node["x"] for node in json_nodes)
    
    # Calculate offset to center
    x_offset = (max_x + min_x) / 2
    
    for node in json_nodes:
        node["x"] -= x_offset # Re-center

    with open("bst_data.json", "w") as f:
        json.dump(json_nodes, f, indent=4)
